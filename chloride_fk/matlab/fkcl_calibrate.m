function Cal = fkcl_calibrate(m, N, src)
%FKCL_CALIBRATE  Importance-weighted calibration of the chloride model to the documented facts.
%
%   Cal = FKCL_CALIBRATE(m, N, src) runs N prior draws (src = seed, or 'python' for the draws of the
%   Python reference), computes the summary statistics of each run, weights them with FKCL_LOGLIK and
%   returns the ensemble, the weights, the effective sample size and prior/posterior quantiles.
%   Takes about 2-3 minutes for N = 20000 in MATLAB.

    P = fkcl_prior(m, N, src);
    [~, names] = fkcl_summaries(m, fkcl_model_run(m, fkcl_member(P, 1)));
    S = zeros(N, numel(names)); mk = [];
    t0 = tic;
    for i = 1:N
        o = fkcl_model_run(m, fkcl_member(P, i));
        [S(i, :), ~, mk] = fkcl_summaries(m, o, mk);
        if mod(i, 2000) == 0, fprintf('  calibration %d / %d (%.0f s)\n', i, N, toc(t0)); end
    end
    ll = fkcl_loglik(m.C, S);
    w = exp(ll - max(ll)); w = w / sum(w);
    Cal.P = P; Cal.S = S; Cal.names = names; Cal.ll = ll; Cal.w = w; Cal.ess = 1 / sum(w.^2);
    pq = [0.05 0.5 0.95];
    for k = 1:numel(names)
        Cal.prior.(names{k}) = fkcl_wquantile(S(:, k), ones(N, 1) / N, pq);
        Cal.post.(names{k}) = fkcl_wquantile(S(:, k), w, pq);
    end
    pn = {'R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s'};
    for k = 1:numel(pn)
        Cal.params_prior.(pn{k}) = fkcl_wquantile(P.(pn{k}), ones(N, 1) / N, pq);
        Cal.params_post.(pn{k}) = fkcl_wquantile(P.(pn{k}), w, pq);
    end
end
