function o = fkcl_model_run(m, p)
%FKCL_MODEL_RUN  Heads, interface depth and screen-averaged chloride for one parameter set.
%
%   o = FKCL_MODEL_RUN(m, p) with p a struct with fields theta (Nz x 1 zone log-K
%   multipliers), R [m/d], eta, b_c, b_e [m], L_B [km], ground [m], w [m], Cl_s [mg/L].
%
%   Physics (steady, confined, Dupuit, sharp interface with a dispersive transition zone):
%     div(K grad phi) + R = 0,  phi = 0 at the shoreline       Strack (1976) potential [m^2]
%     zone 2 (phi < delta B^2/2):  zeta = d + sqrt(2 phi/delta),  h = delta d + sqrt(2 delta phi)
%     zone 1:                      h = phi/B + delta (d + B/2),   zeta = h/delta
%     c(z) = Phi((z - zeta)/w);  Cl = Cl_f + cbar (Cl_s - Cl_f), cbar = screen mean of c
%   Screens: upper ('sh', top 40 m of the aquifer), middle ('mid', 40 m at mid-thickness),
%   base ('dp', bottom 40 m). Depths are below sea level, positive down.

    C = m.C;
    K = p.eta * m.Kidw .* exp(p.theta(m.zone));
    phi = fkcl_solve_phi(m, K, p.R);
    d = max(m.cover - p.ground, 1.0);
    B = p.b_e + (p.b_c - p.b_e) * min(max(1 - m.dist / p.L_B, 0), 1);
    phit = 0.5 * C.delta * B.^2;
    z2 = phi < phit;
    ph = max(phi, 0);
    h1 = phi ./ B + C.delta * (d + 0.5 * B);
    h = h1; zeta = h1 / C.delta;
    h(z2) = C.delta * d(z2) + sqrt(2 * C.delta * ph(z2));
    zeta(z2) = d(z2) + sqrt(2 * ph(z2) / C.delta);
    L = min(C.screen, B);
    zm = d + 0.5 * B;
    f_sh = screen_average(d, d + L, zeta, p.w);
    f_mid = screen_average(zm - 0.5 * L, zm + 0.5 * L, zeta, p.w);
    f_dp = screen_average(d + B - L, d + B, zeta, p.w);
    o.phi = phi; o.h = h; o.zeta = zeta; o.d = d; o.B = B;
    o.f_sh = f_sh; o.f_mid = f_mid; o.f_dp = f_dp;
    o.Cl_sh = C.Cl_f + f_sh * (p.Cl_s - C.Cl_f);
    o.Cl_mid = C.Cl_f + f_mid * (p.Cl_s - C.Cl_f);
    o.Cl_dp = C.Cl_f + f_dp * (p.Cl_s - C.Cl_f);
    o.wedge = zeta < d + B;
end

function c = screen_average(z1, z2, zeta, w)
% mean of Phi((z - zeta)/w) over z in [z1, z2]:  (w/L) [G((z2-zeta)/w) - G((z1-zeta)/w)],
% G(u) = u Phi(u) + phi(u) is the antiderivative of the standard normal CDF
    G = @(u) u .* (0.5 * erfc(-u / sqrt(2))) + exp(-0.5 * u.^2) / sqrt(2 * pi);
    Lz = max(z2 - z1, 1e-9);
    c = w ./ Lz .* (G((z2 - zeta) / w) - G((z1 - zeta) / w));
end
