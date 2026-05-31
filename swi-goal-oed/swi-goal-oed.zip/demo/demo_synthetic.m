function demo_synthetic()
%DEMO_SYNTHETIC  Linear-Gaussian verification of the goal-oriented operator.
%
%   Reproduces the core linear-Gaussian checks of Lemma 1: that the
%   goal-oriented EIG (Eq. 9) equals the mutual information between the
%   scalar goal and the data, and that adding informative observations
%   monotonically increases EIG. This is the regime in which the operator
%   is exact (no variable-density physics involved).
%
%   Run:  >> demo_synthetic
%
%   Author: D. Zeqiraj.  License: MIT.

    rng(0);
    n = 12;                       % parameter dimension
    GamF = make_spd(n, 0.4);      % a generic SPD prior
    h = randn(1, n);              % scalar goal sensitivity
    H = h;

    % three candidate observation rows of increasing informativeness
    M = 6;
    Gcand = randn(M, n);
    noise_var = 0.05;

    fprintf('--- Lemma 1: EIG vs mutual information (scalar goal) ---\n');
    S = [1 3 5];
    G  = Gcand(S, :);
    Gn = noise_var * eye(numel(S));
    [eig, IF, s0] = eig_operator(G, H, GamF, Gn);

    % independent MI check via posterior variance reduction
    Gpost = inv(inv(GamF) + (G' * (Gn \ G)));
    var_post = H * Gpost * H';
    mi = 0.5 * log(s0 / var_post);

    fprintf('  EIG (operator)        = %.6f nats\n', eig);
    fprintf('  MI  (posterior var)   = %.6f nats\n', mi);
    fprintf('  abs difference        = %.3e   (should be ~0)\n', abs(eig - mi));

    fprintf('\n--- Monotonicity: EIG grows as observations are added ---\n');
    e = zeros(1, M);
    for k = 1:M
        Gk = Gcand(1:k, :);
        e(k) = eig_operator(Gk, H, GamF, noise_var * eye(k));
    end
    disp(array2table(e, 'VariableNames', compose("k%d", 1:M)));
    assert(all(diff(e) > -1e-10), 'EIG should be non-decreasing under inclusion.');
    fprintf('  monotone non-decreasing: OK\n');
end

function A = make_spd(n, off)
    A = off * ones(n) + (1 - off) * eye(n);
    A = 0.5 * (A + A');
end
