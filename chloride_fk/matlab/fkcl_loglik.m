function ll = fkcl_loglik(C, S)
%FKCL_LOGLIK  Log-likelihood of the documented facts for rows of summary statistics S.
%   T1 area (Gaussian), T2 littoral head (Gaussian), T3a seawater fraction of the wells 341/503
%   (log-normal; mid-depth screens when C.variant = 'second', upper screens when 'shallow'),
%   T3c fresh NE recharge zone (logistic). The central-band fraction (well 340) is held out.
    o = C.obs;
    ll = -0.5 * ((S(:, 1) - o.area) / o.area_sd).^2;
    ll = ll - 0.5 * ((S(:, 2) - o.hlit) / o.hlit_sd).^2;
    if strcmpi(C.variant, 'second'), fsw = S(:, 11); else, fsw = S(:, 3); end
    ll = ll - 0.5 * ((log(max(fsw, 1e-6)) - log(o.f_sw)) / o.logsd).^2;
    z = (S(:, 5) - o.cl_ne) / o.cl_ne_s;
    ll = ll - (max(z, 0) + log1p(exp(-abs(z))));        % log(1 + exp(z)), stable
end
