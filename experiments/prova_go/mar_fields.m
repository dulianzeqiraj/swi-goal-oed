function F = mar_fields(M, S, u, Rch, sites, qSite, xif)
%MAR_FIELDS  Head fields of the MAR process for one aquifer (u, Rch):
%   current pumping (Q0 at A and B), planned pumping (Q at A and B), planned
%   pumping + injection of qSite m3/d at each of SITES; future recharge factor
%   (1 + xif) on the recharge-driven part of the planned states. Intruded area =
%   cells with h < h_c (km^2); the toe is the h = h_c contour.
    if nargin < 7, xif = 0; end
    Qm = zeros(M.Nc, 1); Qm(sites) = -qSite;            % injection = negative extraction
    H = fk_solve(M, u, Rch, Qm);
    hR = H(:, 1); gA = H(:, 2); gB = H(:, 3); hM = H(:, 4);
    F.cur = hR + S.Q0(1) * gA + S.Q0(2) * gB;
    F.plan = (1 + xif) * hR + S.Q(1) * gA + S.Q(2) * gB;
    F.mar = F.plan + hM; F.mound = hM; F.nat = hR;
    a = M.area / 1e6;
    F.areaCur = a * nnz(F.cur < S.hc); F.areaPlan = a * nnz(F.plan < S.hc); F.areaMar = a * nnz(F.mar < S.hc);
    F.areaNat = a * nnz(F.nat < S.hc);
    F.hSup = [F.cur(M.supCell)'; F.plan(M.supCell)'; F.mar(M.supCell)'];
    F.sites = sites; F.qSite = qSite;
end
