function P = vd_params()
%VD_PARAMS  Henry-class parameters (Zeqiraj dissertation p.46 / p.9).
%   eps   = (rho_s - rho_f)/rho_f         buoyancy ratio
%   phi   = effective porosity
%   Dmol  = PORE-SCALE diffusivity [m^2/s], the coefficient that vd_residual
%           multiplies by phi. The bulk coefficient in the transport operator is
%           therefore phi*Dmol = 6.6e-6 m^2/s, the classic Henry value, and the
%           Henry number is b = phi*Dmol/Q = 0.1. It was 6.6e-6 here, which put
%           the bulk coefficient at phi*6.6e-6 = 2.31e-6 and b at 0.035: phi was
%           applied twice. demo/gate2_henry.m carries the same quantity as
%           Dm = 1.62925 m^2/day, and 1.62925/86400 = 1.88571e-5.
%           (alpha_L = alpha_T = 0 -> pure diffusion)
%   Q     = freshwater inflow flux [m^2/s] per unit height (classic Henry)
%   Kref  = equivalent hydraulic conductivity [m/s] = 864 m/day
    P.eps  = 0.025;
    P.phi  = 0.35;
    P.Dmol = 1.62925/86400;   % = 1.88571e-5 m^2/s; phi*Dmol = 6.6e-6
    P.Q    = 6.6e-5;
    P.Kref = 1.0e-2;
end
