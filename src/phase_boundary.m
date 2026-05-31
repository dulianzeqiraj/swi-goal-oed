function out = phase_boundary(Gcand, H, blocks, cross, noise_var, budget, rho_grid)
%PHASE_BOUNDARY  Poolability phase boundary: pooling loss L(rhoF) and rho_c.
%
%   out = PHASE_BOUNDARY(Gcand, H, blocks, cross, noise_var, budget, rho_grid)
%
%   For each cross-facies correlation rhoF on rho_grid, this computes the
%   facies-pooling loss (Eq. 12)
%       L(rhoF) = max_d Phi_rhoF(d) - Phi_rhoF(d0),
%   where Phi is the goal-oriented EIG, d is selected by exhaustive search
%   over budget-feasible designs under the *true* prior Gamma(rhoF), and d0
%   is the pooled-optimal design (selected under Gamma(1)). It returns the
%   normalized order parameter Lambda = L/L(0), the critical correlation
%   rho_c (onset of the machine-zero "dead zone"), and the loss curve.
%
%   INPUTS
%     Gcand     : M-by-n candidate observation sensitivities
%     H         : 1-by-n scalar goal sensitivity
%     blocks    : within-facies covariance blocks (see FACIES_PRIOR)
%     cross     : cross-facies coupling (see FACIES_PRIOR; [] for default)
%     noise_var : scalar i.i.d. observation-noise variance
%     budget    : design cardinality B (exhaustive over all B-subsets)
%     rho_grid  : vector of rhoF values in [0,1]
%
%   OUTPUT (struct)
%     out.rho     : rho_grid
%     out.L       : pooling loss L(rhoF) [nats]
%     out.Lambda  : normalized order parameter L/L(0)
%     out.rho_c   : estimated critical correlation (dead-zone onset)
%     out.d0      : pooled-optimal design (indices)
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    M = size(Gcand, 1);
    combs = nchoosek(1:M, budget);          % all budget-feasible designs

    % pooled-optimal design d0 under Gamma(1) (facies-blind)
    Gam1 = facies_prior(1.0, blocks, cross);
    d0 = best_design(Gcand, H, Gam1, noise_var, combs);

    nR = numel(rho_grid);
    L  = zeros(nR, 1);
    for i = 1:nR
        Gam = facies_prior(rho_grid(i), blocks, cross);
        dstar = best_design(Gcand, H, Gam, noise_var, combs);
        e_star = design_eig(Gcand, H, Gam, noise_var, dstar);
        e_0    = design_eig(Gcand, H, Gam, noise_var, d0);
        L(i)   = max(e_star - e_0, 0);
    end

    L0     = L(1);
    Lambda = L / max(L0, eps);
    % dead-zone onset: largest rho where L is still > machine zero
    tol    = 1e-12 * max(L0, eps);
    active = L > tol;
    if any(active)
        rho_c = rho_grid(find(active, 1, 'last'));
    else
        rho_c = NaN;
    end

    out = struct('rho', rho_grid(:), 'L', L, 'Lambda', Lambda, ...
                 'rho_c', rho_c, 'd0', d0);
end

% ----------------------------------------------------------------------
function d = best_design(Gcand, H, Gam, noise_var, combs)
    bestE = -inf; d = combs(1,:);
    for c = 1:size(combs,1)
        e = design_eig(Gcand, H, Gam, noise_var, combs(c,:));
        if e > bestE, bestE = e; d = combs(c,:); end
    end
end

function e = design_eig(Gcand, H, Gam, noise_var, S)
    G  = Gcand(S, :);
    if isscalar(noise_var)
        Gn = noise_var * eye(numel(S));
    else
        Gn = diag(noise_var(S));      % per-candidate (per-facies) noise
    end
    e  = eig_operator(G, H, Gam, Gn);
end
