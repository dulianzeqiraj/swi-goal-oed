function S = prova_settings(M)
%PROVA_SETTINGS  All fixed settings of PROVA-GO (chosen a priori; documented in README.md).
    S.sigH = 0.05;      % m, noise of the calibration heads
    S.sigV = 0.01;      % m, noise of the Stage-0 head changes (validation items)
    S.sigXi = 0.08;     % sd of the future change of mean recharge (fraction), as VENDI-GO
    S.sigR = 0.3;       % sd of log recharge (truth and arm priors)
    S.zetaSd = 0.35; S.zetaL = 2.0;    % sub-zonal field: sd, exponential correlation exp(-d/2 km)
    S.stripLog = -1.0;  % log-multiplier of the coastal low-K strip (half of the truths)
    S.hc = M.hcrit;     % critical head h_c = base*delta = 1.0 m
    S.z90 = 1.6448536269514722;   % 90 % central interval: +-1.645 sd
    S.fdStep = 1e-3; S.lam0 = 1e-2; S.tolRel = 1e-4; S.maxIt = 15;
    S.k = 0.5; S.beta = 0.95; S.Hor = 60; S.kSens = [0.2 0.8];
    S.minItems = 5;     % items an arm needs before it can be selected
    S.Q = [NaN NaN]; S.Q0 = [NaN NaN]; S.budget = NaN;   % set in prova_go_run (pumping design, budget)
    S.q0frac = 0.5;     % current pumping = 0.5 x planned pumping
    S.nPrior = 300;     % prior draws for the pumping design
    S.budgetFactor = 2.5;
end
