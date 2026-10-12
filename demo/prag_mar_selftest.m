function ok = prag_mar_selftest(xlsxfile)
%PRAG_MAR_SELFTEST  Checks of the PRAG-MAR pieces, each reported PASS or FAIL.
%
%   ok = PRAG_MAR_SELFTEST(xlsxfile)
%
%   1. BVN_CDF against Phi2(0,0;r) = 1/4 + asin(r)/(2 pi) and Phi2(a,b;0) = Phi(a)Phi(b).
%   2. The published field design is unchanged when P.supplyIDs is given:
%      the monitoring and MAR wells are the same as without it.
%   3. The adjoint g_A,k = -[A^{-T} e_A]_k against direct solves -A \ e_k
%      (error relative to the largest head change of the direct solve).
%   4. The closed-form gradient against a central difference of the
%      linear-Gaussian P(Q) = 1 - Phi2(a(Q), b(Q); r), with the means shifted
%      by Q g, at the five best PRAG-MAR cells.
%   5. The vectorized operator in PRAG_MAR_CHECK against the project assembler.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    here = fileparts(mfilename('fullpath'));
    if nargin < 1 || isempty(xlsxfile), xlsxfile = fullfile(here, '..', 'data', 'Fushe_Kuqe_All_Data.xlsx'); end
    if exist('prag_mar', 'file') ~= 2, addpath(fullfile(here, '..', 'src')); end
    res = {};
    ncdf = @(x) 0.5 * erfc(-x / sqrt(2));

    % 1. bivariate normal CDF
    r = [-0.8 -0.3 0 0.175 0.5 0.9];
    e1 = max(abs(arrayfun(@(rr) bvn_cdf(0, 0, rr), r) - (0.25 + asin(r) / (2*pi))));
    a = [-1.3 0.2 1.7]; b = [0.4 -0.9 2.1];
    e2 = max(abs(bvn_cdf(a, b, 0) - ncdf(a) .* ncdf(b)));
    res(end+1, :) = {'bvn_cdf vs closed forms', max(e1, e2), 1e-10};

    % 2. the published design does not change
    R0 = fushe_kuqe_field_design(xlsxfile);
    R  = fushe_kuqe_field_design(xlsxfile, struct('supplyIDs', {{'A23', 'R16'}}));
    same = isequal(R0.monCell, R.monCell) && isequal(R0.marCell, R.marCell) && abs(R0.baseArea - R.baseArea) == 0;
    res(end+1, :) = {'published design unchanged', double(~same), 0.5};

    % 3. adjoint vs direct solves at five cells
    A = R.A0; cA = R.supplyCell(1);
    ks = R.pragCell(:)'; ks = [ks round(linspace(1, R.Nc, 3))]; ks = ks(~R.coast(R.act(ks)));
    e3 = 0;
    for k = ks
        ek = zeros(R.Nc, 1); ek(k) = -1;
        dh = A \ ek;
        e3 = max(e3, abs(dh(cA) - R.pragInfo.g(k, 1)) / max(abs(dh)));   % relative to the solution scale
    end
    res(end+1, :) = {'adjoint vs direct solve', e3, 1e-8};

    % 4. closed-form gradient vs central difference of P(Q)
    I = R.pragInfo; s = I.s(:); mu = R.h0(R.supplyCell); dq = 1e-3;
    PQ = @(k, Q) 1 - bvn_cdf((mu(1) + Q * I.g(k, 1) - R.hcrit) / s(1), (mu(2) + Q * I.g(k, 2) - R.hcrit) / s(2), I.r);
    [~, top] = sort(R.RISK_c, 'descend'); e4 = 0;
    for k = top(1:5)'
        fd = -(PQ(k, dq) - PQ(k, -dq)) / (2 * dq);
        e4 = max(e4, abs(fd - R.RISK_c(k)) / abs(R.RISK_c(k)));
    end
    res(end+1, :) = {'closed-form gradient vs FD', e4, 1e-5};

    % 5. vectorized operator vs project assembler
    chk = prag_mar_check(R, {R.pragCell}, 5000, 2, 1);
    res(end+1, :) = {'vectorized operator vs assembler', chk.assemblyRelErr, 1e-12};

    % report
    ok = true;
    fprintf('=== PRAG-MAR self-test ===\n');
    for q = 1:size(res, 1)
        pass = res{q, 2} <= res{q, 3}; ok = ok && pass;
        fprintf('  %-34s error %.2e  (tol %.0e)  %s\n', res{q, 1}, res{q, 2}, res{q, 3}, tern(pass));
    end
    fprintf('overall: %s\n', tern(ok));
end

function s = tern(c), if c, s = 'PASS'; else, s = 'FAIL'; end, end
