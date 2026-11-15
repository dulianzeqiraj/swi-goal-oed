function D = pumping_design(M, S)
%PUMPING_DESIGN  Planned pumping Q_A, Q_B: under the prior (the truth family of
%   MAKE_TRUTH, S.nPrior draws with seeds 900001.., including xi_f) the median of
%   the future head at A and at B equals h_c, i.e. each supply well is intruded
%   with probability 1/2 (as in VENDI-GO). Alternating bisection on Q_A and Q_B.
%   Current pumping Q0 = S.q0frac * Q.
    n = S.nPrior; hR = zeros(n, 2); gA = hR; gB = hR; xf = zeros(n, 1);
    for i = 1:n
        tr = make_truth(M, S, 900000 + i, false);
        H = fk_solve(M, tr.u, tr.Rch); c = M.supCell;
        hR(i, :) = H(c, 1)'; gA(i, :) = H(c, 2)'; gB(i, :) = H(c, 3)'; xf(i) = tr.xif;
    end
    Hf = @(QA, QB) (1 + xf) .* hR + QA * gA + QB * gB;
    QA = 0; QB = 0;
    for outer = 1:60
        lo = 0; hi = 1e5;
        for it = 1:60, mid = 0.5 * (lo + hi); h = Hf(mid, QB); if median(h(:, 1)) > S.hc, lo = mid; else, hi = mid; end, end
        QA = 0.5 * (lo + hi);
        lo = 0; hi = 1e5;
        for it = 1:60, mid = 0.5 * (lo + hi); h = Hf(QA, mid); if median(h(:, 2)) > S.hc, lo = mid; else, hi = mid; end, end
        QBn = 0.5 * (lo + hi);
        if abs(QBn - QB) < 1e-3, QB = QBn; break; end
        QB = QBn;
    end
    D.Q = [QA QB]; D.Q0 = S.q0frac * D.Q;
    h = Hf(QA, QB); D.pA = mean(h(:, 1) < S.hc); D.pB = mean(h(:, 2) < S.hc); D.pAB = mean(any(h < S.hc, 2));
    h0 = hR + D.Q0(1) * gA + D.Q0(2) * gB; D.pA0 = mean(h0(:, 1) < S.hc); D.pB0 = mean(h0(:, 2) < S.hc);
    D.pAB0 = mean(any(h0 < S.hc, 2)); D.medNat = median(hR); D.medCur = median(h0); D.medFut = median(h);
    D.nPrior = n;
end
