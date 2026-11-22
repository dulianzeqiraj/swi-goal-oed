function f = arm_run(M, S, arm, th)
%ARM_RUN  Outputs of arm ARM at parameters TH (one model run, see FK_FORWARD).
    u = arm.B * th(1:arm.nK);
    if arm.hasR, Rch = M.R0 * exp(th(end)); else, Rch = M.R0; end
    f = fk_forward(M, S, full(u), Rch);
end
