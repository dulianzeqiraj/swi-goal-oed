function H = fkcl_hydrochem(C, D)
%FKCL_HYDROCHEM  Seawater fractions and ion-exchange indicators of the four analyses.
%
%   H = FKCL_HYDROCHEM(C, D) uses the conservative mixing of the freshest sample
%   (well 193) with Adriatic seawater (standard seawater scaled to S = 38.3):
%       f       = (Cl - Cl_f) / (Cl_sw - Cl_f)                       seawater fraction
%       dX      = X_obs - [X_f + f (X_sw - X_f)]   in meq/L          ion-exchange deviation
%       Na/Cl   molar ratio (seawater 0.86)
%       Revelle = Cl / HCO3 in meq/L (Revelle 1941)
%       BEX     = Na + K + Mg - 1.0716 Cl in meq/L (Stuyfzand): < 0 salinization, > 0 freshening
%   and the chloride trend of wells 341 and 503 (1984-2001).

    sw = struct();
    fn = fieldnames(C.sw35);
    for q = 1:numel(fn), sw.(fn{q}) = C.sw35.(fn{q}) * C.S_adr / 35 * C.rho_sw; end
    ch = D.chem;
    ifr = find(strcmp(ch.well, '193'));
    meq = @(ion, mg) mg / C.molar.(ion) * C.charge.(ion);
    n = numel(ch.well);
    H.well = ch.well; H.position = ch.position; H.sw = sw;
    H.f = (ch.Cl - ch.Cl(ifr)) / (sw.Cl - ch.Cl(ifr));
    ions = {'Na', 'Ca', 'Mg', 'K', 'SO4'};
    for q = 1:numel(ions)
        ion = ions{q};
        mix = ch.(ion)(ifr) + H.f * (sw.(ion) - ch.(ion)(ifr));
        H.(['d' ion]) = meq(ion, ch.(ion)) - meq(ion, mix);
    end
    H.NaCl = (ch.Na / C.molar.Na) ./ (ch.Cl / C.molar.Cl);
    H.revelle = meq('Cl', ch.Cl) ./ meq('HCO3', ch.HCO3);
    H.BEX = meq('Na', ch.Na) + meq('K', ch.K) + meq('Mg', ch.Mg) - 1.0716 * meq('Cl', ch.Cl);
    H.TDS = ch.TDS; H.Cl = ch.Cl; H.sw_pct_source = ch.sw_pct;
    H.class = cell(n, 1);
    for k = 1:n
        if H.f(k) < 1e-6, H.class{k} = 'fresh (end-member)';
        elseif H.BEX(k) < 0, H.class{k} = 'salinization (reverse cation exchange)';
        else, H.class{k} = 'freshening (cation exchange)';
        end
    end
    % chloride trend
    H.trend = D.trend;
    H.trend.rate = (D.trend.Cl(:, end) - D.trend.Cl(:, 1)) / (D.trend.years(end) - D.trend.years(1));
end
