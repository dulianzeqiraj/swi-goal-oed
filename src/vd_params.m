function P = vd_params()
%VD_PARAMS  Henry-class parameters (Zeqiraj dissertation p.46 / p.9).
%   eps   = (rho_s - rho_f)/rho_f         buoyancy ratio
%   phi   = effective porosity
%   Dmol  = molecular diffusion [m^2/s]   (alpha_L=alpha_T=0 -> pure diffusion)
%   Q     = freshwater inflow flux [m^2/s] per unit height (classic Henry)
%   Kref  = equivalent hydraulic conductivity [m/s] = 864 m/day
    P.eps  = 0.025;
    P.phi  = 0.35;
    P.Dmol = 6.6e-6;
    P.Q    = 6.6e-5;
    P.Kref = 1.0e-2;
end
