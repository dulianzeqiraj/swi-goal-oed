function Post = fkcl_posterior(m, Cal, M, src)
%FKCL_POSTERIOR  Posterior chloride ensemble, per-cell products and affected areas.
%
%   Post = FKCL_POSTERIOR(m, Cal, M, src) resamples M members from the calibrated ensemble
%   (systematic resampling with seed src, or the indices of the Python run when src = 'python'),
%   runs each member and returns
%     Post.idx                      member indices into Cal
%     Post.Cl_sh, Cl_mid, Cl_dp     M x Nc chloride [mg/L] (single precision)
%     Post.h, Post.wedge            heads [m], seawater wedge at the base (logical)
%     Post.cells                    per-cell products: p05/p50/p95 chloride, P(Cl > 250) at three
%                                   depths, P(wedge), median head
%     Post.area                     M x 4 areas [km2]: Cl > 250 upper, middle, base; wedge

    if ischar(src) && strcmpi(src, 'python')
        idx = fkcl_readnum(fullfile(m.C.results, 'post_idx.csv')); idx = idx(1:M);
    else
        rng(src); u = (rand + (0:M - 1)') / M;
        c = cumsum(Cal.w); idx = zeros(M, 1);
        for k = 1:M, idx(k) = min(find(c >= u(k), 1, 'first'), numel(c)); end
    end
    Nc = m.Nc;
    Post.idx = idx;
    Post.Cl_sh = zeros(M, Nc, 'single'); Post.Cl_mid = Post.Cl_sh; Post.Cl_dp = Post.Cl_sh;
    Post.h = Post.Cl_sh; Post.zeta = Post.Cl_sh; Post.wedge = false(M, Nc);
    for k = 1:M
        o = fkcl_model_run(m, fkcl_member(Cal.P, idx(k)));
        Post.Cl_sh(k, :) = o.Cl_sh; Post.Cl_mid(k, :) = o.Cl_mid; Post.Cl_dp(k, :) = o.Cl_dp;
        Post.h(k, :) = o.h; Post.zeta(k, :) = o.zeta; Post.wedge(k, :) = o.wedge;
    end
    v = m.valid'; L = m.C.Cl_lim; A = m.area / 1e6;
    lay = {'sh', 'mid', 'dp'};
    for q = 1:3
        X = double(Post.(['Cl_' lay{q}]));
        Qx = fkcl_quantile(X, [0.05 0.5 0.95]);
        Post.cells.(['Cl_' lay{q} '_p05']) = Qx(1, :)'; Post.cells.(['Cl_' lay{q} '_p50']) = Qx(2, :)';
        Post.cells.(['Cl_' lay{q} '_p95']) = Qx(3, :)';
        Post.cells.(['P250_' lay{q}]) = mean(X > L, 1)';
        Post.area(:, q) = sum((X > L) & v, 2) * A;
    end
    Post.cells.P_wedge = mean(Post.wedge, 1)';
    Post.cells.h_p50 = fkcl_quantile(double(Post.h), 0.5)';
    Post.area(:, 4) = sum(Post.wedge & v, 2) * A;
    fn = fieldnames(Post.cells);
    for q = 1:numel(fn), x = Post.cells.(fn{q}); x(~m.valid) = NaN; Post.cells.(fn{q}) = x; end
    Post.area_q = fkcl_quantile(Post.area, [0.05 0.5 0.95]);
end
