"""Function-space diffusion prior for the RINDERTIMI-GO test bed (JAX, CPU).

Following FunDPS (Yao et al., NeurIPS 2025): the noising process adds Gaussian-random-field noise a_sigma = a + sigma*eta
with eta ~ N(0, C) (Algorithm 1 there); the denoiser D_theta(a_sigma, sigma) is a neural operator trained with the EDM
loss (Karras et al., 2022); the score is (D - a_sigma)/sigma^2. Here the operator is a Fourier neural operator (Li et al.,
2020) on the (x, t) grid with noise-level conditioning. The four boundary channels (eta, qL, r, f) are functions of time
only: their noise is a GRF in t broadcast along x, and the denoiser output for them is averaged along x, so samples stay in
that function space.

usage: python rgo_net.py [steps]   (writes res/rgo_params.npz and res/rgo_norm.json)"""
import json
import os
import sys
import time

import numpy as np
import jax
import jax.numpy as jnp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rgo_model as M  # noqa: E402

RES = os.path.join(HERE, 'res')
C_W, N_BLOCK, MX, MT = 32, 4, 8, 12          # width, blocks, retained Fourier modes in x and t
N_FREQ, EMB = 16, 64
ELL_X, ELL_T = 0.05, 0.05                    # GRF noise length scales on the unit domain (FunDPS rbf_scale 0.05)
SIG_DATA = 1.0
P_MEAN, P_STD = -1.2, 1.2                    # EDM log-normal noise-level distribution
N_TRAIN = 24000


# ------------------------------------------------------------------------------------------------ data and normalisation
def make_data(n, seed):
    rng = np.random.default_rng(seed)
    out = dict(h=[], eta=[], qL=[], r=[], f=[])
    for start in range(0, n, 2000):
        a, _ = M.sample_prior(rng, min(2000, n - start))
        out['h'].append(a[:, 0]); out['eta'].append(a[:, 1, 0]); out['qL'].append(a[:, 2, 0])
        out['r'].append(a[:, 3, 0]); out['f'].append(a[:, 4, 0])
    return {k: np.concatenate(v).astype(np.float32) for k, v in out.items()}


def norm_stats(D):
    st = dict(h_mean=D['h'].mean(axis=(0, 2)).tolist(), h_sd=float(D['h'].std(axis=(0, 2)).mean()))
    for k in ('eta', 'qL', 'r', 'f'):
        st[k + '_mean'] = float(D[k].mean()); st[k + '_sd'] = float(D[k].std())
    return st


def to_field(D, st):
    """(B, NX, NT, 5) normalised joint function."""
    hm = np.asarray(st['h_mean'], np.float32)[None, :, None]
    h = (D['h'] - hm) / st['h_sd']
    tch = [(D[k] - st[k + '_mean']) / st[k + '_sd'] for k in ('eta', 'qL', 'r', 'f')]
    B = h.shape[0]
    a = np.empty((B, M.NX, M.NT, 5), np.float32)
    a[..., 0] = h
    for c, v in enumerate(tch, start=1):
        a[..., c] = v[:, None, :]
    return a


def from_field(a, st):
    a = np.asarray(a)
    hm = np.asarray(st['h_mean'])[None, :, None]
    out = dict(h=a[..., 0] * st['h_sd'] + hm)
    for c, k in enumerate(('eta', 'qL', 'r', 'f'), start=1):
        out[k] = a[..., c].mean(1) * st[k + '_sd'] + st[k + '_mean']
    return out


# ------------------------------------------------------------------------------------------------ GRF noise
def grf_filters():
    """amplitude filters in Fourier space for a squared-exponential covariance with length ELL on the unit domain."""
    kx = np.fft.fftfreq(M.NX, d=1.0 / M.NX)          # integer wavenumbers
    kt = np.fft.rfftfreq(M.NT, d=1.0 / M.NT)
    fx = np.exp(-0.25 * (2 * np.pi * kx * ELL_X) ** 2)
    ft = np.exp(-0.25 * (2 * np.pi * kt * ELL_T) ** 2)
    f2 = fx[:, None] * ft[None, :]
    # unit marginal variance
    s2 = np.sqrt((np.abs(np.fft.irfft2(f2, s=(M.NX, M.NT))) ** 2).sum() * M.NX * M.NT)
    ft1 = ft
    s1 = np.sqrt((np.abs(np.fft.irfft(ft1, n=M.NT)) ** 2).sum() * M.NT)
    return jnp.asarray(f2 / s2 * np.sqrt(M.NX * M.NT), jnp.complex64), jnp.asarray(ft1 / s1 * np.sqrt(M.NT), jnp.complex64)


F2, F1 = grf_filters()


def grf_noise(key, B):
    """(B, NX, NT, 5): channel 0 a 2-D GRF in (x, t); channels 1-4 1-D GRFs in t broadcast along x."""
    k1, k2 = jax.random.split(key)
    w2 = jax.random.normal(k1, (B, M.NX, M.NT))
    n2 = jnp.fft.irfft2(jnp.fft.rfft2(w2, axes=(1, 2)) * F2[None], s=(M.NX, M.NT), axes=(1, 2))
    w1 = jax.random.normal(k2, (B, 4, M.NT))
    n1 = jnp.fft.irfft(jnp.fft.rfft(w1, axis=-1) * F1[None, None], n=M.NT, axis=-1)
    n1 = jnp.broadcast_to(jnp.moveaxis(n1, 1, -1)[:, None, :, :], (B, M.NX, M.NT, 4))
    return jnp.concatenate([n2[..., None], n1], axis=-1)


# ------------------------------------------------------------------------------------------------ network
def init_params(key):
    ks = iter(jax.random.split(key, 64))
    cin = 5 + 2

    def dense(i, o, scale=None):
        s = scale if scale is not None else np.sqrt(2.0 / i)
        return dict(w=jax.random.normal(next(ks), (i, o)) * s, b=jnp.zeros(o))
    p = dict(lift=dense(cin, C_W), emb1=dense(2 * N_FREQ, EMB), emb2=dense(EMB, N_BLOCK * C_W, scale=0.02),
             proj1=dense(C_W, 64), proj2=dense(64, 5, scale=0.01), blocks=[])
    sc = 1.0 / (C_W * C_W)
    for _ in range(N_BLOCK):
        p['blocks'].append(dict(
            wr1=sc * jax.random.uniform(next(ks), (C_W, C_W, MX, MT)), wi1=sc * jax.random.uniform(next(ks), (C_W, C_W, MX, MT)),
            wr2=sc * jax.random.uniform(next(ks), (C_W, C_W, MX, MT)), wi2=sc * jax.random.uniform(next(ks), (C_W, C_W, MX, MT)),
            pw=dense(C_W, C_W)))
    return p


GRID = jnp.stack(jnp.meshgrid(jnp.linspace(0, 1, M.NX), jnp.linspace(0, 1, M.NT), indexing='ij'), -1)


def spectral(x, blk):
    xf = jnp.fft.rfft2(x, axes=(1, 2))
    w1 = blk['wr1'] + 1j * blk['wi1']; w2 = blk['wr2'] + 1j * blk['wi2']
    o1 = jnp.einsum('bxtc,cdxt->bxtd', xf[:, :MX, :MT], w1)
    o2 = jnp.einsum('bxtc,cdxt->bxtd', xf[:, -MX:, :MT], w2)
    out = jnp.zeros(xf.shape[:3] + (C_W,), jnp.complex64)
    out = out.at[:, :MX, :MT].set(o1).at[:, -MX:, :MT].set(o2)
    return jnp.fft.irfft2(out, s=(M.NX, M.NT), axes=(1, 2))


def net(p, x, c_noise):
    """F_theta: x (B, NX, NT, 5), c_noise (B,) -> (B, NX, NT, 5)."""
    B = x.shape[0]
    g = jnp.broadcast_to(GRID[None], (B, M.NX, M.NT, 2))
    h = jnp.concatenate([x, g], -1) @ p['lift']['w'] + p['lift']['b']
    fr = jnp.exp(jnp.linspace(0.0, np.log(100.0), N_FREQ))
    ff = jnp.concatenate([jnp.sin(c_noise[:, None] * fr), jnp.cos(c_noise[:, None] * fr)], -1)
    e = jax.nn.silu(ff @ p['emb1']['w'] + p['emb1']['b']) @ p['emb2']['w'] + p['emb2']['b']
    e = e.reshape(B, N_BLOCK, C_W)
    for k, blk in enumerate(p['blocks']):
        y = spectral(h, blk) + h @ blk['pw']['w'] + blk['pw']['b'] + e[:, k][:, None, None, :]
        h = h + jax.nn.gelu(y)
    out = jax.nn.gelu(h @ p['proj1']['w'] + p['proj1']['b']) @ p['proj2']['w'] + p['proj2']['b']
    return out


def project(a):
    """boundary channels are functions of t only: replace them by their mean along x."""
    return jnp.concatenate([a[..., :1], jnp.broadcast_to(a[..., 1:].mean(1, keepdims=True), a[..., 1:].shape)], -1)


def denoise(p, a, sigma):
    """EDM-preconditioned denoiser D(a, sigma); sigma (B,)."""
    s = sigma[:, None, None, None]
    c_skip = SIG_DATA ** 2 / (s ** 2 + SIG_DATA ** 2)
    c_out = s * SIG_DATA / jnp.sqrt(s ** 2 + SIG_DATA ** 2)
    c_in = 1.0 / jnp.sqrt(s ** 2 + SIG_DATA ** 2)
    return project(c_skip * a + c_out * net(p, c_in * a, jnp.log(sigma) / 4.0))


def loss_fn(p, a, key):
    B = a.shape[0]
    k1, k2 = jax.random.split(key)
    sigma = jnp.exp(P_MEAN + P_STD * jax.random.normal(k1, (B,)))
    noisy = a + sigma[:, None, None, None] * grf_noise(k2, B)
    d = denoise(p, noisy, sigma)
    lam = (sigma ** 2 + SIG_DATA ** 2) / (sigma * SIG_DATA) ** 2
    return jnp.mean(lam[:, None, None, None] * (d - a) ** 2)


# ------------------------------------------------------------------------------------------------ Adam with warm-up and cosine decay
def adam_init(p):
    z = jax.tree_util.tree_map(jnp.zeros_like, p)
    return dict(m=z, v=jax.tree_util.tree_map(jnp.zeros_like, p), t=0)


@jax.jit
def train_step(p, opt_m, opt_v, t, ema, a, key, lr):
    l, g = jax.value_and_grad(loss_fn)(p, a, key)
    gn = jnp.sqrt(sum(jnp.sum(x ** 2) for x in jax.tree_util.tree_leaves(g)))
    g = jax.tree_util.tree_map(lambda x: x * jnp.minimum(1.0, 1.0 / (gn + 1e-12)), g)
    b1, b2 = 0.9, 0.999
    opt_m = jax.tree_util.tree_map(lambda m, x: b1 * m + (1 - b1) * x, opt_m, g)
    opt_v = jax.tree_util.tree_map(lambda v, x: b2 * v + (1 - b2) * x ** 2, opt_v, g)
    mh = jax.tree_util.tree_map(lambda m: m / (1 - b1 ** t), opt_m)
    vh = jax.tree_util.tree_map(lambda v: v / (1 - b2 ** t), opt_v)
    p = jax.tree_util.tree_map(lambda x, m, v: x - lr * m / (jnp.sqrt(v) + 1e-8), p, mh, vh)
    ema = jax.tree_util.tree_map(lambda e, x: 0.999 * e + 0.001 * x, ema, p)
    return p, opt_m, opt_v, ema, l


def save_params(p, path):
    leaves, tree = jax.tree_util.tree_flatten(p)
    np.savez(path, *[np.asarray(x) for x in leaves])


def load_params(path):
    p0 = init_params(jax.random.PRNGKey(0))
    leaves0, tree = jax.tree_util.tree_flatten(p0)
    z = np.load(path)
    leaves = [jnp.asarray(z[f'arr_{i}']) for i in range(len(leaves0))]
    return jax.tree_util.tree_unflatten(tree, leaves)


def main(steps=8000, batch=32, lr_max=2e-3):
    os.makedirs(RES, exist_ok=True)
    t0 = time.time()
    D = make_data(N_TRAIN, seed=11)
    st = norm_stats(D)
    A = to_field(D, st)
    with open(os.path.join(RES, 'rgo_norm.json'), 'w') as fh:
        json.dump(st, fh)
    print(f'data {A.shape} in {time.time() - t0:.0f}s', flush=True)
    p = init_params(jax.random.PRNGKey(1))
    nparam = sum(int(np.prod(x.shape)) for x in jax.tree_util.tree_leaves(p))
    print('parameters', nparam, flush=True)
    opt = adam_init(p); m, v = opt['m'], opt['v']
    ema = p
    key = jax.random.PRNGKey(2)
    rng = np.random.default_rng(3)
    hist = []
    t0 = time.time()
    for it in range(1, steps + 1):
        idx = rng.integers(0, A.shape[0], batch)
        key, sk = jax.random.split(key)
        lr = lr_max * min(1.0, it / 300) * 0.5 * (1 + np.cos(np.pi * it / steps)) + 1e-5
        p, m, v, ema, l = train_step(p, m, v, it, ema, jnp.asarray(A[idx]), sk, lr)
        hist.append(float(l))
        if it % 500 == 0 or it == 1:
            print(f'step {it} loss {np.mean(hist[-500:]):.4f} ({time.time() - t0:.0f}s)', flush=True)
    save_params(ema, os.path.join(RES, 'rgo_params.npz'))
    with open(os.path.join(RES, 'rgo_train_loss.json'), 'w') as fh:
        json.dump(dict(loss=hist[::10], steps=steps, batch=batch, nparam=nparam, seconds=time.time() - t0), fh)
    print('saved', flush=True)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
