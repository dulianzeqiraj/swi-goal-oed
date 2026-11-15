function [A, rhs] = fk_assemble(M, u, Rch)
%FK_ASSEMBLE  Flow operator of the Fushe-Kuqe model for a cell-wise log-K multiplier field.
%   [A, rhs] = FK_ASSEMBLE(M, u, Rch) mirrors the subfunction ASSEMBLE of
%   src/fushe_kuqe_field_design.m exactly (same entries, same ordering of the
%   unknowns), vectorised: transmissivity T = K0c .* exp(u) * b, face value
%   Tf = (T_k + T_l)/2, diagonal -sum(Tf), identity rows (h = 0) on the coast
%   cells and rhs = -Rch*dxm^2 on the other cells. u is Nc-by-1 (u = theta(zone)
%   reproduces R.operator(theta)); Rch is the recharge [m/d] (builder: 5e-4).
%   M comes from FK_MODEL_SETUP. Extraction Q [m3/d] at cell k adds +Q to rhs(k).
    T  = M.K0c .* exp(u(:)) * M.b;
    Tf = 0.5 * (T(M.fk) + T(M.fl));                       % one value per directed link k->l, k not coastal
    A  = sparse([M.fk; M.cst; M.ncst], [M.fl; M.cst; M.ncst], ...
                [Tf; ones(numel(M.cst), 1); -accumarray(M.fk_row, Tf, [numel(M.ncst) 1])], M.Nc, M.Nc);
    rhs = zeros(M.Nc, 1); rhs(M.ncst) = -Rch * M.dxm^2;
end
