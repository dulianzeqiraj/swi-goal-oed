function P = fkcl_prior(m, n, src)
%FKCL_PRIOR  Prior draws of the chloride model parameters.
%
%   P = FKCL_PRIOR(m, n, seed) draws n sets with this MATLAB session's generator:
%     theta  ~ N(0, Gamma_F(rho_F))  zone log-K multipliers (facies-conditional prior)
%     R      ~ 5e-4 exp(0.7 N(0,1))  m/d, net recharge
%     eta    ~ U(0.3, 0.8)           transmissive (gravel) fraction
%     b_c    ~ U(180, 200) m         thickness at the coast; b_e ~ U(5, 10) m at the inland margin
%     L_B    ~ U(12, 20) km          thinning distance
%     ground ~ U(0, 5) m             ground elevation subtracted from the DRASTIC depth
%     w      ~ 20 exp(0.6 N(0,1)) m  transition-zone half-width
%     Cl_s   ~ U(20500, 22000) mg/L  Adriatic chloride
%   P = FKCL_PRIOR(m, n, 'python') reads the n first draws of the Python run
%   (results/calib_prior_draws.csv), so that every number can be compared exactly.

    if ischar(src) && strcmpi(src, 'python')
        X = fkcl_readnum(fullfile(m.C.results, 'calib_prior_draws.csv'));
        X = X(1:n, :);
        P.theta = X(:, 1:m.Nz);
        names = {'R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s'};
        for q = 1:numel(names), P.(names{q}) = X(:, m.Nz + q); end
        return
    end
    rng(src);
    P.theta = (m.Lgam * randn(m.Nz, n))';
    P.R = 5e-4 * exp(0.7 * randn(n, 1));
    P.eta = 0.3 + 0.5 * rand(n, 1);
    P.b_c = 180 + 20 * rand(n, 1);
    P.b_e = 5 + 5 * rand(n, 1);
    P.L_B = 12 + 8 * rand(n, 1);
    P.ground = 5 * rand(n, 1);
    P.w = 20 * exp(0.6 * randn(n, 1));
    P.Cl_s = 20500 + 1500 * rand(n, 1);
end
