function C = fk_checks(M, S)
%FK_CHECKS  Numerical checks of the model used by PROVA-GO.
%   C = FK_CHECKS(M, S) reports
%   1. assembly: FK_ASSEMBLE vs R.operator(theta) of the builder for random zonal
%      theta (max abs difference of the matrices and right-hand sides) and the
%      solution of FK_SOLVE vs A\rhs;
%   2. sign of pumping: extraction of S.Q(1) m3/d at A lowers the head at A;
%   3. reciprocity: the head change at observation well j per unit extraction at
%      A equals the head change at A per unit extraction at j (symmetric interior
%      block of the operator);
%   4. flux-scale invariance: multiplying all K and the recharge by c leaves the
%      recharge-driven heads unchanged; the metered Stage-0 responses scale as 1/c;
%      the heads under current (metered) pumping change only through the pumping term.
    rng(12345, 'twister');
    e = zeros(5, 3);
    for t = 1:5
        th = chol(M.GamF, 'lower') * randn(M.Nz, 1);
        [A1, r1] = M.operator(th); [A2, r2] = fk_assemble(M, th(M.zone), M.R0);
        H = fk_solve(M, th(M.zone), M.R0); h1 = A1 \ r1;
        e(t, :) = [full(max(abs(A1(:) - A2(:)))) max(abs(r1 - r2)) max(abs(H(:, 1) - h1)) / max(abs(h1))];
    end
    C.assembly_maxAbsDiffA = max(e(:, 1)); C.assembly_maxAbsDiffRhs = max(e(:, 2));
    C.assembly_identical = all(e(:, 1) == 0 & e(:, 2) == 0); C.solve_maxRelDiff = max(e(:, 3));
    % 2. sign of pumping (direct solve with the builder's operator, extraction adds +Q to rhs)
    [A1, r1] = M.operator(zeros(M.Nz, 1)); h1 = A1 \ r1; rq = r1; rq(M.cellA) = rq(M.cellA) + S.Q(1); hq = A1 \ rq;
    C.sign_hA_noPump = h1(M.cellA); C.sign_hA_pumped = hq(M.cellA); C.sign_ok = hq(M.cellA) < h1(M.cellA);
    H = fk_solve(M, zeros(M.Nc, 1), M.R0); C.sign_fksolve_gA_atA = H(M.cellA, 2);
    C.sign_fksolve_match = abs(h1(M.cellA) + S.Q(1) * H(M.cellA, 2) - hq(M.cellA)) / abs(hq(M.cellA));
    % 3. reciprocity: unit extraction at each observation well
    Q = sparse(M.obsCell, 1:M.J, 1, M.Nc, M.J); u = chol(M.GamF, 'lower') * randn(M.Nz, 1);
    Hr = fk_solve(M, u(M.zone), M.R0, full(Q));
    gA_at_j = Hr(M.obsCell, 2); gj_at_A = Hr(M.cellA, 4:end)';
    C.recip_maxRelDiff = max(abs(gA_at_j - gj_at_A)) / max(abs(gA_at_j));
    % 4. flux-scale invariance
    c = 1.5; f1 = fk_forward(M, S, u(M.zone), M.R0); f2 = fk_forward(M, S, u(M.zone) + log(c), c * M.R0);
    H1 = fk_solve(M, u(M.zone), M.R0); H2 = fk_solve(M, u(M.zone) + log(c), c * M.R0);
    J = M.J;
    C.scale_c = c;
    C.scale_naturalHeads_maxAbsDiff = max(abs(H1(:, 1) - H2(:, 1)));
    C.scale_naturalHeads_maxHead = max(abs(H1(:, 1)));
    C.scale_responseRatio = (f2(J+1:3*J) ./ f1(J+1:3*J))';
    C.scale_responseRatio_minmax = [min(C.scale_responseRatio) max(C.scale_responseRatio)];
    C.scale_curHeads_maxAbsDiff = max(abs(f2(1:J) - f1(1:J)));
    C.scale_curHeads_pumpTerm_maxAbs = max(abs(f1(1:J) - H1(M.obsCell, 1)));
    C.scale_curHeads_rmsDiff = sqrt(mean((f2(1:J) - f1(1:J)).^2));
    C.scale_selfResponse_ratio = H2(M.cellA, 2) / H1(M.cellA, 2);
    C.scale_example = [f1(J + (1:5))'; f2(J + (1:5))'];
end
