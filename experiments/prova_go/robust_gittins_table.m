function T = robust_gittins_table(k, beta, H, np, N, ng)
%ROBUST_GITTINS_TABLE  Robust Gittins index of a Bernoulli cost arm (Cohen & Treetanthiploet 2022).
%   T = ROBUST_GITTINS_TABLE(k, beta, H, np, N, ng) implements the algorithm of
%   Section 5 / Appendix D of S. N. Cohen and T. Treetanthiploet, "Gittins'
%   theorem under uncertainty", Electron. J. Probab. 27 (2022), paper 17:
%     costs h(t) in {0,1}, P(h = 1) = theta unknown, state (p, n), h = 2 after the
%     horizon (so the player stops), discount beta;
%     one-step nonlinear expectation E(f) = max over theta in {p-, p+} of
%       theta f(1) + (1 - theta) f(0),  p+- = Beta^-1_(p n, (1-p) n)(0.5 +- k/2)
%     (sup of a linear function of theta over [p-, p+]: an endpoint; p n or
%     (1-p) n equal to 0 replaced by 1e-6);
%     for every gamma of a grid G in [0,1]: V_H = 0,
%       V_t(p, n+t) = min{0, E_t[(h - gamma) + beta V_{t+1}(p_{t+1}, n+t+1)]},
%       p_{t+1} = (p (n+t) + h)/(n+t+1), linear interpolation in p,
%       U(gamma, p, n) = E_0[(h - gamma) + beta V_1(p_1, n+1)]  (first play forced),
%     index gamma(p, n) = min{gamma in G : U <= 0}, refined linearly between the
%     two grid values that bracket U = 0.
%   Vectorised over gamma (ng values) and p (np values on [0,1]); n = 1..N.
%   T.gam(ip, in) is the index at p = T.p(ip), n = T.n(in); lookup: GITTINS_LOOKUP.
%   Defaults: np = 101, N = 80, ng = 401. N may also be a vector of the counts n
%   wanted (T.n = N), e.g. for the check of gamma -> p as n grows.
    if nargin < 4 || isempty(np), np = 101; end
    if nargin < 5 || isempty(N), N = 80; end
    if isscalar(N), nlist = 1:N; else, nlist = N(:)'; end
    if nargin < 6 || isempty(ng), ng = 401; end
    p = linspace(0, 1, np); G = linspace(0, 1, ng)'; ep = 1e-6;
    qlo = 0.5 - k / 2; qhi = 0.5 + k / 2;
    cmax = max(nlist) + H;
    PL = zeros(cmax, np); PH = zeros(cmax, np);
    IU = zeros(cmax, np); WU = zeros(cmax, np); ID = zeros(cmax, np); WD = zeros(cmax, np);
    need = false(cmax, 1); for n = nlist, need(n:n + H - 1) = true; end
    for c = find(need)'
        a = max(p * c, ep); b = max((1 - p) * c, ep);
        PL(c, :) = beta_q(qlo, a, b); PH(c, :) = beta_q(qhi, a, b);
        [IU(c, :), WU(c, :)] = lin_w((p * c + 1) / (c + 1), np);
        [ID(c, :), WD(c, :)] = lin_w((p * c) / (c + 1), np);
    end
    gam = zeros(np, numel(nlist));
    for in = 1:numel(nlist)
        n = nlist(in);
        V = zeros(ng, np);                                  % V_H
        for t = H-1:-1:0
            c = n + t;
            Vu = V(:, IU(c, :)) .* WU(c, :) + V(:, IU(c, :) + 1) .* (1 - WU(c, :));
            Vd = V(:, ID(c, :)) .* WD(c, :) + V(:, ID(c, :) + 1) .* (1 - WD(c, :));
            f1 = (1 - G) + beta * Vu; f0 = (0 - G) + beta * Vd;
            E = max(PL(c, :) .* f1 + (1 - PL(c, :)) .* f0, PH(c, :) .* f1 + (1 - PH(c, :)) .* f0);
            if t > 0, V = min(0, E); else, U = E; end
        end
        for ip = 1:np                                       % U decreases in gamma
            j = find(U(:, ip) <= 0, 1);
            if isempty(j), gam(ip, in) = 1;
            elseif j == 1, gam(ip, in) = G(1);
            else
                u0 = U(j - 1, ip); u1 = U(j, ip);
                gam(ip, in) = G(j - 1) + (G(j) - G(j - 1)) * u0 / (u0 - u1);
            end
        end
    end
    T = struct('k', k, 'beta', beta, 'H', H, 'p', p, 'n', nlist, 'gam', gam, 'ng', ng);
end
function q = beta_q(prob, a, b)
% Quantile of Beta(a, b) by bisection on betainc (identical in MATLAB and Octave;
% robust for the tiny shape parameters of the edge states).
    if prob <= 0, q = zeros(size(a)); return; end
    if prob >= 1, q = ones(size(a)); return; end
    lo = zeros(size(a)); hi = ones(size(a));
    for it = 1:42
        x = 0.5 * (lo + hi); up = betainc(x, a, b) < prob;
        lo(up) = x(up); hi(~up) = x(~up);
    end
    q = 0.5 * (lo + hi);
end
function [i, w] = lin_w(x, np)
    s = x * (np - 1); i = floor(s) + 1; i = min(max(i, 1), np - 1);
    w = 1 - (s - (i - 1));                                  % weight of node i
end
