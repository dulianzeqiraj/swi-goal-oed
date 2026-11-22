function [sites, info, risk] = mar_sites(M, S, st, nSites, exclKm)
%MAR_SITES  MAR injection sites chosen from a calibrated arm with PRAG-MAR.
%   [sites, info, risk] = MAR_SITES(M, S, st, nSites, exclKm): the arm's operator
%   at its calibrated parameters (FK_ASSEMBLE), its goal predictive (GOAL_PREDICT:
%   mean and covariance of the future heads at A and B under the planned pumping)
%   and src/prag_mar.m (unchanged) give the reduction of P(A or B intruded) per
%   m3/d of recharge at every cell. Coastal cells and cells within exclKm of a
%   supply well get 0; the top nSites cells are taken with the builder's rule
%   (descending, at least M.P.space = 6 km apart in northing).
    arm = st.arm; u = full(arm.B * st.th(1:arm.nK)); Rch = M.R0; if arm.hasR, Rch = M.R0 * exp(st.th(end)); end
    [A, ~] = fk_assemble(M, u, Rch);
    g = goal_predict(st, S, M);
    [risk, info] = prag_mar(A, M.supCell, g.C, g.mu, S.hc);
    risk(M.isCoast) = 0;
    dA = hypot(M.X - M.X(M.cellA), M.Y - M.Y(M.cellA)); dB = hypot(M.X - M.X(M.cellB), M.Y - M.Y(M.cellB));
    risk(min(dA, dB) < exclKm) = 0;
    [~, ord] = sort(risk, 'descend'); sites = []; usedN = [];
    for q = 1:numel(ord)
        k = ord(q); if ~isfinite(risk(k)) || risk(k) <= 0, continue; end
        N = M.Y(k); if ~isempty(usedN) && any(abs(N - usedN) < M.P.space), continue; end
        sites(end + 1) = k; usedN(end + 1) = N; %#ok<AGROW>
        if numel(sites) >= nSites, break; end
    end
    sites = sites(:)';
end
