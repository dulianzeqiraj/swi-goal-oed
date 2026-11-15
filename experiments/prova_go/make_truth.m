function tr = make_truth(M, S, seed, withData)
%MAKE_TRUTH  One synthetic Fushe-Kuqe truth (richer than every arm) and its data.
%   tr = MAKE_TRUTH(M, S, seed) draws, with rng(seed,'twister'), in this order:
%     theta_zone ~ N(0, GamF); zeta = L*randn(Nc,1) (sub-zonal field, ZETA_FACTOR);
%     xi_R ~ N(0, 0.3^2) (true recharge 5e-4*exp(xi_R)); xi_f ~ N(0, 0.08^2)
%     (future recharge factor 1 + xi_f); head noise (sd 0.05 m, J values);
%     Stage-0 noise (sd 0.01 m, 2J values); one random permutation of the 2J
%     validation items per arm (five independent streams); a seed for Thompson
%     sampling. The coastal low-K strip (log-multiplier -1 within 1.5 km of the
%     coast) is present when seed is even (half of the truths).
%   log K = log K0c + theta_zone(zone) + zeta + strip. True outputs from FK_FORWARD.
    if nargin < 4, withData = true; end
    rng(seed, 'twister');
    Lg = chol(M.GamF, 'lower'); thz = Lg * randn(M.Nz, 1);
    zeta = zeta_factor(M, S) * randn(M.Nc, 1);
    xiR = S.sigR * randn; xif = S.sigXi * randn;
    tr.seed = seed; tr.hasStrip = mod(seed, 2) == 0;
    tr.thz = thz; tr.xiR = xiR; tr.xif = xif;
    tr.u = thz(M.zone) + zeta + S.stripLog * tr.hasStrip * M.strip;
    tr.zeta = zeta; tr.Rch = M.R0 * exp(xiR);
    if ~withData, return; end
    J = M.J;
    tr.noiseH = S.sigH * randn(J, 1); tr.noiseV = S.sigV * randn(2 * J, 1);
    tr.perm = zeros(5, 2 * J); for m = 1:5, tr.perm(m, :) = randperm(2 * J); end
    tr.tsSeed = seed * 7 + 3;
    tr.f = fk_forward(M, S, tr.u, tr.Rch);
    tr.dH = tr.f(1:J) + tr.noiseH; tr.dV = tr.f(J+1:3*J) + tr.noiseV;
    H0 = tr.f(3*J+1:3*J+2); hn = tr.f(3*J+3:3*J+4);
    tr.Hfut0 = H0; tr.hnat = hn; tr.Hfut = H0 + xif * hn;          % realised future heads at A, B
    tr.riskTrue = 0.5 * erfc(-(max((S.hc - H0) ./ hn) / S.sigXi) / sqrt(2));   % P(A or B intruded) over xi_f
    tr.intrA = tr.Hfut(1) < S.hc; tr.intrB = tr.Hfut(2) < S.hc;
end
