function [f, H] = fk_forward(M, S, u, Rch)
%FK_FORWARD  All outputs of one model run (one assembly + one factorisation).
%   [f, H] = FK_FORWARD(M, S, u, Rch) for the log-K multiplier field u and the
%   recharge Rch returns the column of outputs (J = M.J observation wells)
%     f(1:J)       heads at the observation wells under the current pumping (calibration data)
%     f(J+1:2J)    head rise at the wells when the pumping at A is stopped (Stage 0, metered dQ = Q_A0)
%     f(2J+1:3J)   head rise when the pumping at B is stopped (dQ = Q_B0)
%     f(3J+1:3J+2) future heads at A and B under the planned pumping, future recharge factor 1 (xi_f = 0)
%     f(3J+3:3J+4) natural heads (recharge only) at A and B: dH/dxi_f
%   and H = [h_R g_A g_B] (FK_SOLVE). The pumping states are extra right-hand
%   sides of the same run.
    H = fk_solve(M, u, Rch);
    o = M.obsCell(:); s = M.supCell(:);
    hR = H(:, 1); gA = H(:, 2); gB = H(:, 3);
    f = [hR(o) + S.Q0(1) * gA(o) + S.Q0(2) * gB(o);
         -S.Q0(1) * gA(o);
         -S.Q0(2) * gB(o);
         hR(s) + S.Q(1) * gA(s) + S.Q(2) * gB(s);
         hR(s)];
end
