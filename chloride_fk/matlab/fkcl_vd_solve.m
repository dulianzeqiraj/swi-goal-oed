function s = fkcl_vd_solve(s, c0, opt)
%FKCL_VD_SOLVE  Steady state of the variable-density section by a fully implicit march in time.
%
%   s = FKCL_VD_SOLVE(s, c0, opt) starts from c0 (default fresh) and takes implicit Euler steps;
%   each step converges the flow-transport coupling by inner Picard iterations (tolerance tol_in),
%   halves when the inner loop fails and grows by 1.6 when it converges in a few iterations. Every
%   25 steps the steady residual gap = max|T(c) - c| (T = steady transport with the current flow)
%   is computed; the march stops when gap < tol_ss. Returns s.c, s.h, s.gap, s.steps, s.t_end.
%   opt fields (defaults): dt0 10 d, dtmax 1e5 d, tol_in 1e-8, max_in 25, tol_ss 1e-6, max_steps 4000.

    d0 = struct('dt0', 10, 'dtmax', 1e5, 'tol_in', 1e-8, 'max_in', 25, 'tol_ss', 1e-6, 'max_steps', 4000, 'verbose', false);
    if nargin < 3, opt = struct(); end
    fn = fieldnames(d0);
    for q = 1:numel(fn), if ~isfield(opt, fn{q}), opt.(fn{q}) = d0.(fn{q}); end, end
    if nargin < 2 || isempty(c0), c = zeros(s.N, 1); else, c = c0(:); end
    dt = opt.dt0; t = 0; gap = inf;
    for step = 1:opt.max_steps
        ck = c; ok = false;
        for k = 1:opt.max_in
            [~, qx, qz, qs] = fkcl_vd_flow(s, ck);
            cn = fkcl_vd_transport(s, qx, qz, qs, dt, c);
            din = max(abs(cn - ck)); ck = cn;
            if din < opt.tol_in, ok = true; break; end
        end
        if ~ok
            dt = dt / 2;
            if dt < 1e-3, error('fkcl:vd', 'time step collapsed'); end
            continue
        end
        c = ck; t = t + dt;
        if mod(step, 25) == 0
            [~, qx, qz, qs] = fkcl_vd_flow(s, c);
            gap = max(abs(fkcl_vd_transport(s, qx, qz, qs) - c));
            if opt.verbose, fprintf('  step %d  t = %.4g d  dt = %.3g d  gap = %.2e\n', step, t, dt, gap); end
            if gap < opt.tol_ss, break; end
        end
        if k < 7, dt = min(dt * 1.6, opt.dtmax); end
    end
    [s.h, qx, qz, qs] = fkcl_vd_flow(s, c);
    s.gap = max(abs(fkcl_vd_transport(s, qx, qz, qs) - c));
    s.c = c; s.steps = step; s.t_end = t;
end
