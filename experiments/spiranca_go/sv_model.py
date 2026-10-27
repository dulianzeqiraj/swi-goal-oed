"""SPIRANCA-GO on the variable-density section of the assembled-system note (experiments/montimi_go).

The section is the goal-guided assembly of MONTIMI-GO: variable-density flow with buoyancy, salt with two immobile
zones, solved monolithically on the goal-graded mesh (39 columns x 20 layers), half-year steps. Here it runs season by
season with three additions, none of which changes the equations:
  - the regional fresh inflow at the inland face is scaled every season by the recharge of that season;
  - a hidden private abstraction, spread over the top 20 m between 0.8 and 2.2 km from the coast, is added to the sinks;
  - the supply well is pumped at a different rate every season.
The interface now has memory (immobile zones, advection over years) and the heads are nonlinear in the sources
(buoyancy). Seasons (half-years), as in the areal test but with persistence:
  r      rainfall anomaly at the gauge, AR(1) with lag-one correlation 0.7 (multi-year droughts), recorded
  u      operator's pumping anomaly of the supply well, 0.25 U(-1, 1) - 0.08 r, recorded
  R      inflow factor 1 + 0.2 r + 0.06 e_R (e_R unrecorded)
  H      private abstraction Hbar (1 - 0.25 r + 0.15 e_H) (e_H unrecorded)
Both the utility pumping and the private abstraction ramp up linearly over the first 10 years of the 80-year record
(development), which gives the record the slow variation that memory needs.
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
MG = os.path.join(HERE, '..', 'montimi_go')
sys.path.insert(0, MG)
import mg_model as M      # noqa: E402
import mg_setup as S      # noqa: E402

DT_YR = 0.5
N_REC = 160                       # 80-year record (half-year seasons)
N_FUT = 60                        # 30-year future
RAMP = 20                         # development ramp: 10 years
XS = S.snap(2000.0)               # the supply well
HFRAC = 0.4                       # private abstraction, fraction of the utility's mean pumping
OPTS = dict(memory_h=(False, False), slr=False)   # the goal-guided assembly of MONTIMI-GO
PIEZO_X = [500.0, 1000.0, 1500.0, 2500.0, 3000.0, 3500.0]   # candidate piezometers (mid-depth)
PIEZO_Z = [-40.0]
PH = 0.7                          # lag-one correlation of the rainfall anomaly
HEAD_SD = 0.01                    # m, head noise of a piezometer


def grid_G():
    d = json.load(open(os.path.join(MG, 'res', 'grid_G.json')))
    return M.Grid(d['xf'], d['zf'])


class SeasonModel(M.Model):
    """MONTIMI-GO model with a seasonal inflow factor and a hidden private abstraction (layout key 'H')."""

    def private_sink(self):
        if not hasattr(self, '_eP'):
            g = self.g
            e = np.zeros(g.N)
            rows = [i for i in range(g.NZ) if -30.0 < g.zc[i] < -10.0]
            cols = [j for j in range(g.NX) if 800.0 <= g.xc[j] <= 2200.0]
            for i in rows:
                for j in cols:
                    e[i * g.NX + j] = g.dz[i] * (g.xf[j + 1] - g.xf[j])
            self._eP = e / e.sum()
        return self._eP

    def wells_of(self, layout):
        Wo, Wi, eQ, eqr, wJ = super().wells_of(layout)
        if layout.get('H'):
            Wo = Wo + layout['H'] * self.private_sink()
        return Wo, Wi, eQ, eqr, wJ

    def seasons(self, t0, fac):
        self.t_s0, self.fac = t0, np.asarray(fac, float)

    def g0(self, t, slr=None, scale=1.0):
        g0 = super().g0(t, slr, scale)
        if getattr(self, 'fac', None) is not None:
            n = int(round((t - self.t_s0) / self.dt))
            g0[self.inl] *= self.fac[min(max(n, 0), len(self.fac) - 1)]
        return g0


def drivers(rng, n, r0=0.0, decision=None, du=0.0, h_extra=0.0, ramp=None):
    """recorded anchors (r, u) and the unrecorded sources of n seasons. du: unrecorded warming (in r units)."""
    r = np.empty(n); prev = r0
    for k in range(n):
        prev = PH * prev + np.sqrt(1 - PH ** 2) * rng.standard_normal(); r[k] = prev
    u = 0.25 * rng.uniform(-1, 1, n) - 0.08 * r if decision is None else np.full(n, decision)
    eR, eH = rng.standard_normal(n), rng.standard_normal(n)
    ramp = np.ones(n) if ramp is None else ramp
    fac = 1.0 + 0.2 * r + 0.06 * eR - 0.2 * du
    hfac = (1.0 - 0.25 * r + 0.15 * eH) + 0.25 * du + h_extra
    return r, u, np.maximum(fac, 0.2), np.maximum(hfac, 0.0) * ramp, ramp


def simulate(g, P, y0, z0, t0, Qbar, r, u, fac, hfac, ramp):
    """runs the seasons; returns screen sea fraction and the heads at the piezometers per season, and the end state."""
    m = SeasonModel(g, P=P, opts=OPTS, dt_yr=DT_YR)
    n = len(r)
    m.seasons(t0, np.r_[fac[0], fac])
    sched = [(1, dict(xs=XS, Q=float(Qbar * ramp[k] * (1 + u[k])), H=float(HFRAC * Qbar * hfac[k]))) for k in range(n)]
    m.run(y0=y0, z0=z0, schedule=sched, t0=t0, keep=True, toe=False)
    cells = [g.column(x) + g.NX * int(np.argmin(np.abs(g.zc - z))) for x in PIEZO_X for z in PIEZO_Z]
    H = np.array([yk[cells] for yk in m.Y[1:]])
    J = np.array(m.Jt[1:])
    return J, H, m.y_end, m.z_end
