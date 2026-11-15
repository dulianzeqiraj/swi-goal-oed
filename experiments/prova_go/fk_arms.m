function arms = fk_arms(M, S)
%FK_ARMS  The five competing model structures (bandit arms) of PROVA-GO.
%   arms = FK_ARMS(M, S) returns a 1-by-5 struct array. Each arm maps its
%   parameter vector theta (log-multipliers, Gaussian prior N(0, Gam)) to a
%   cell-wise log-K multiplier field u = B*theta(1:nK) and a recharge
%   Rch = R0*exp(theta(end)) (A1: Rch = R0 fixed).
%     A1 'zones, recharge fixed'  Nz zone multipliers, prior GamF (PEST practice)
%     A2 'uniform'                 one global multiplier (sd 1) + log recharge (sd 0.3)
%     A3 'facies'                  three facies-class multipliers (sd 0.5) + log recharge
%     A4 'zones + recharge'        Nz zone multipliers (GamF) + log recharge (sd 0.3)
%     A5 'zones + strip + rech.'   A4 + one multiplier of the cells within 1.5 km of the coast (sd 1)
    Nc = M.Nc; Nz = M.Nz;
    Bz = sparse((1:Nc)', M.zone, 1, Nc, Nz);
    Bf = sparse((1:Nc)', M.zfac(M.zone), 1, Nc, 3);
    Bs = sparse(find(M.strip), 1, 1, Nc, 1);
    sR = S.sigR^2;
    def = { 'A1', 'zones, recharge fixed',      Bz,              M.GamF,                       false;
            'A2', 'uniform',                    sparse(ones(Nc, 1)), 1,                         true;
            'A3', 'facies',                     Bf,              0.25 * eye(3),                true;
            'A4', 'zones + recharge',           Bz,              M.GamF,                       true;
            'A5', 'zones + strip + recharge',   [Bz Bs],         blkdiag(M.GamF, 1),           true };
    for m = 1:5
        a.id = def{m, 1}; a.name = def{m, 2}; a.B = def{m, 3}; a.nK = size(a.B, 2);
        a.hasR = def{m, 5};
        if a.hasR, a.Gam = blkdiag(def{m, 4}, sR); else, a.Gam = def{m, 4}; end
        a.n = size(a.Gam, 1); a.th0 = zeros(a.n, 1); a.Gi = inv(a.Gam); a.Gi = 0.5 * (a.Gi + a.Gi');
        arms(m) = a; %#ok<AGROW>
    end
end
