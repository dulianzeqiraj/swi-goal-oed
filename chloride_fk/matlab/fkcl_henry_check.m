function [toe, s] = fkcl_henry_check(nx, nz)
%FKCL_HENRY_CHECK  Henry's problem with the section solver; returns the toe measured from the
%   inflow face. The repository's Newton solver (src/vd_solve_forward.m) gives 1.4226, 1.3971,
%   1.3918 and 1.3864 m at 16x8, 32x16, 41x21 and 61x31; this solver reproduces those values.
    if nargin < 1, nx = 41; nz = 21; end
    L = 2.0; H = 1.0;
    opt = struct('aniso', 1, 'eps', 0.025, 'phi', 0.35, 'Dm', 1.62925 / 86400, 'aL', 0, 'aT', 0, ...
                 'Qin', 6.6e-5, 'mode', 'henry');
    s = fkcl_vd_init(linspace(0, L, nx + 1), linspace(0, H, nz + 1), zeros(1, nx), H * ones(1, nx), 1e-2 * ones(1, nx), opt);
    s = fkcl_vd_solve(s, [], struct('dt0', 10, 'dtmax', 1e9, 'tol_ss', 1e-12));
    toe = L - fkcl_vd_toe(s, 0.5);
end
