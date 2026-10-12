function out = prag_mar_check(R, designs, Q, N, seed)
%PRAG_MAR_CHECK  Exact prior Monte Carlo evaluation of MAR site sets.
%
%   out = PRAG_MAR_CHECK(R, designs, Q, N, seed)
%
%   R       : output of FUSHE_KUQE_FIELD_DESIGN called with P.supplyIDs
%   designs : cell array of site sets (active-cell indices), e.g.
%             {R.marCell, R.pragCell} for the published and the PRAG-MAR sites
%   Q       : recharge per site [m3/day]; a vector evaluates several rates
%             (default [2500 5000 10000])
%   N       : number of prior realizations (default 2000)
%   seed    : random seed (default 9000)
%
%   No linearization. For every realization theta ~ N(0, GamF), the operator
%   is assembled and factorized once and the heads are solved. The head change
%   of each site set needs one more solve and is linear in Q. For the baseline
%   and for every design and rate, the function counts how often each supply
%   well is intruded (h < hcrit) and averages the intruded area.
%
%   The operator is assembled in vectorized form. At the first realization it
%   is compared with the project's own assembler (R.operator), and the relative
%   difference is returned in out.assemblyRelErr.
%
%   OUTPUT  out.none   : struct with pA, pB, pAB (A or B), area [km^2]
%           out.design : struct array, one per design, with fields cells, Q
%                        and pA, pB, pAB, area as vectors over Q
%           out.N, out.seed, out.assemblyRelErr
%
%   See also PRAG_MAR, FUSHE_KUQE_FIELD_DESIGN, demo/fushe_kuqe_prag_mar.m.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 3 || isempty(Q),    Q = [2500 5000 10000]; end
    if nargin < 4 || isempty(N),    N = 2000; end
    if nargin < 5 || isempty(seed), seed = 9000; end
    assert(isfield(R, 'supplyCell'), 'prag_mar_check:supply', ...
           'Call FUSHE_KUQE_FIELD_DESIGN with P.supplyIDs first.');
    if ~iscell(designs), designs = {designs}; end

    rng(seed);
    Lc  = chol(R.GamF, 'lower');  Nz = size(Lc, 1);  Nc = R.Nc;
    sc  = R.supplyCell(:);        nw = numel(sc);
    Q   = Q(:)';                  nq = numel(Q);     nd = numel(designs);
    coastc = R.coast(R.act);
    [fr, fc] = faces(R, coastc);
    rhs = -R.P.R * R.dxm^2 * ones(Nc, 1);  rhs(coastc) = 0;

    ns    = 1 + nd * nq;                          % baseline + designs x rates
    hit   = false(N, nw, ns);
    area  = zeros(N, ns);
    relErr = NaN;
    for i = 1:N
        theta = Lc * randn(Nz, 1);
        A = operator(R, theta, fr, fc, coastc);
        if i == 1                                 % same physics as the project
            [A1, rhs1] = R.operator(theta);
            relErr = max(norm(A - A1, 1) / norm(A1, 1), norm(rhs - rhs1) / norm(rhs1));
            assert(relErr < 1e-12, 'prag_mar_check:assembly', ...
                   'Vectorized operator differs from the project assembler (%.2e).', relErr);
        end
        [L, U, Pp, Qq] = lu(A);
        sol = @(b) Qq * (U \ (L \ (Pp * b)));
        h = sol(rhs);
        hit(i, :, 1) = h(sc)' < R.hcrit;  area(i, 1) = R.goalA(h);
        for d = 1:nd
            rd = zeros(Nc, 1); rd(designs{d}) = -1;
            u  = sol(rd);                         % head change per m3/day at every site
            for q = 1:nq
                k = 1 + (d - 1) * nq + q;  hq = h + Q(q) * u;
                hit(i, :, k) = hq(sc)' < R.hcrit;  area(i, k) = R.goalA(hq);
            end
        end
    end

    summ = @(k) struct('pA', mean(hit(:, 1, k)), 'pB', mean(hit(:, end, k)), ...
                       'pAB', mean(any(hit(:, :, k), 2)), 'area', mean(area(:, k)));
    out.none = summ(1);
    for d = 1:nd
        S = struct('cells', designs{d}(:)', 'Q', Q, 'pA', zeros(1, nq), 'pB', zeros(1, nq), ...
                   'pAB', zeros(1, nq), 'area', zeros(1, nq));
        for q = 1:nq
            s = summ(1 + (d - 1) * nq + q);
            S.pA(q) = s.pA; S.pB(q) = s.pB; S.pAB(q) = s.pAB; S.area(q) = s.area;
        end
        out.design(d) = S; %#ok<AGROW>
    end
    out.N = N; out.seed = seed; out.assemblyRelErr = relErr;
end

% ============================= helpers ==================================
function [fr, fc] = faces(R, coastc)
%FACES  (row, neighbour) pairs of the 5-point stencil for every non-coast cell.
    fr = []; fc = [];
    nb = [-1 0; 1 0; 0 -1; 0 1];
    k  = (1:R.Nc)';
    for q = 1:4
        jj = R.aj + nb(q, 1); ii = R.ai + nb(q, 2);
        ok = ~coastc & jj >= 1 & jj <= R.ny & ii >= 1 & ii <= R.nx;
        lin = zeros(R.Nc, 1); lin(ok) = sub2ind([R.ny R.nx], jj(ok), ii(ok));
        ok(ok) = R.inside(lin(ok));
        fr = [fr; k(ok)];                         %#ok<AGROW>
        fc = [fc; R.idx(lin(ok))];                %#ok<AGROW>
    end
end

function A = operator(R, theta, fr, fc, coastc)
%OPERATOR  Vectorized copy of the project assembler (arithmetic face T).
    Tc = (R.K0c .* exp(theta(R.zone))) * R.P.b;
    Tf = 0.5 * (Tc(fr) + Tc(fc));
    dg = accumarray(fr, -Tf, [R.Nc 1]);  dg(coastc) = 1;
    A  = sparse([fr; (1:R.Nc)'], [fc; (1:R.Nc)'], [Tf; dg], R.Nc, R.Nc);
end
