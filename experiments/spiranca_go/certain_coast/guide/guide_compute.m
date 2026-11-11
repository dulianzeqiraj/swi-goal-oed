function guide_compute(ccPath, fkCsvDir, outDir)
%GUIDE_COMPUTE Every computed result behind the figures of the illustrated CERTAIN-COAST guide.
%   guide_compute(CCPATH, FKCSVDIR, OUTDIR) uses the open-source MATLAB package in CCPATH (the certain-coast
%   repository) and the Fushë-Kuqe wells and boundary exported to CSV in FKCSVDIR, and writes MAT files (-v7) to
%   OUTDIR: Henry benchmark fields and toes, toe against freshwater inflow, the goal-oriented information map and
%   designs, warnings between samples, the certified alarm, recharge from heads, the learned inland boundary and the
%   Fushë-Kuqe field model. Runs in MATLAB or GNU Octave (about two minutes in Octave).

%   Copyright 2026 Dulian Zeqiraj.

addpath(ccPath);
addpath(fileparts(mfilename('fullpath')));
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

% ---------------------------------------------------------------- 1. Henry benchmark: fields and grid convergence
P = certaincoast.model.henryParameters();
sizes = [16 8; 32 16; 41 21; 61 31; 81 41];
toes = zeros(size(sizes, 1), 1);
resid = toes;
secs = toes;
for k = 1:size(sizes, 1)
    g = certaincoast.model.henryGrid(sizes(k, 1), sizes(k, 2));
    t0 = tic;
    [U, resid(k)] = certaincoast.model.solveDensity(zeros(g.N, 1), g, P, 1e-12);
    secs(k) = toc(t0);
    toes(k) = certaincoast.model.toePosition(U, g);
end
[c, h, qxc, qyc] = fields(U, g, P);                     % finest grid
xc = g.xc;
yc = g.yc;
save('-v7', fullfile(outDir, 'henry.mat'), 'sizes', 'toes', 'resid', 'secs', 'c', 'h', 'qxc', 'qyc', 'xc', 'yc');
fprintf('Henry: toes %s\n', mat2str(toes', 5));

% ---------------------------------------------------------------- 2. toe against the freshwater inflow
qf = 0.6:0.1:1.4;
toeQ = zeros(size(qf));
g = certaincoast.model.henryGrid(41, 21);
cQ = zeros(g.Ny, g.Nx, 3);
for k = 1:numel(qf)
    Pk = P;
    Pk.Q = qf(k) * P.Q;
    U = certaincoast.model.solveDensity(zeros(g.N, 1), g, Pk, 1e-12);
    toeQ(k) = certaincoast.model.toePosition(U, g);
    j = find(abs(qf(k) - [0.6 1.0 1.4]) < 1e-9);
    if ~isempty(j)
        cQ(:, :, j) = reshape(U(g.N + 1:end), g.Nx, g.Ny).';
    end
end
xQ = g.xc;
yQ = g.yc;
save('-v7', fullfile(outDir, 'henry_inflow.mat'), 'qf', 'toeQ', 'cQ', 'xQ', 'yQ');
fprintf('toe against inflow: %s\n', mat2str(toeQ, 4));

% ---------------------------------------------------------------- 3. where a salinity sensor tells most about the toe
rng(31);
g = certaincoast.model.henryGrid(32, 16);
theta = zeros(g.N, 1);
U = certaincoast.model.solveDensity(theta, g, P, 1e-12);
[J, ~, Jt] = certaincoast.model.densityJacobian(U, theta, g, P);
[X, Y] = ndgrid(g.xc, g.yc);
X = X(:);
Y = Y(:);
zone = find(X > 1.0 & X < 1.6 & Y < 0.25);
dOdu = sparse(1:g.N, g.N + (1:g.N), 1, g.N, 2 * g.N);
dqdu = zeros(1, 2 * g.N);
dqdu(g.N + zone) = g.dx * g.dy;
[G, H] = certaincoast.network.adjointSensitivities(J, Jt, dOdu, dqdu);
D = sqrt(bsxfun(@minus, X, X.') .^ 2 + bsxfun(@minus, Y, Y.') .^ 2);
Gam = 0.25 * exp(-D / 0.4);
noise = 0.02 ^ 2;
eigMap = zeros(g.N, 1);
for k = 1:g.N
    eigMap(k) = certaincoast.network.eigOperator(G(k, :), H, Gam, noise);
end
[S, gain, steps] = certaincoast.network.greedyDesign(G, H, Gam, noise, 6);
greedyCurve = [steps.gain];
nRand = 300;
randGains = zeros(nRand, 6);
for k = 1:6
    for r = 1:nRand
        T = randperm(g.N, k);
        randGains(r, k) = certaincoast.network.eigOperator(G(T, :), H, Gam, noise * eye(k));
    end
end
cS = reshape(U(g.N + 1:end), g.Nx, g.Ny).';
eigMap = reshape(eigMap, g.Nx, g.Ny).';
xS = g.xc;
yS = g.yc;
zoneX = [1.0 1.6];
zoneY = [0 0.25];
sx = X(S);
sy = Y(S);
save('-v7', fullfile(outDir, 'sensors_henry.mat'), 'eigMap', 'cS', 'xS', 'yS', 'S', 'sx', 'sy', 'gain', ...
     'greedyCurve', 'randGains', 'zoneX', 'zoneY');
fprintf('sensors: greedy %s nats\n', mat2str(greedyCurve, 3));

% ---------------------------------------------------------------- 4. warnings between samples
rng(3);
z = (250 - 180) / 35;
kGrid = exp(linspace(log(1 / 400), log(4), 41));
curve = certaincoast.betweensamples.crossingProbability(kGrid, z, 120, 0.25, 8000);
truthP = interp1(log(kGrid), curve, log(1 / 8));
steps_ = [91 30 7 1];
nRec = 40;
bandLo = zeros(nRec, 4);
bandHi = bandLo;
for d = 1:4
    for r = 1:nRec
        t = certaincoast.betweensamples.sampleTimes(8 * 365, steps_(d));
        x = certaincoast.betweensamples.ouAtTimes(t, 1 / 8);
        [~, kLo, kHi] = certaincoast.betweensamples.timeScaleInterval(t, x, kGrid);
        [bandLo(r, d), bandHi(r, d)] = certaincoast.betweensamples.crossingBand(kLo, kHi, kGrid, curve);
    end
end
rng(8);
pathT = (0:0.25:365).';
pathX = certaincoast.betweensamples.ouPaths(1 / 8, 1, numel(pathT) - 1, 0.25).';
tau = logspace(log10(0.25), log10(365), 200);
info = certaincoast.betweensamples.pairInformation(1 / 8, tau) * (1 / 8) ^ 2;
save('-v7', fullfile(outDir, 'between.mat'), 'kGrid', 'curve', 'truthP', 'steps_', 'bandLo', 'bandHi', 'pathT', ...
     'pathX', 'z', 'tau', 'info');
fprintf('between samples: truth %.3f, median bands %s %s\n', truthP, mat2str(median(bandLo), 2), ...
        mat2str(median(bandHi), 2));

% ---------------------------------------------------------------- 5. the certified alarm
rng(1);
n = 1200;
tA = (1:n).';
truthA = 180 + 60 * sin(linspace(0, 12 * pi, n)).' + 15 * randn(n, 1);
forecastA = truthA + 20 * randn(n, 1);
margin = certaincoast.alarms.conformalMargin(truthA(1:600) - forecastA(1:600), 0.10);
alarmA = certaincoast.alarms.issueAlarm(forecastA, 250, margin);
events = truthA >= 250;
live = (601:n).';
nEvents = sum(events(live));
nMiss = sum(events(live) & ~alarmA(live));
nFalse = sum(~events(live) & alarmA(live));
bound = certaincoast.alarms.missRateUpperBound(nMiss, nEvents);
evGrid = 0:200;
cp0 = arrayfun(@(e) certaincoast.alarms.missRateUpperBound(0, e), evGrid);
cp10 = arrayfun(@(e) certaincoast.alarms.missRateUpperBound(round(0.1 * e), e), evGrid);
save('-v7', fullfile(outDir, 'alarm.mat'), 'tA', 'truthA', 'forecastA', 'margin', 'alarmA', 'events', 'nEvents', ...
     'nMiss', 'nFalse', 'bound', 'evGrid', 'cp0', 'cp10');
fprintf('alarm: margin %.1f, events %d, missed %d, false %d, bound %.3f\n', margin, nEvents, nMiss, nFalse, bound);

% ---------------------------------------------------------------- 6. recharge from the heads of a well
rng(11);
par = struct('m', 1.12, 'k_et', 0.9, 'Ic', 30, 'theta_fc', 150, 'tau_s', 8, 'phi0', 0.25, 'Sy', 0.2, ...
             'tau_a', 150, 'h_b', 0.8, 'h_0', 1.4);
N = 1096;
[Pr, PET] = certaincoast.recharge.syntheticClimate(N);
o = certaincoast.recharge.soilWaterBalance(par, Pr / par.m, PET);
hObs = o.h + 0.01 * randn(N, 1);
Rhat = certaincoast.recharge.rechargeFromHeads(hObs, par.Sy, par.tau_a, par.h_b, par.h_0);
Rtrue = o.R;
hTrue = o.h;
save('-v7', fullfile(outDir, 'recharge.mat'), 'Pr', 'PET', 'hObs', 'hTrue', 'Rhat', 'Rtrue');

% ---------------------------------------------------------------- 7. the learned inland boundary
rng(7);
p = certaincoast.boundary.aquifer();
A = certaincoast.boundary.conductanceMatrix(p.nFull, p, true);
f = zeros(p.nFull, 1);
f(1:p.nModel) = p.R0 * p.dx;
f(p.well) = f(p.well) - p.Q0;
hs = A \ f;
Href = hs(p.boundaryCell);
h0 = hs(1:p.nModel);
bc = p.boundaryCell;
nd = round(20 * 365.25);
[~, r, Q] = certaincoast.boundary.forcing(p, nd, 'broadband');
full = certaincoast.boundary.simulateFull(p, r, Q);
o1 = full(:, p.bandCells(1)) + 0.002 * randn(nd, 1);
o2 = full(:, p.bandCells(2)) + 0.002 * randn(nd, 1);
[Ci, wi, mui] = certaincoast.boundary.identifyFromPiezometers(p, o1, o2, r, Href);
[Cx, wx, mux] = certaincoast.boundary.exactExterior(p);
[tp, rp, Qp] = certaincoast.boundary.forcing(p, round(10 * 365.25), 'seasonal', [3 * 365.25, 8 * 365.25, 0.3], ...
                                             [2 * 365.25, Inf, 1.2]);
ref = certaincoast.boundary.simulateFull(p, rp, Qp);
hL = certaincoast.boundary.simulateTruncated(p, rp, Qp, Ci, wi, mui, Href, h0);
hN = certaincoast.boundary.simulateTruncated(p, rp, Qp, 0, 0, 1, Href, h0);
hF = certaincoast.boundary.simulateTruncated(p, rp, Qp, p.c, 0, 1, Href, h0);
bRef = ref(:, bc);
bL = hL(:, bc);
bN = hN(:, bc);
bF = hF(:, bc);
om = logspace(log10(2 * pi / (200 * 365.25)), log10(2 * pi / 2.5), 300).';
Zx = abs(certaincoast.boundary.impedance(1i * om, Cx, wx, mux));
Zl = abs(certaincoast.boundary.impedance(1i * om, Ci, wi, mui));
nComp = numel(mux);
save('-v7', fullfile(outDir, 'boundary.mat'), 'tp', 'rp', 'Qp', 'bRef', 'bL', 'bN', 'bF', 'om', 'Zx', 'Zl', 'nComp');
fprintf('boundary: rms learned %.4f, no flow %.4f, fixed %.4f m\n', sqrt(mean((bL - bRef) .^ 2)), ...
        sqrt(mean((bN - bRef) .^ 2)), sqrt(mean((bF - bRef) .^ 2)));

% ---------------------------------------------------------------- 8. the Fushë-Kuqe field model (published design)
Rf = fk_field_model(fkCsvDir);
nyF = numel(Rf.ys);
nxF = numel(Rf.xs);
hMap = nan(nyF, nxF);
hMap(Rf.act) = Rf.h0;
eMap = nan(nyF, nxF);
eMap(Rf.act) = Rf.EIG_c;
xsF = Rf.xs;
ysF = Rf.ys;
Bk = Rf.Bk;
Wk = Rf.Wk;
wellID = Rf.wellID;
monID = Rf.monID;
marID = Rf.marID;
baseArea = Rf.baseArea;
nCells = Rf.Nc;
topGain = Rf.topGain;
greedyGain = Rf.greedyGain;
greedyID = Rf.greedyID;
save('-v7', fullfile(outDir, 'fushe_kuqe.mat'), 'hMap', 'eMap', 'xsF', 'ysF', 'Bk', 'Wk', 'wellID', 'monID', ...
     'marID', 'baseArea', 'nCells', 'topGain', 'greedyGain', 'greedyID');
fprintf('Fushë-Kuqe: %d cells, intruded area %.1f km2, monitoring %s, MAR %s\n', nCells, baseArea, ...
        strjoin(monID', ' '), strjoin(marID', ' '));

% ---------------------------------------------------------------- 9. does the alarm keep its stated miss rate?
rng(21);
alphas = [0.05 0.10 0.20 0.30];
nCal = 100;
nRep = 4000;
missRate = zeros(nRep, numel(alphas));
for j = 1:numel(alphas)
    for r = 1:nRep
        res = exp(0.8 * randn(nCal + 2000, 1));          % skewed (lognormal) forecast errors
        m = certaincoast.alarms.conformalMargin(res(1:nCal), alphas(j));
        missRate(r, j) = mean(res(nCal + 1:end) > m);
    end
end
save('-v7', fullfile(outDir, 'alarm_reliability.mat'), 'alphas', 'missRate', 'nCal', 'nRep');
fprintf('alarm reliability: mean miss rates %s\n', mat2str(mean(missRate), 3));

% ---------------------------------------------------------------- 10. heads alone do not fix the amount of recharge
rng(11);
[Pr, PET] = certaincoast.recharge.syntheticClimate(1096);
o1 = certaincoast.recharge.soilWaterBalance(par, Pr / par.m, PET);
q = par;
names = {'m', 'k_et', 'Ic', 'theta_fc', 'Sy'};
for i = 1:numel(names)
    q.(names{i}) = 1.5 * q.(names{i});
end
o2 = certaincoast.recharge.soilWaterBalance(q, Pr / par.m, PET);
h1 = o1.h;
h2 = o2.h;
cum1 = cumsum(o1.R);
cum2 = cumsum(o2.R);
maxdh = max(abs(h2 - h1));
save('-v7', fullfile(outDir, 'equifinality.mat'), 'h1', 'h2', 'cum1', 'cum2', 'maxdh');
fprintf('equifinality: max head difference %.1e m, recharge %.0f vs %.0f mm\n', maxdh, cum1(end), cum2(end));
end

function [c, h, qxc, qyc] = fields(U, g, P)
% salinity, head and Darcy velocity at the cell centres (uniform conductivity)
Nx = g.Nx;
Ny = g.Ny;
h = reshape(U(1:g.N), Nx, Ny).';
c = reshape(U(g.N + 1:end), Nx, Ny).';
K = P.Kref;
qx = zeros(Ny, Nx + 1);
qy = zeros(Ny + 1, Nx);
qx(:, 2:Nx) = -K * diff(h, 1, 2) / g.dx;
qy(2:Ny, :) = -K * (diff(h, 1, 1) / g.dy + P.eps * 0.5 * (c(1:Ny - 1, :) + c(2:Ny, :)));
qx(:, 1) = P.Q;
qx(:, Nx + 1) = -K * (P.eps * (g.Ly - g.yc(:)) - h(:, Nx)) / (0.5 * g.dx);
qxc = 0.5 * (qx(:, 1:Nx) + qx(:, 2:Nx + 1));
qyc = 0.5 * (qy(1:Ny, :) + qy(2:Ny + 1, :));
end
