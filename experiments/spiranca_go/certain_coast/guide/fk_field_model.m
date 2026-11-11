function R = fk_field_model(dataDir, P)
%FK_FIELD_MODEL The Fushë-Kuqe field model and the goal-oriented design, with the public CERTAIN-COAST functions.
%   R = fk_field_model(DATADIR) reads wells.csv and boundary.csv from DATADIR and builds the model of
%   Zeqiraj (2026), Journal of Hydrology 680, 136559: confined areal flow on the real polygon (cells of 0.25 km,
%   conductivity by inverse-distance weighting of the 43 measured wells, the coast at h = 0 along the whole western
%   margin), a facies prior on the pilot zones, the intruded area (Ghyben-Herzberg, h < 1.0 m), the goal-oriented
%   information field, the recharge (MAR) field, the published top-5 monitoring and top-3 recharge sites, and two
%   uses of the public package on the real field: certaincoast.network.greedyDesign among the real wells and
%   certaincoast.network.rechargeRisk (PRAG-MAR) for two supply wells.
%   R = fk_field_model(DATADIR, P) overrides parameters (fields of the default struct below).
%
%   The data belong to the Albanian Geological Survey and to Prof. Arjan Beqiraj and are used
%   with their permission; they stay out of the public CERTAIN-COAST repository.

%   Copyright 2026 Dulian Zeqiraj. Licensed under the Apache License, Version 2.0 (code only, not the data).

if nargin < 1 || isempty(dataDir)
    dataDir = fullfile(fileparts(mfilename('fullpath')), 'data');
end
Pdef = struct('b', 30, 'base', 40, 'R', 5e-4, 'delta', 0.025, 'dx', 0.25, 'sn', 0.2, 'rhoF', 0.6, 'Nmon', 5, ...
              'Nmar', 3, 'space', 6.0, 'supply', {{'A23', 'R16'}});
if nargin < 2 || isempty(P)
    P = Pdef;
end
fn = fieldnames(Pdef);
for q = 1:numel(fn)
    if ~isfield(P, fn{q})
        P.(fn{q}) = Pdef.(fn{q});
    end
end
P.hcrit = P.base * P.delta;

% ---- data -------------------------------------------------------------------------------------------------------
B = dlmread(fullfile(dataDir, 'boundary.csv'), ',', 1, 0);
B = B(all(isfinite(B), 2), :);
fid = fopen(fullfile(dataDir, 'wells.csv'));
C = textscan(fid, '%s %f %f %f', 'Delimiter', ',', 'HeaderLines', 1, 'EmptyValue', NaN);
fclose(fid);
WXY = [C{2}, C{3}];
ok = all(isfinite([WXY, C{4}]), 2);
WK = [WXY(ok, :), C{4}(ok)];
wellID = C{1}(ok);
x0 = min(B(:, 1));
y0 = min(B(:, 2));
Bk = [(B(:, 1) - x0), (B(:, 2) - y0)] / 1000;
Wk = [(WK(:, 1) - x0), (WK(:, 2) - y0)] / 1000;
Wk(:, 3) = WK(:, 3);

% ---- grid and conductivity -----------------------------------------------------------------------------------------
dx = P.dx;
xs = 0:dx:max(Bk(:, 1)) + dx;
ys = 0:dx:max(Bk(:, 2)) + dx;
[GX, GY] = meshgrid(xs, ys);
[ny, nx] = size(GX);
inside = inpolygon(GX, GY, Bk(:, 1), Bk(:, 2));
K0 = nan(ny, nx);
for j = 1:ny
    for i = 1:nx
        if inside(j, i)
            d = hypot(Wk(:, 1) - xs(i), Wk(:, 2) - ys(j)) + 1e-6;
            w = 1 ./ d .^ 2;
            K0(j, i) = (w' * Wk(:, 3)) / sum(w);
        end
    end
end
act = find(inside);
[aj, ai] = ind2sub([ny, nx], act);
Nc = numel(act);
idx = zeros(ny, nx);
idx(act) = 1:Nc;
dxm = dx * 1000;
area = dxm ^ 2;
coast = false(ny, nx);
for j = 1:ny
    ii = find(inside(j, :));
    if ~isempty(ii)
        coast(j, ii(1)) = true;
    end
end
K0c = K0(act);

% ---- baseline heads and intruded area ------------------------------------------------------------------------------
M = struct('P', P, 'act', act, 'aj', aj, 'ai', ai, 'idx', idx, 'inside', inside, 'coast', coast, 'ny', ny, ...
           'nx', nx, 'Nc', Nc, 'dxm', dxm, 'K0c', K0c);
[A0, rhs0] = assemble(M, ones(Nc, 1));
h0 = A0 \ rhs0;
baseArea = goalArea(h0, P, area);

% ---- pilot zones, sensitivities and facies prior -------------------------------------------------------------------
[pgx, pgy] = meshgrid(linspace(1, max(xs) - 1, 5), linspace(2, max(ys) - 2, 8));
pil = [pgx(:), pgy(:)];
pil = pil(inpolygon(pil(:, 1), pil(:, 2), Bk(:, 1), Bk(:, 2)), :);
Nz = size(pil, 1);
zone = zeros(Nc, 1);
for k = 1:Nc
    [~, zone(k)] = min(hypot(pil(:, 1) - xs(ai(k)), pil(:, 2) - ys(aj(k))));
end
zK = arrayfun(@(z) mean(K0c(zone == z)), (1:Nz)');
zfac = 1 + (zK <= 150) + (zK <= 80);              % coarse, medium and fine facies
S = zeros(Nc, Nz);
Hg = zeros(1, Nz);
dd = 1e-3;
for z = 1:Nz
    tp = zeros(Nz, 1);
    tp(z) = dd;
    [Ap, rp] = assemble(M, exp(tp(zone)));
    [Am, rm] = assemble(M, exp(-tp(zone)));
    hp = Ap \ rp;
    hm = Am \ rm;
    S(:, z) = (hp - hm) / (2 * dd);
    Hg(z) = (goalArea(hp, P, area) - goalArea(hm, P, area)) / (2 * dd);
end
GamF = zeros(Nz);
for a = 1:Nz
    for b = 1:Nz
        bs = exp(-hypot(pil(a, 1) - pil(b, 1), pil(a, 2) - pil(b, 2)) / 8.0);
        if zfac(a) == zfac(b)
            GamF(a, b) = bs;
        else
            GamF(a, b) = P.rhoF * bs;
        end
    end
end
st = [0.30 0.45 0.60];
sig = st(zfac)';
GamF = (sig * sig') .* GamF + 1e-9 * eye(Nz);

% ---- goal-oriented information field (public function, one cell at a time) -----------------------------------------
EIG_c = zeros(Nc, 1);
for k = 1:Nc
    EIG_c(k) = certaincoast.network.eigOperator(S(k, :), Hg, GamF, P.sn ^ 2);
end

% ---- recharge field of the published pipeline (one adjoint solve) ----------------------------------------------------
s = 0.15;
sigQ = 1 ./ (1 + exp(-(P.hcrit - h0) / s));
wh = area * (-(sigQ .* (1 - sigQ)) / s) / 1e6;
MAR_c = A0' \ wh;
MAR_c(coast(act)) = 0;

monCell = pickTopK(EIG_c, aj, ys, P.Nmon, P.space);
marCell = pickTopK(MAR_c, aj, ys, P.Nmar, P.space);
monID = snap(monCell, ai, aj, xs, ys, Wk, wellID);
marID = snap(marCell, ai, aj, xs, ys, Wk, wellID);

% ---- the public package on the real field ----------------------------------------------------------------------------
wellCell = zeros(numel(wellID), 1);
for q = 1:numel(wellID)
    jj = round(Wk(q, 2) / dx) + 1;
    ii = round(Wk(q, 1) / dx) + 1;
    if jj >= 1 && jj <= ny && ii >= 1 && ii <= nx && idx(jj, ii) > 0
        wellCell(q) = idx(jj, ii);
    end
end
inWells = find(wellCell > 0);
[gSel, gGain] = certaincoast.network.greedyDesign(S(wellCell(inWells), :), Hg, GamF, P.sn ^ 2, P.Nmon);
greedyID = wellID(inWells(gSel));
topGain = certaincoast.network.eigOperator(S(monCell, :), Hg, GamF, P.sn ^ 2 * eye(numel(monCell)));

supCell = zeros(numel(P.supply), 1);
for q = 1:numel(P.supply)
    w = find(strcmp(wellID, P.supply{q}), 1);
    if isempty(w) || wellCell(w) == 0
        error('fk:supply', 'Supply well %s is not an active cell.', P.supply{q});
    end
    supCell(q) = wellCell(w);
end
Ssup = S(supCell, :);
[RISK_c, info] = certaincoast.network.rechargeRisk(A0, supCell, Ssup * GamF * Ssup', h0(supCell), P.hcrit);
RISK_c(coast(act)) = 0;
pragCell = pickTopK(RISK_c, aj, ys, P.Nmar, P.space);
pragID = snap(pragCell, ai, aj, xs, ys, Wk, wellID);

R = struct('P', P, 'xs', xs, 'ys', ys, 'inside', inside, 'act', act, 'Nc', Nc, 'Nz', Nz, 'Bk', Bk, 'Wk', Wk, ...
           'h0', h0, 'baseArea', baseArea, 'EIG_c', EIG_c, 'MAR_c', MAR_c, 'RISK_c', RISK_c, ...
           'monCell', monCell, 'marCell', marCell, 'pragCell', pragCell, 'aj', aj, 'ai', ai, 'GamF', GamF, ...
           'nWellsK', numel(wellID), 'nWellsInside', numel(inWells), 'topGain', topGain, 'greedyGain', gGain, ...
           'supplyP0', info.P0);
R.wellID = wellID;
R.monID = monID;
R.marID = marID;
R.pragID = pragID;
R.greedyID = greedyID;
R.supply = P.supply;
end

% ===================================================================================================================
function [A, rhs] = assemble(M, kfac)
% steady confined flow, transmissivity K * b, recharge R, the coast at h = 0
P = M.P;
Tg = nan(M.ny, M.nx);
Tg(M.act) = M.K0c .* kfac * P.b;
I = zeros(5 * M.Nc, 1);
J = I;
V = I;
rhs = zeros(M.Nc, 1);
p = 0;
nb = [-1 0; 1 0; 0 -1; 0 1];
for k = 1:M.Nc
    j = M.aj(k);
    i = M.ai(k);
    if M.coast(j, i)
        p = p + 1;
        I(p) = k;
        J(p) = k;
        V(p) = 1;
        continue
    end
    dg = 0;
    for q = 1:4
        jj = j + nb(q, 1);
        ii = i + nb(q, 2);
        if jj >= 1 && jj <= M.ny && ii >= 1 && ii <= M.nx && M.inside(jj, ii)
            Tf = 0.5 * (Tg(j, i) + Tg(jj, ii));
            p = p + 1;
            I(p) = k;
            J(p) = M.idx(jj, ii);
            V(p) = Tf;
            dg = dg - Tf;
        end
    end
    p = p + 1;
    I(p) = k;
    J(p) = k;
    V(p) = dg;
    rhs(k) = -P.R * M.dxm ^ 2;
end
A = sparse(I(1:p), J(1:p), V(1:p), M.Nc, M.Nc);
end

function a = goalArea(h, P, area)
a = sum(area * (1 ./ (1 + exp(-(P.hcrit - h) / 0.15)))) / 1e6;     % intruded area, km2 (smooth indicator)
end

function sel = pickTopK(vals, aj, ys, k, spaceN)
v = vals;
v(~isfinite(v)) = -Inf;
[~, ord] = sort(v, 'descend');
sel = [];
used = [];
for q = 1:numel(ord)
    kk = ord(q);
    if ~isfinite(vals(kk))
        continue
    end
    N = ys(aj(kk));
    if ~isempty(used) && any(abs(N - used) < spaceN)
        continue
    end
    sel(end + 1) = kk; %#ok<AGROW>
    used(end + 1) = N; %#ok<AGROW>
    if numel(sel) >= k
        break
    end
end
sel = sel(:);
end

function ID = snap(cells, ai, aj, xs, ys, Wk, wellID)
ID = cell(numel(cells), 1);
for q = 1:numel(cells)
    [~, w] = min(hypot(Wk(:, 1) - xs(ai(cells(q))), Wk(:, 2) - ys(aj(cells(q)))));
    ID{q} = wellID{w};
end
end
