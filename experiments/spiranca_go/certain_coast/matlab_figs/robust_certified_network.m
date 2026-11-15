function R = robust_certified_network(repoRoot, outDir)
%ROBUST_CERTIFIED_NETWORK Robust, certified placement of the salinity sensors of CERTAIN-COAST when sensors interfere.
%   robust_certified_network() recomputes the test case of examples/example_network.m of CERTAIN-COAST (Henry section of
%   16 x 8 cells, uncertain log-conductivity field with standard deviation 0.5 and correlation length 0.4 m, 12
%   candidate salinity sensors on 4 columns x 3 depths, sensor noise 0.02^2; goals: the salt mass near the toe and the
%   question "is the supply cell above its limit?") and puts robust optimal experimental design (Wald max-min of ROED,
%   Chowdhary, Attia & Alexanderian, arXiv:2409.09137, SIAM J. Sci. Comput. 2026) and the Certified OED framework
%   (relaxation on the capped simplex, Frank-Wolfe certificate, noise-inflation relaxation for correlated noise) into
%   the objective function and the optimal placement of the sensors:
%
%     noise      Gamma_n(theta) = sigma^2 I + a^2 B B' + s_m^2 C_ell        (common error of each data-logger hub,
%                                                                           model error correlated over distance)
%     channels   one sealed reference channel per hub (zero sensitivity to the aquifer, reads the hub error)
%     objective  J(S, R) = min over theta = (a, ell) in the box of EIG_goal(S, R; theta)   (eigOperator, exact)
%     designs    nominal (interference ignored), robust exhaustive optimum, robust optimum with a reference channel
%     bound      certified upper bound on max J without enumeration of the designs (noise-inflation relaxation on
%                the capped simplex per scenario and max-min dual, interference-free ceiling, full network), certified
%                gap, robust greedy + exchange against exhaustive search for 3 to 6 sensors
%     checks     direct Gaussian conditioning, Monte Carlo, the nominal results of example_network for a = s_m = 0
%
%   The figure fig7_robust_network (16 cm wide; PNG at 300 dpi and vector PDF; palette and font scale fs() of
%   run_all_figures.m), the log robust_certified_network_log.txt with every number and the short results file
%   robust_certified_network_results.json are written to OUTDIR.
%   robust_certified_network(REPOROOT, OUTDIR) uses the given repository and output folders; without them the
%   defaults of run_all_figures.m apply (CERTAINCOAST_ROOT, then the local clone; the folder 'figures' next to this
%   file). R = robust_certified_network(...) also returns the results structure.
%
%   GNU Octave on a machine without a display:
%       xvfb-run -a octave --no-gui --eval "robust_certified_network"
%   The designs use no random numbers; the Monte Carlo checks use fixed seeds (the random streams of MATLAB and GNU
%   Octave differ, so the Monte Carlo digits differ slightly between the two programs).
%
%   The yes/no information is the integral of thresholdGoalEig; its 24-node Gauss-Hermite rule under-resolves the
%   integrand when the data explain more than about 90% of the variance of the supply salinity, so the values in
%   nats are computed with an accurate quadrature of the same integral (phiAccurate), checked by Monte Carlo, and the
%   values of thresholdGoalEig are logged beside them. Both increase with the explained variance, so the designs agree.
%
%   Synthetic data only, as in the example. Copyright 2026 Dulian Zeqiraj. Licensed under the Apache License 2.0.

if nargin < 1 || isempty(repoRoot)
    repoRoot = getenv('CERTAINCOAST_ROOT');
    if isempty(repoRoot)
        repoRoot = '/home/user/dulianzeqiraj/certain-coast';
    end
end
if nargin < 2 || isempty(outDir)
    outDir = fullfile(fileparts(mfilename('fullpath')), 'figures');
end
if ~exist(fullfile(repoRoot, '+certaincoast'), 'dir')
    error('robust_certified_network:repo', 'CERTAIN-COAST not found in %s: pass its folder as the first argument.', ...
          repoRoot);
end
addpath(repoRoot);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end
isOctave = exist('OCTAVE_VERSION', 'builtin') ~= 0;
if isOctave
    warning('off', 'Octave:print:figure-too-large');
    if any(strcmp(available_graphics_toolkits(), 'qt'))
        graphics_toolkit('qt');
    end
    program = sprintf('GNU Octave %s (graphics toolkit %s)', version(), graphics_toolkit());
else
    program = sprintf('MATLAB %s', version());
end
lg = fopen(fullfile(outDir, 'robust_certified_network_log.txt'), 'w');
tStart = tic;
say(lg, 'ROBUST, CERTIFIED PLACEMENT OF THE SALINITY SENSORS (ROED + Certified OED) on examples/example_network.m\n');
say(lg, 'CERTAIN-COAST %s from %s\n%s, %s\n', certaincoast.version(), repoRoot, program, datestr(now, 31));
say(lg, 'Package functions used: model.henryGrid, model.henryParameters, model.solveDensity, model.densityJacobian,\n');
say(lg, '  network.adjointSensitivities, network.eigOperator, network.greedyDesign, network.thresholdGoalEig,\n');
say(lg, '  network.exactGoalEig (Monte Carlo check). The package is read only; nothing in it is changed.\n');

% ==================================================================================================================
% 0. The test case of examples/example_network.m (same calls, same arguments)
% ==================================================================================================================
g = certaincoast.model.henryGrid(16, 8);
P = certaincoast.model.henryParameters();
theta = zeros(g.N, 1);
U = certaincoast.model.solveDensity(theta, g, P, 1e-12);
[J, ~, Jtheta] = certaincoast.model.densityJacobian(U, theta, g, P);
[X, Y] = ndgrid(g.xc, g.yc);
X = X(:);
Y = Y(:);
cellAt = @(x, y) find(abs(X - x) < g.dx / 2 & abs(Y - y) < g.dy / 2);
colX = [0.5625 1.0625 1.4375 1.8125];
depY = [0.0625 0.4375 0.8125];
cand = zeros(12, 1);
k = 0;
for x = colX
    for y = depY
        k = k + 1;
        cand(k) = cellAt(x, y);
    end
end
supply = cellAt(1.5625, 0.3125);
zone = find(X > 1.0 & X < 1.6 & Y < 0.25);
dOdu = sparse(1:12, g.N + cand, 1, 12, 2 * g.N);
dqdu = [zeros(1, g.N), zeros(1, g.N)];
dqdu(g.N + zone) = g.dx * g.dy;
dsdu = sparse(1, g.N + supply, 1, 1, 2 * g.N);
[G, H] = certaincoast.network.adjointSensitivities(J, Jtheta, [dOdu; dsdu], dqdu);
Hs = G(13, :);
G = G(1:12, :);
D = sqrt(bsxfun(@minus, X, X.') .^ 2 + bsxfun(@minus, Y, Y.') .^ 2);
Gam = 0.25 * exp(-D / 0.4);
sigma = 0.02;
noise = sigma ^ 2;
Sigma = [G; -Hs] * Gam * [G; -Hs].';
sdS = sqrt(Sigma(13, 13));
limit = U(g.N + supply) + 0.3 * sdS;
muS = -U(g.N + supply);                          % thresholdGoalEig works with -salinity (event: -s < -limit)
p0 = 0.5 * erfc(0.3 / sqrt(2));
xc = X(cand);
yc = Y(cand);

say(lg, '\n=== 0. Test case (examples/example_network.m)\n');
say(lg, 'Henry section %d x %d cells (%.2f x %.2f m); %d log-conductivity parameters, prior 0.25 exp(-d/0.4)\n', ...
    g.Nx, g.Ny, g.Lx, g.Ly, g.N);
say(lg, '12 candidate salinity sensors (relative salinity, sea water = 1), noise sigma = %.3f:\n', sigma);
for j = 1:12
    say(lg, '  sensor %2d  x = %.4f m  y = %.4f m  prior sd of the reading %.4f\n', j, xc(j), yc(j), ...
        sqrt(G(j, :) * Gam * G(j, :).'));
end
say(lg, 'goal 1: salt mass in the toe zone (%d cells), prior sd %.5f; goal 2: supply cell (x = %.4f, y = %.4f),\n', ...
    numel(zone), sqrt(H * Gam * H.'), X(supply), Y(supply));
say(lg, '  salinity %.4f, prior sd %.4f, limit %.4f (= salinity + 0.3 sd), prior probability above it %.4f\n', ...
    U(g.N + supply), sdS, limit, p0);

% ---------------------------------------------------------------- 0b. the nominal results of example_network
[Sg, gainG] = certaincoast.network.greedyDesign(G, H, Gam, noise, 3);
combs3 = nchoosek(1:12, 3);
gains = zeros(size(combs3, 1), 1);
risks = zeros(size(combs3, 1), 1);
for c = 1:size(combs3, 1)
    gains(c) = certaincoast.network.eigOperator(G(combs3(c, :), :), H, Gam, noise * eye(3));
    risks(c) = certaincoast.network.thresholdGoalEig(Sigma, muS, combs3(c, :), noise, 13, -limit);
end
[bestNom, ib] = max(gains);
[bestRiskNom, ir] = max(risks);
nomMass = combs3(ib, :);
nomSupply = combs3(ir, :);
say(lg, 'Nominal model (independent noise 0.02^2, as in example_network):\n');
say(lg, '  salt mass: greedyDesign %s gives %.4f nats; exhaustive optimum %s %.4f nats; median design %.4f\n', ...
    mat2str(sort(Sg)), gainG, mat2str(nomMass), bestNom, median(gains));
say(lg, '  supply cell above its limit: exhaustive optimum (thresholdGoalEig) %s %.4f nats; the salt-mass design %s %.4f\n', ...
    mat2str(nomSupply), bestRiskNom, mat2str(nomMass), risks(ib));
r2Nom = zeros(1, 2);
for q = 1:2
    Sd = ternary(q == 1, nomSupply, nomMass);
    Sy = Sigma(Sd, Sd) + noise * eye(3);
    r2Nom(q) = Sigma(13, Sd) * (Sy \ Sigma(Sd, 13)) / Sigma(13, 13);
end
aStd = (-limit - muS) / sdS;
say(lg, '  accurate quadrature of the same integral (see section 2): %s %.4f nats (r2_s = %.6f), %s %.4f nats\n', ...
    mat2str(nomSupply), phiAccurate(r2Nom(1), aStd), r2Nom(1), mat2str(nomMass), phiAccurate(r2Nom(2), aStd));
say(lg, '  (r2_s = %.6f), i.e. %.1f%% of the optimum; thresholdGoalEig gives %.1f%%. Same designs, other values.\n', ...
    r2Nom(2), 100 * phiAccurate(r2Nom(2), aStd) / phiAccurate(r2Nom(1), aStd), 100 * risks(ib) / bestRiskNom);

% ==================================================================================================================
% 1. Interference-aware noise model of the 12 candidates and the 4 reference channels
% ==================================================================================================================
hub = ceil((1:12).' / 3);                        % hub h serves the sensors of column h (3 depths)
B = double(bsxfun(@eq, hub, 1:4));               % 12 x 4 hub loadings
Dc = sqrt(bsxfun(@minus, xc, xc.') .^ 2 + bsxfun(@minus, yc, yc.') .^ 2);
sigR = 0.005;                                    % noise of a sealed reference channel
sm = 0.02;                                       % amplitude of the model error (fixed)
aBox = [0.01 0.03];                              % hub error amplitude a
ellBox = [0.1 2.0];                              % correlation length ell of the model error (m)
th0 = [0.02, sqrt(ellBox(1) * ellBox(2))];       % nominal theta: middle of the box (geometric middle in ell)
Lh = [B; eye(4)];                                % hub-error loadings of the 12 sensors and the 4 reference channels
gamJ = @(a, ell, smv) blkdiag(sigma ^ 2 * eye(12) + smv ^ 2 * exp(-Dc / ell), sigR ^ 2 * eye(4)) + a ^ 2 * (Lh * Lh.');
gamE = @(ell) sigma ^ 2 * eye(12) + sm ^ 2 * exp(-Dc / ell);   % non-correctable part (interference-free ceiling)
Gaug = [G; zeros(4, g.N)];                       % rows of the reference channels: zero sensitivity to the aquifer
Kj = Gaug * Gam * Gaug.';                        % 16 x 16 prior covariance of the noise-free channel readings
Zj = Gaug * Gam * [H; -Hs].';                    % 16 x 2 covariance of the channels with salt mass and -salinity
s2 = [H * Gam * H.', Hs * Gam * Hs.'];           % prior variances of the two goal variables
R0s = {[], 13, 14, 15, 16};                      % reference sets within the budget: none, or the channel of one hub
R0names = {'none', 'r1', 'r2', 'r3', 'r4'};

say(lg, '\n=== 1. Noise model of the candidates (all values in relative salinity, sea water = 1)\n');
say(lg, 'Gamma_n(theta) = sigma^2 I + a^2 B B'' + s_m^2 C_ell, (C_ell)_ij = exp(-|x_i - x_j| / ell), theta = (a, ell)\n');
say(lg, '  sigma = %.3f   independent sensor noise (2%% of sea-water salinity, as in example_network)\n', sigma);
say(lg, '  a in [%.3f, %.3f]   common error of each data-logger hub (logger drift / shared calibration between\n', ...
    aBox(1), aBox(2));
say(lg, '                    recalibrations: 1-3%% of sea-water salinity, 0.5-1.5 times the sensor noise)\n');
say(lg, '  B   12 x 4 hub loadings: hub h = column h of candidates (hub 1: sensors 1-3 at x = %.4f m, hub 2: 4-6 at\n', ...
    colX(1));
say(lg, '      x = %.4f, hub 3: 7-9 at x = %.4f, hub 4: 10-12 at x = %.4f m)\n', colX(2), colX(3), colX(4));
say(lg, '  s_m = %.3f fixed   model error (structural error of the section model at the sensors, equal to sigma)\n', sm);
say(lg, '  ell in [%.2f, %.2f] m   from one cell (nearly independent at the sensor spacing of 0.375-0.5 m) to the\n', ...
    ellBox(1), ellBox(2));
say(lg, '                    length of the section (one common pattern)\n');
say(lg, '  nominal theta0 = (a, ell) = (%.3f, %.4f m), the middle of the box (geometric middle in ell)\n', th0(1), th0(2));
say(lg, 'Reference channels r1-r4 (candidates 13-16): one sealed channel per hub (a conductivity cell in a sealed\n');
say(lg, '  standard on the logger): zero sensitivity to the aquifer (rows [G_S; 0]), reads the hub error c_h with\n');
say(lg, '  noise sigma_r = %.3f; its noise is correlated with the sensors of its hub through a^2 B. Joint covariance\n', sigR);
say(lg, '  Gamma_joint = blkdiag(sigma^2 I_12 + s_m^2 C_ell, sigma_r^2 I_4) + a^2 [B; I_4] [B; I_4]''\n');
say(lg, 'Budget: 3 salinity sensors (piezometers) and at most 1 reference channel (a sealed cell on an existing\n');
say(lg, '  logger, a small fraction of the cost of a sensor); budgets of 3-6 sensors for the certificate.\n');

% exact information: eigOperator with the augmented rows and the joint covariance; the loops below use the same
% formula in data space (K = G Gam G', z = G Gam h'), checked against eigOperator on all 1100 configurations
eigExact = @(T, Gn, goal) certaincoast.network.eigOperator(Gaug(T, :), goalRow(goal, H, Hs), Gam, Gn(T, T));
thrExact = @(T, Gn) certaincoast.network.thresholdGoalEig([Kj + Gn, Zj(:, 2); Zj(:, 2).', s2(2)], muS, T, 0, 17, ...
                                                          -limit);
phiPkg = @(r2) certaincoast.network.thresholdGoalEig(s2(2) * [1, sqrt(r2); sqrt(r2), 1], muS, 1, 0, 2, -limit);
phiT = @(r2) phiAccurate(r2, (-limit - muS) / sqrt(s2(2)));
eigFromR2 = @(r2) -0.5 * log(max(1 - r2, eps));

% ==================================================================================================================
% 2. Objective function, checks of the data-space formula and of the threshold function with correlated noise
% ==================================================================================================================
say(lg, '\n=== 2. Objective function\n');
say(lg, 'For sensors S (rows G_S) and reference channels R (rows 0), T = S u R, data y_T = [G_S; 0] m + e_T,\n');
say(lg, 'e_T ~ N(0, Gamma_joint(theta)_TT); the goal-oriented expected information gain (eigOperator, exact):\n');
say(lg, '  EIG_goal(S, R; theta) = -1/2 log(1 - r2),  r2 = z_T'' (K_TT + Gamma_TT(theta))^-1 z_T / sigma_q^2,\n');
say(lg, '  K = [G; 0] Gam [G; 0]'', z = [G; 0] Gam h'', sigma_q^2 = h Gam h'' (h = goal row)\n');
say(lg, 'Robust objective (Wald max-min of ROED):  J(S, R) = min_{theta in Theta} EIG_goal(S, R; theta),\n');
say(lg, '  Theta = [%.2f, %.2f] x [%.2f, %.2f] m;  design problem  max_{|S| = k, |R| <= 1} J(S, R).\n', aBox, ellBox);
say(lg, 'Supply cell: I(1{s > limit}; y_T) = thresholdGoalEig(Sigma_theta, -s0, T, 0, 17, -limit) with\n');
say(lg, '  Sigma_theta = [K + Gamma_joint(theta), -z_s; -z_s'', sigma_s^2]: the correlated noise is placed in the\n');
say(lg, '  covariance of the readings and NOISEVAR = 0. This is exact, because thresholdGoalEig uses the readings only\n');
say(lg, '  through Sigma(design, design) + NOISEVAR I and Sigma(goal, design); so the threshold function applies.\n');
say(lg, '  It depends on the design only through r2_s (explained fraction of the variance of the supply salinity) and is\n');
say(lg, '  increasing in it (Gaussian channels of higher r2_s are Blackwell-better), so J_supply = phi_t(min_theta r2_s)\n');
say(lg, '  and the robust design for the yes/no question is the robust design for the Gaussian supply-salinity goal.\n');

ells = exp(linspace(log(ellBox(1)), log(ellBox(2)), 41));
aGrid = linspace(aBox(1), aBox(2), 5);
% check: data-space formula = eigOperator for all 220 x 5 configurations of 3 sensors, at a_hi and theta0's ell
Gchk = gamJ(aBox(2), th0(2), sm);
Achk = Kj + Gchk;
errOp = 0;
errOpS = 0;
for c = 1:size(combs3, 1)
    for r = 1:5
        T = [combs3(c, :), R0s{r}];
        zt = Zj(T, :);
        q = diag(zt.' * (Achk(T, T) \ zt)).' ./ s2;
        errOp = max(errOp, abs(eigFromR2(q(1)) - eigExact(T, Gchk, 1)));
        errOpS = max(errOpS, abs(eigFromR2(q(2)) - eigExact(T, Gchk, 2)));
    end
end
say(lg, 'Check: data-space formula against eigOperator on all 1100 configurations (3 sensors, 0/1 reference) at\n');
say(lg, '  theta = (%.3f, %.4f): max difference %.2e nats (salt mass), %.2e nats (supply salinity)\n', aBox(2), th0(2), ...
    errOp, errOpS);
% check: the folded threshold call equals the original one when a = s_m = 0
G00 = gamJ(0, th0(2), 0);
errThr = 0;
for c = 1:size(combs3, 1)
    errThr = max(errThr, abs(thrExact(combs3(c, :), G00) - risks(c)));
end
r2grid = linspace(0, 0.999, 1000);
phiGrid = arrayfun(phiPkg, r2grid);
phiGridA = arrayfun(phiT, r2grid);
say(lg, 'Check: thresholdGoalEig with the noise folded into Sigma (NOISEVAR = 0), a = s_m = 0, against the original\n');
say(lg, '  call of example_network on all 220 designs: max difference %.2e nats\n', errThr);
say(lg, 'Check: phi_t(r2) (yes/no information at explained fraction r2) is increasing on [0, 0.999] (1000 points):\n');
say(lg, '  thresholdGoalEig %d, accurate quadrature %d; entropy of the prior event %.4f nats (the most data can give)\n', ...
    all(diff(phiGrid) > 0), all(diff(phiGridA) > 0), -(p0 * log(p0) + (1 - p0) * log(1 - p0)));
say(lg, 'Accuracy of thresholdGoalEig (24 Gauss-Hermite nodes): when r2 -> 1 the integrand H(Phi((a - r x)/sqrt(1 - r2)))\n');
say(lg, '  is a peak of width sqrt(1 - r2)/r in x, narrower than the node spacing. The same integral after the change of\n');
say(lg, '  variable u = (a - r x)/sqrt(1 - r2), 28001-point rule on u in [-14, 14] (phiAccurate):\n');
for r2v = [0.6 0.8 0.9 0.95 0.97 0.98 0.99 0.999]
    say(lg, '    r2 = %.3f: thresholdGoalEig %.4f nats, accurate %.4f nats\n', r2v, phiPkg(r2v), phiT(r2v));
end
say(lg, '  The values in nats of the yes/no question below are accurate ones (Monte Carlo check in section 6);\n');
say(lg, '  thresholdGoalEig is logged beside them. Designs are the same with both (both increase with r2).\n');

% ==================================================================================================================
% 3. N3: the worst amplitude is the upper end; the correlation length is searched on a grid
% ==================================================================================================================
say(lg, '\n=== 3. Worst case over the box (Proposition N3)\n');
say(lg, 'd Gamma_joint / da = 2a [B; I][B; I]'' >= 0 and (K + Gamma)^-1 decreases in the Loewner order, so r2 and\n');
say(lg, '  EIG_goal are non-increasing in a: the worst amplitude is the upper end a = %.3f. ell is searched on a grid of\n', ...
    aBox(2));
say(lg, '  %d log-spaced values in [%.2f, %.2f] m, refined by fminbnd around the grid minimum for reported designs.\n', ...
    numel(ells), ellBox);
A3 = zeros(16, 16, numel(aGrid), numel(ells));
for ia = 1:numel(aGrid)
    for il = 1:numel(ells)
        A3(:, :, ia, il) = Kj + gamJ(aGrid(ia), ells(il), sm);
    end
end
V3 = zeros(size(combs3, 1), 5, numel(aGrid), numel(ells), 2);
for ia = 1:numel(aGrid)
    for il = 1:numel(ells)
        A = A3(:, :, ia, il);
        for r = 1:5
            for c = 1:size(combs3, 1)
                T = [combs3(c, :), R0s{r}];
                zt = Zj(T, :);
                V3(c, r, ia, il, :) = reshape(sum(zt .* (A(T, T) \ zt), 1) ./ s2, [1 1 1 1 2]);
            end
        end
    end
end
dA = diff(V3, 1, 3);
monoA = max(dA(:));
nWorstUpper = 0;
nWorstLoEll = 0;
nWorstHiEll = 0;
for gl = 1:2
    for r = 1:5
        for c = 1:size(combs3, 1)
            M = squeeze(V3(c, r, :, :, gl));
            [~, idx] = min(M(:));
            [iaW, ilW] = ind2sub(size(M), idx);
            nWorstUpper = nWorstUpper + (iaW == numel(aGrid));
            nWorstLoEll = nWorstLoEll + (ilW == 1);
            nWorstHiEll = nWorstHiEll + (ilW == numel(ells));
        end
    end
end
nCfg = 2 * 5 * size(combs3, 1);
say(lg, 'Numerical check on the grid a = %s x %d values of ell, all %d configurations x 2 goals:\n', ...
    mat2str(aGrid, 3), numel(ells), nCfg / 2);
say(lg, '  largest increase of r2 with a: %.2e (non-positive = non-increasing); worst point at the upper end of a\n', ...
    monoA);
say(lg, '  for %d of %d (configuration, goal) pairs; worst ell at the lower end for %d, at the upper end for %d,\n', ...
    nWorstUpper, nCfg, nWorstLoEll, nWorstHiEll);
say(lg, '  in the interior for %d: the worst correlation length depends on the design, as in ROED.\n', ...
    nCfg - nWorstLoEll - nWorstHiEll);

% robust values for budgets 3-6 at a = a_hi on the ell grid (exhaustive)
Ahi = squeeze(A3(:, :, end, :));
budgets = 3:6;
EX = struct([]);
for ik = 1:numel(budgets)
    kk = budgets(ik);
    if kk == 3
        combs = combs3;
        Vk = squeeze(V3(:, :, end, :, :));
    else
        combs = nchoosek(1:12, kk);
        Vk = zeros(size(combs, 1), 5, numel(ells), 2);
        for il = 1:numel(ells)
            A = Ahi(:, :, il);
            for r = 1:5
                for c = 1:size(combs, 1)
                    T = [combs(c, :), R0s{r}];
                    zt = Zj(T, :);
                    Vk(c, r, il, :) = reshape(sum(zt .* (A(T, T) \ zt), 1) ./ s2, [1 1 1 2]);
                end
            end
        end
    end
    W = squeeze(min(Vk, [], 3));                 % worst r2 over the ell grid: (design, reference set, goal)
    EX(ik).k = kk;
    EX(ik).combs = combs;
    EX(ik).W = W;
    EX(ik).Vk = Vk;
end

% ==================================================================================================================
% 4. Optimal placement of 3 sensors (and 0 or 1 reference channel)
% ==================================================================================================================
say(lg, '\n=== 4. Placement of 3 sensors and at most 1 reference channel\n');
W3 = EX(1).W;
goalName = {'salt mass near the toe', 'supply cell above its limit'};
nomDesign = {nomMass, nomSupply};
A0 = Kj + gamJ(th0(1), th0(2), sm);
D4 = struct([]);
for gl = 1:2
    % (i) interference ignored; (i') exact at the nominal theta0, no reference; (ii) robust; (iii) robust + reference
    Snom = nomDesign{gl};
    v0 = zeros(size(combs3, 1), 1);
    for c = 1:size(combs3, 1)
        zt = Zj(combs3(c, :), gl);
        v0(c) = zt.' * (A0(combs3(c, :), combs3(c, :)) \ zt) / s2(gl);
    end
    [~, i0] = max(v0);
    Sth0 = combs3(i0, :);
    [~, i2] = max(W3(:, 1, gl));
    Srob = combs3(i2, :);
    Wr = W3(:, :, gl);
    [~, idx] = max(Wr(:));
    [i3, r3] = ind2sub(size(Wr), idx);
    Sref = combs3(i3, :);
    Rref = R0s{r3};
    [~, rn] = max(W3(ismember(combs3, Snom, 'rows'), :, gl));
    rules = {struct('name', 'interference ignored', 'S', Snom, 'R', []), ...
             struct('name', 'exact at nominal theta0', 'S', Sth0, 'R', []), ...
             struct('name', 'robust (ROED), no reference', 'S', Srob, 'R', []), ...
             struct('name', 'robust + reference channel', 'S', Sref, 'R', Rref), ...
             struct('name', 'interference ignored + best reference', 'S', Snom, 'R', R0s{rn})};
    say(lg, '\n-- goal %d: %s\n', gl, goalName{gl});
    for q = 1:numel(rules)
        T = [rules{q}.S, rules{q}.R];
        [wr2, wEll, gridR2] = worstEll(T, Kj, Zj(:, gl), s2(gl), @(ell) gamJ(aBox(2), ell, sm), ells, ellBox);
        Gw = gamJ(aBox(2), wEll, sm);
        nomVal = valueOf(gl, T, gamJ(0, th0(2), 0), eigExact, thrExact, phiT);
        th0Val = valueOf(gl, T, A0 - Kj, eigExact, thrExact, phiT);
        [worstVal, worstPkg] = valueOf(gl, T, Gw, eigExact, thrExact, phiT);
        rules{q}.worstPkg = worstPkg;
        rules{q}.worst = worstVal;
        rules{q}.worstR2 = wr2;
        rules{q}.worstEll = wEll;
        rules{q}.claimed = nomVal;
        rules{q}.atTheta0 = th0Val;
        rules{q}.gridWorst = gridR2;
        say(lg, '  %-40s %-12s ref %-4s: claimed (independent noise) %.4f; at theta0 %.4f; worst case %.4f nats\n', ...
            rules{q}.name, mat2str(rules{q}.S), refName(rules{q}.R), nomVal, th0Val, worstVal);
        say(lg, '      worst theta = (a, ell) = (%.3f, %.4f m); worst r2 %.6f (grid minimum %.6f)\n', aBox(2), wEll, ...
            wr2, gridR2);
        if gl == 2
            say(lg, '      thresholdGoalEig at the worst theta %.4f nats; Gaussian information on the supply salinity %.4f\n', ...
                worstPkg, eigFromR2(wr2));
        end
    end
    % ranking check after refinement: the best 10 designs on the grid keep their order at their refined worst case
    for opt = 1:2
        if opt == 1
            vals = W3(:, 1, gl);
            cfg = [(1:size(combs3, 1)).', ones(size(combs3, 1), 1)];
        else
            vals = reshape(W3(:, :, gl), [], 1);
            [cc, rr] = ind2sub([size(combs3, 1), 5], (1:numel(vals)).');
            cfg = [cc, rr];
        end
        [vs, o] = sort(vals, 'descend');
        top = o(1:10);
        ref = zeros(10, 1);
        for t = 1:10
            T = [combs3(cfg(top(t), 1), :), R0s{cfg(top(t), 2)}];
            ref(t) = worstEll(T, Kj, Zj(:, gl), s2(gl), @(ell) gamJ(aBox(2), ell, sm), ells, ellBox);
        end
        [~, best] = max(ref);
        say(lg, '  refinement check (%s): best of the 10 leading configurations after refinement is number %d;\n', ...
            ternary(opt == 1, 'no reference', '0/1 reference'), best);
        say(lg, '      grid minus refined worst r2 at most %.2e; margin to the second configuration %.2e (r2)\n', ...
            max(vs(1:10) - ref), ref(1) - max(ref(2:end)));
    end
    loss = rules{3}.worst - rules{1}.worst;
    lossRef = rules{4}.worst - rules{1}.worst;
    say(lg, '  The nominal design %s claims %.4f nats and delivers %.4f at its worst theta (a drop of %.4f, %.1f%%);\n', ...
        mat2str(Snom), rules{1}.claimed, rules{1}.worst, rules{1}.claimed - rules{1}.worst, ...
        100 * (rules{1}.claimed - rules{1}.worst) / rules{1}.claimed);
    say(lg, '  it is %.4f nats (%.1f%%) below the robust optimum %s and %.4f nats (%.1f%%) below the robust optimum\n', ...
        loss, 100 * loss / rules{3}.worst, mat2str(Srob), lossRef, 100 * lossRef / rules{4}.worst);
    say(lg, '  with a reference channel %s + %s.\n', mat2str(Sref), refName(Rref));
    D4(gl).rules = rules;
end

% ==================================================================================================================
% 5. Certificate (Certified OED) and 6. greedy + exchange against exhaustive search, budgets 3-6
% ==================================================================================================================
say(lg, '\n=== 5. Certified upper bound on the robust optimum (no enumeration of the designs)\n');
say(lg, 'Derivation. Let Theta_c = {a_hi} x {%d values of ell} (a subset of the search grid, a subset of Theta). For\n', ...
    numel(1:4:numel(ells)));
say(lg, '  every design OPT_k(Theta) <= OPT_k(Theta_c) because a minimum over a smaller set is larger. EIG_goal =\n');
say(lg, '  phi(r2) with phi increasing (phi(x) = -1/2 log(1 - x); phi_t for the yes/no question), so the robust\n');
say(lg, '  problem is max_S min_theta r2 and any bound U on it gives phi(U). For a fixed reference set R0 and a\n');
say(lg, '  scenario theta_j, relax the sensor weights w in the capped simplex Delta_k = {0 <= w <= 1, sum w = k}:\n');
say(lg, '    r2_j(w) = z'' P_j(w) (I + K P_j(w))^-1 z / sigma_q^2,  P_j(w) = (R_j + W (Gamma_j - R_j))^-1 W,\n');
say(lg, '  the noise-inflation relaxation (Certified OED, eq. 36-38, Theorem 15 with a diagonal inflation, its\n');
say(lg, '  Appendix A.6) with R_j = blkdiag(rho_j I_12, sigma_r^2 I_|R0|), rho_j = lambda_min(sigma^2 I + s_m^2 C_ellj),\n');
say(lg, '  the inflation borrowed from the non-correctable part (Gamma_j >= Gamma_e,j >= R_j). It is exact at binary\n');
say(lg, '  w (P_j(1_S) = E_S'' Gamma_SS^-1 E_S) and concave (P_j operator concave, X -> h''(Gam^-1 + G''XG)^-1 h convex\n');
say(lg, '  and non-increasing). Gradient: d r2_j / d w_i = rho_i ((N_j'' \\ v)_i)^2 / sigma_q^2, N_j = R_j + W(Gamma_j - R_j),\n');
say(lg, '  v = (I + K P_j)^-1 z. Then for every w_bar in Delta_k and every lambda in the simplex of the scenarios\n');
say(lg, '    max_S min_j r2(S; theta_j) <= max_{w in Delta_k} sum_j lambda_j r2_j(w)\n');
say(lg, '                               <= sum_j lambda_j r2_j(w_bar) + gamma_FW(sum_j lambda_j grad r2_j(w_bar), w_bar),\n');
say(lg, '  gamma_FW(g, w) = sum of the k largest g_i - g''w (Frank-Wolfe certificate, Theorem 8). lambda = e_j gives\n');
say(lg, '  min_j (best-k bound at theta_j) (min over theta of an upper bound of the best k-subset); a mixed lambda (the\n');
say(lg, '  soft-min weights at the relaxed max-min point) gives the max-min (dual) bound. Reference channels: the\n');
say(lg, '  bound is the maximum over the 5 reference sets R0 (none, r1-r4). Two cruder valid bounds, for any R:\n');
say(lg, '  the interference-free ceiling (N2: EIG(S u R; theta) <= EIG_e(S; theta), Gamma_e = sigma^2 I + s_m^2 C_ell,\n');
say(lg, '  relaxed in the same way) and the full network (all 16 channels; more data never lose information).\n');
say(lg, '  The certificate is the smallest of these bounds; the certified gap of a design is U - J(design).\n');

ellC = ells(1:4:end);
nC = numel(ellC);
gamC = cell(nC, 1);
rhoC = zeros(nC, 1);
gamCe = cell(nC, 1);
for j = 1:nC
    gamC{j} = gamJ(aBox(2), ellC(j), sm);
    gamCe{j} = gamE(ellC(j));
    rhoC(j) = min(eig(gamCe{j}));
end
say(lg, 'Scenarios Theta_c: a = %.3f, ell = %s m\n', aBox(2), mat2str(ellC, 4));
say(lg, '  inflations rho_j = lambda_min(Gamma_e,j) = %s (sigma^2 = %.1e)\n', mat2str(rhoC.', 4), sigma ^ 2);

% self-checks of the relaxation: exact at binary points, gradient, concavity
rng0 = 7;
randStream(rng0);
Tall = [1:12, 15];
scenChk = makeScen(Kj, Zj(:, 1), s2(1), gamC(6), rhoC(6), 15, sigR);
errBin = 0;
for c = 1:size(combs3, 1)
    w = zeros(12, 1);
    w(combs3(c, :)) = 1;
    v = relaxR2(w, scenChk, 1);
    T = [combs3(c, :), 15];
    zt = Zj(T, 1);
    exact = zt.' * ((Kj(T, T) + gamC{6}(T, T)) \ zt) / s2(1);
    errBin = max(errBin, abs(v - exact));
end
w = 0.1 + 0.8 * rand(12, 1);
[v0r, g0r] = relaxR2(w, scenChk, 1);
fd = zeros(12, 1);
for i = 1:12
    e = zeros(12, 1);
    e(i) = 1e-6;
    fd(i) = (relaxR2(w + e, scenChk, 1) - relaxR2(w - e, scenChk, 1)) / 2e-6;
end
errGrad = max(abs(fd - g0r)) / max(abs(g0r));
worstMid = -Inf;
for t = 1:200
    wa = rand(12, 1);
    wb = rand(12, 1);
    worstMid = max(worstMid, relaxR2(wa, scenChk, 1) + relaxR2(wb, scenChk, 1) - 2 * relaxR2(0.5 * (wa + wb), scenChk, 1));
end
say(lg, 'Self-checks of the relaxation (scenario ell = %.4f, reference r3 fixed, salt mass):\n', ellC(6));
say(lg, '  exact at all 220 binary designs: max error %.2e; gradient against finite differences: relative error %.2e;\n', ...
    errBin, errGrad);
say(lg, '  concavity along 200 random segments: largest f(a) + f(b) - 2 f(mid) = %.2e (<= 0: concave)\n', worstMid);
clear Tall v0r

CERT = struct([]);
for ik = 1:numel(budgets)
    kk = budgets(ik);
    for gl = 1:2
        % exhaustive robust optimum on the ell grid
        W = EX(ik).W(:, :, gl);
        [optNo, iNo] = max(W(:, 1));
        [optRef, idx] = max(W(:));
        [iRef, rRef] = ind2sub(size(W), idx);
        % per-reference-set relaxation bounds
        ubR = zeros(1, 5);
        ubVert = zeros(1, 5);
        ubDual = zeros(1, 5);
        relaxVal = zeros(1, 5);
        for r = 1:5
            scen = makeScen(Kj, Zj(:, gl), s2(gl), gamC, rhoC, R0s{r}, sigR);
            B5 = relaxBound(scen, kk);
            ubR(r) = B5.ub;
            ubVert(r) = B5.ubVertex;
            ubDual(r) = B5.ubDual;
            relaxVal(r) = B5.val;
        end
        % interference-free ceiling (N2), relaxed
        scenE = makeScen(blkdiag(Kj(1:12, 1:12)), Zj(1:12, gl), s2(gl), gamCe, rhoC, [], sigR);
        BE = relaxBound(scenE, kk);
        % full network (all 16 channels)
        full = Inf;
        for j = 1:nC
            Af = Kj + gamC{j};
            full = min(full, Zj(:, gl).' * (Af \ Zj(:, gl)) / s2(gl));
        end
        ubNo = min([ubR(1), BE.ub, full]);
        ubRef = min([max(ubR), BE.ub, full]);
        % robust greedy + exchange on the ell grid, for each reference set
        gx = zeros(1, 5);
        gS = cell(1, 5);
        for r = 1:5
            [gS{r}, gx(r)] = greedyExchange(Ahi, Zj(:, gl), s2(gl), kk, R0s{r});
        end
        [gxRef, rg] = max(gx);
        CERT(ik, gl).k = kk;
        CERT(ik, gl).optNo = optNo;
        CERT(ik, gl).optRef = optRef;
        CERT(ik, gl).Sno = EX(ik).combs(iNo, :);
        CERT(ik, gl).Sref = EX(ik).combs(iRef, :);
        CERT(ik, gl).Rref = R0s{rRef};
        CERT(ik, gl).ubR = ubR;
        CERT(ik, gl).ubVert = ubVert;
        CERT(ik, gl).ubDual = ubDual;
        CERT(ik, gl).relaxVal = relaxVal;
        CERT(ik, gl).ubCeil = BE.ub;
        CERT(ik, gl).full = full;
        CERT(ik, gl).ubNo = ubNo;
        CERT(ik, gl).ubRef = ubRef;
        CERT(ik, gl).gxNo = gx(1);
        CERT(ik, gl).gxRef = gxRef;
        CERT(ik, gl).gSno = gS{1};
        CERT(ik, gl).gSref = gS{rg};
        CERT(ik, gl).gRref = R0s{rg};
        if gl == 1
            tf = eigFromR2;
        else
            tf = phiT;
        end
        CERT(ik, gl).nats = struct('optNo', tf(optNo), 'optRef', tf(optRef), 'ubNo', tf(ubNo), 'ubRef', tf(ubRef), ...
                                   'gxNo', tf(gx(1)), 'gxRef', tf(gxRef), 'ceil', tf(BE.ub), 'full', tf(full), ...
                                   'ubRmax', tf(max(ubR)));
    end
end
for gl = 1:2
    say(lg, '\n-- goal %d: %s (nats; r2 in brackets)\n', gl, goalName{gl});
    for ik = 1:numel(budgets)
        Cc = CERT(ik, gl);
        n = Cc.nats;
        say(lg, '  k = %d sensors, no reference: exhaustive robust optimum %s %.4f [%.6f]; greedy + exchange %s %.4f\n', ...
            Cc.k, mat2str(Cc.Sno), n.optNo, Cc.optNo, mat2str(sort(Cc.gSno)), n.gxNo);
        say(lg, '      certificate %.4f [%.6f]: relaxation (R0 = none) %.4f [vertex %.6f, dual %.6f], ceiling %.4f,\n', ...
            n.ubNo, Cc.ubNo, tf2(gl, Cc.ubR(1), eigFromR2, phiT), Cc.ubVert(1), Cc.ubDual(1), n.ceil);
        say(lg, '      full network %.4f; certified gap %.4f nats (%.1f%% of the optimum)\n', n.full, n.ubNo - n.optNo, ...
            100 * (n.ubNo - n.optNo) / n.optNo);
        say(lg, '  k = %d sensors, <= 1 reference: exhaustive robust optimum %s + %s %.4f [%.6f]; greedy + exchange\n', ...
            Cc.k, mat2str(Cc.Sref), refName(Cc.Rref), n.optRef, Cc.optRef);
        say(lg, '      %s + %s %.4f; certificate %.4f [%.6f] (relaxation bounds per reference set %s, max %.4f);\n', ...
            mat2str(sort(Cc.gSref)), refName(Cc.gRref), n.gxRef, n.ubRef, Cc.ubRef, mat2str(Cc.ubR, 6), n.ubRmax);
        say(lg, '      certified gap %.4f nats (%.1f%% of the optimum); relaxed max-min values %s\n', n.ubRef - n.optRef, ...
            100 * (n.ubRef - n.optRef) / n.optRef, mat2str(Cc.relaxVal, 6));
    end
end
okCert = true;
okGx = 0;
nGx = 0;
for ik = 1:numel(budgets)
    for gl = 1:2
        okCert = okCert && CERT(ik, gl).ubNo >= CERT(ik, gl).optNo - 1e-12 && CERT(ik, gl).ubRef >= CERT(ik, gl).optRef - 1e-12;
        okGx = okGx + (abs(CERT(ik, gl).gxNo - CERT(ik, gl).optNo) < 1e-12) + (abs(CERT(ik, gl).gxRef - CERT(ik, gl).optRef) < 1e-12);
        nGx = nGx + 2;
    end
end
say(lg, '\nCertificate never below the exhaustive robust optimum (k = 3-6, both goals, 0 or <= 1 reference): %d\n', okCert);
say(lg, 'Robust greedy + exchange equal to the exhaustive robust optimum in %d of %d cases (k = 3-6, 2 goals, 0 or <= 1 ref)\n', ...
    okGx, nGx);

% ==================================================================================================================
% 6. Independent verification
% ==================================================================================================================
say(lg, '\n=== 6. Independent verification\n');
% (a) direct Gaussian conditioning in the augmented parameter space (m, c): hub errors as explicit unknowns
say(lg, '(a) Direct Gaussian conditioning: unknowns (m, c), c the 4 hub errors with prior a^2 I; readings\n');
say(lg, '    y_S = G_S m + B_S c + e_S, e_S ~ N(0, sigma^2 I + s_m^2 C_ell), y_R = c_R + e_R, e_R ~ N(0, sigma_r^2 I);\n');
say(lg, '    posterior precision Gam_x^-1 + A'' E^-1 A, goal variance h'' Lambda^-1 h (precision form, no K, no z)\n');
chkList = {};
for gl = 1:2
    rl = D4(gl).rules;
    for q = [1 3 4]
        chkList{end + 1} = struct('gl', gl, 'T', [rl{q}.S, rl{q}.R], 'ell', rl{q}.worstEll, 'name', rl{q}.name); %#ok<AGROW>
    end
end
maxDirect = 0;
for t = 1:numel(chkList)
    cl = chkList{t};
    hrow = goalRow(cl.gl, H, Hs);
    vDirect = directEig(cl.T, G, hrow, Gam, B, Dc, sigma, sm, sigR, aBox(2), cl.ell);
    vOp = eigExact(cl.T, gamJ(aBox(2), cl.ell, sm), cl.gl);
    maxDirect = max(maxDirect, abs(vDirect - vOp));
    say(lg, '  goal %d %-30s %-14s ell %.4f: eigOperator %.10f, direct conditioning %.10f nats\n', cl.gl, cl.name, ...
        refList(cl.T), cl.ell, vOp, vDirect);
end
say(lg, '  largest difference %.2e nats\n', maxDirect);
% (b) Monte Carlo: the mean-square error of the best linear predictor of the goal from simulated readings
say(lg, '(b) Monte Carlo (2 x 10^5 draws of m, c and the noises; regression of the goal on the readings):\n');
randStream(2026);
mcOut = zeros(numel(chkList), 2);
for t = [3 6]
    cl = chkList{t};
    hrow = goalRow(cl.gl, H, Hs);
    [vMC, seMC] = mcEig(cl.T, G, hrow, Gam, B, Dc, sigma, sm, sigR, aBox(2), cl.ell, 10, 20000);
    vOp = eigExact(cl.T, gamJ(aBox(2), cl.ell, sm), cl.gl);
    mcOut(t, :) = [vMC, seMC];
    say(lg, '  goal %d %-30s %-14s: exact %.4f nats, Monte Carlo %.4f +- %.4f (1 standard error of 10 batches)\n', ...
        cl.gl, cl.name, refList(cl.T), vOp, vMC, seMC);
end
% (c) the yes/no question with correlated noise: exactGoalEig on whitened readings against thresholdGoalEig
say(lg, '(c) Supply cell above its limit with correlated noise, at the worst theta of each design:\n');
say(lg, '    MC1 = Monte Carlo over 4 x 10^4 data sets with the exact posterior probability of the event (Gaussian\n');
say(lg, '    conditioning, no quadrature): H(p0) - mean H(P(s > limit | y)); MC2 = exactGoalEig (likelihood\n');
say(lg, '    re-weighting of 1.2 x 10^5 prior runs, 2000 data sets; readings whitened by chol(Gamma_TT)); its\n');
say(lg, '    effective sample size is printed: with few effective runs it is biased upwards.\n');
randStream(24);
thrMC = zeros(2, 5);
for t = [4 6]
    cl = chkList{t};
    T = cl.T;
    Gw = gamJ(aBox(2), cl.ell, sm);
    vThr = thrExact(T, Gw);
    vAcc = valueOf(2, T, Gw, eigExact, thrExact, phiT);
    [vMC1, se1] = mcThreshold(T, G, Hs, Gam, U(g.N + supply), limit, Gw, 40000);
    [vEx, ess] = exactThreshold(T, G, Hs, Gam, U(g.N + supply), limit, Gw, 120000, 2000);
    thrMC(t / 2 - 1, :) = [vAcc, vThr, vMC1, se1, vEx];
    say(lg, '  %-30s %-14s: accurate %.4f, thresholdGoalEig %.4f, MC1 %.4f +- %.4f, MC2 %.4f (mean ESS %.0f) nats\n', ...
        cl.name, refList(T), vAcc, vThr, vMC1, se1, vEx, ess);
end
% (d) a = 0 and s_m = 0: the nominal results with the machinery of this file (joint channels, references)
G0 = gamJ(0, th0(2), 0);
A00 = Kj + G0;
best0 = [-Inf -Inf];
arg0 = cell(1, 2);
for gl = 1:2
    for r = 1:5
        for c = 1:size(combs3, 1)
            T = [combs3(c, :), R0s{r}];
            v = Zj(T, gl).' * (A00(T, T) \ Zj(T, gl)) / s2(gl);
            if v > best0(gl) + 1e-13
                best0(gl) = v;
                arg0{gl} = T;
            end
        end
    end
end
refZero = 0;
for c = 1:size(combs3, 1)
    for r = 2:5
        T = [combs3(c, :), R0s{r}];
        refZero = max(refZero, abs(eigExact(T, G0, 1) - eigExact(combs3(c, :), G0, 1)));
    end
end
say(lg, '(d) a = 0 and s_m = 0 (independent noise 0.02^2), all 1100 configurations through the joint machinery:\n');
say(lg, '    salt mass optimum %s, %.4f nats (example_network: [4 7 8], %.4f); supply optimum %s, %.4f nats by\n', ...
    mat2str(arg0{1}), eigFromR2(best0(1)), bestNom, mat2str(arg0{2}), phiPkg(best0(2)));
say(lg, '    thresholdGoalEig (example_network: [7 8 11], %.4f; accurate %.4f); a reference channel then adds at most\n', ...
    bestRiskNom, phiT(best0(2)));
say(lg, '    %.1e nats (N1: without a hub error a reference channel is worth nothing)\n', refZero);
% (e) N1: the value of a reference channel
say(lg, '(e) Value of the reference channel r3 of hub 3 (Proposition N1), salt mass, worst amplitude, ell = %.4f m:\n', ...
    th0(2));
Gn1 = gamJ(aBox(2), th0(2), sm);
for Sx = {[], 4, 7, [7 8], [7 8 9], [4 7 8], [4 6 7]}
    S = Sx{1};
    if isempty(S)
        v1 = eigExact(15, Gn1, 1);
        say(lg, '    alone: %.2e nats\n', v1);
    else
        v1 = eigExact([S 15], Gn1, 1) - eigExact(S, Gn1, 1);
        say(lg, '    added to %-9s: %+.4f nats\n', mat2str(S), v1);
    end
end
say(lg, '\nTime: %.1f s for the computations\n', toc(tStart));

% ==================================================================================================================
% 7. Figure fig7_robust_network
% ==================================================================================================================
say(lg, '\n=== 7. Figure fig7_robust_network\n');
figRobust(outDir, 'fig7_robust_network', lg, g, U, X, Y, cand, zone, supply, D4, CERT, budgets, colX);

% ==================================================================================================================
% 8. Results file
% ==================================================================================================================
R = struct();
R.case = struct('sensor_noise', sigma, 'hub_error_box', aBox, 'model_error_sd', sm, 'corr_length_box_m', ellBox, ...
                'reference_noise', sigR, 'nominal_theta', th0, 'ell_grid', numel(ells), 'cert_scenarios', ellC, ...
                'budget', '3 sensors + at most 1 reference channel');
R.reproduced = struct('salt_mass', nomMass, 'salt_mass_nats', bestNom, 'supply', nomSupply, 'supply_nats', bestRiskNom, ...
                      'joint_salt_mass', arg0{1}, 'joint_supply', arg0{2});
for gl = 1:2
    rl = D4(gl).rules;
    rr = struct([]);
    for q = 1:numel(rl)
        rr(q).rule = rl{q}.name;
        rr(q).sensors = rl{q}.S;
        rr(q).reference = refName(rl{q}.R);
        rr(q).claimed_nats = round4(rl{q}.claimed);
        rr(q).at_theta0_nats = round4(rl{q}.atTheta0);
        rr(q).worst_nats = round4(rl{q}.worst);
        rr(q).worst_theta = [aBox(2), round4(rl{q}.worstEll)];
    end
    cc = struct([]);
    for ik = 1:numel(budgets)
        Cc = CERT(ik, gl);
        cc(ik).k = Cc.k;
        cc(ik).opt_noref_nats = round4(Cc.nats.optNo);
        cc(ik).opt_ref_nats = round4(Cc.nats.optRef);
        cc(ik).design_noref = Cc.Sno;
        cc(ik).design_ref = [Cc.Sref, Cc.Rref];
        cc(ik).certificate_noref_nats = round4(Cc.nats.ubNo);
        cc(ik).certificate_ref_nats = round4(Cc.nats.ubRef);
        cc(ik).gap_noref_pct = round(1000 * (Cc.nats.ubNo - Cc.nats.optNo) / Cc.nats.optNo) / 10;
        cc(ik).gap_ref_pct = round(1000 * (Cc.nats.ubRef - Cc.nats.optRef) / Cc.nats.optRef) / 10;
        cc(ik).greedy_exchange_noref_nats = round4(Cc.nats.gxNo);
        cc(ik).greedy_exchange_ref_nats = round4(Cc.nats.gxRef);
    end
    fld = ternary(gl == 1, 'salt_mass', 'supply_above_limit');
    R.(fld) = struct('rules', rr, 'budgets', cc);
end
R.checks = struct('eigOperator_vs_dataspace', max(errOp, errOpS), 'threshold_fold_vs_original', errThr, ...
                  'direct_conditioning_max_diff', maxDirect, 'certificate_never_below_optimum', okCert, ...
                  'greedy_exchange_equal_exhaustive', sprintf('%d of %d', okGx, nGx), ...
                  'worst_a_at_upper_end', sprintf('%d of %d', nWorstUpper, nCfg), ...
                  'monte_carlo_salt_mass', round4(mcOut(3, :)), 'monte_carlo_supply_gauss', round4(mcOut(6, :)), ...
                  'supply_accurate_pkg_mc1_se_mc2', round4(thrMC));
R.figure = 'fig7_robust_network.png';
R.log = 'robust_certified_network_log.txt';
writeJson(fullfile(outDir, 'robust_certified_network_results.json'), R);
say(lg, 'saved %s\n', fullfile(outDir, 'robust_certified_network_results.json'));
say(lg, 'Total time %.1f s\n', toc(tStart));
if lg > 0
    fclose(lg);
end
end

% ==================================================================================================================
% Criteria, worst case, designs
% ==================================================================================================================
function h = goalRow(goal, H, Hs)
% Goal row: 1 = salt mass near the toe, 2 = salinity of the supply cell.
if goal == 1
    h = H;
else
    h = Hs;
end
end

function [v, vPkg] = valueOf(goal, T, Gn, eigExact, thrExact, phiT)
% Information of the channels T in nats. Salt mass: eigOperator. Supply question: the yes/no information at the
% explained fraction r2_s = 1 - exp(-2 eigOperator(supply salinity)) by the accurate quadrature (V), and
% thresholdGoalEig with the noise folded into Sigma (VPKG).
if goal == 1
    v = eigExact(T, Gn, 1);
    vPkg = v;
else
    r2 = 1 - exp(-2 * eigExact(T, Gn, 2));
    v = phiT(r2);
    vPkg = thrExact(T, Gn);
end
end

function v = phiAccurate(r2, a)
% Mutual information (nats) between the event {z < a} of a standard normal goal z and data that explain the fraction
% r2 of its variance: H(Phi(a)) - E H(Phi((a - r x)/sqrt(1 - r2))), x ~ N(0, 1), the integral of thresholdGoalEig,
% written in u = (a - r x)/sqrt(1 - r2) and summed on 28001 points of [-14, 14] (accurate for r2 up to 1 - 1e-8).
if r2 <= 0
    v = 0;
    return
end
r2 = min(r2, 1 - 1e-12);
r = sqrt(r2);
s = sqrt(1 - r2);
u = linspace(-14, 14, 28001);
du = u(2) - u(1);
p = 0.5 * erfc(-u / sqrt(2));
w = exp(-0.5 * ((a - s * u) / r) .^ 2) / sqrt(2 * pi) * (s / r) * du;
p0 = 0.5 * erfc(-a / sqrt(2));
v = hbin(p0) - sum(w .* hbin(p));
v = max(v, 0);
end

function v = hbin(p)
p = min(max(p, 0), 1);
v = zeros(size(p));
k = p > 0 & p < 1;
v(k) = -(p(k) .* log(p(k)) + (1 - p(k)) .* log(1 - p(k)));
end

function [r2, ellW, gridR2] = worstEll(T, Kj, z, s2, gamFun, ells, ellBox)
% Smallest explained fraction r2 of channels T over ell (amplitude at its upper end): grid, then fminbnd in log ell.
f = @(ell) explained(T, Kj, z, s2, gamFun(ell));
v = arrayfun(f, ells);
[gridR2, i] = min(v);
lo = log(ells(max(i - 1, 1)));
hi = log(ells(min(i + 1, numel(ells))));
[x, fx] = fminbnd(@(t) f(exp(t)), lo, hi, optimset('TolX', 1e-10));
if fx < gridR2
    r2 = fx;
    ellW = exp(x);
else
    r2 = gridR2;
    ellW = ells(i);
end
ellW = min(max(ellW, ellBox(1)), ellBox(2));
end

function r2 = explained(T, Kj, z, s2, Gn)
zt = z(T);
r2 = zt.' * ((Kj(T, T) + Gn(T, T)) \ zt) / s2;
end

function v = worstGrid(Ahi, z, s2, T)
% Worst r2 of the channels T over the scenario matrices Ahi(:, :, j) = K + Gamma_j.
v = Inf;
zt = z(T);
for j = 1:size(Ahi, 3)
    v = min(v, zt.' * (Ahi(T, T, j) \ zt));
end
v = v / s2;
end

function [S, val] = greedyExchange(Ahi, z, s2, k, R0)
% Robust greedy (largest worst-case r2 over the scenarios) and best-improvement exchange of one sensor.
S = [];
for step = 1:k
    best = -Inf;
    bj = 0;
    for j = setdiff(1:12, S)
        v = worstGrid(Ahi, z, s2, [S, j, R0]);
        if v > best + 1e-15
            best = v;
            bj = j;
        end
    end
    S = [S, bj]; %#ok<AGROW>
end
val = worstGrid(Ahi, z, s2, [S, R0]);
improved = true;
while improved
    improved = false;
    bestSwap = val;
    bT = S;
    for i = S
        for j = setdiff(1:12, S)
            T = [setdiff(S, i), j];
            v = worstGrid(Ahi, z, s2, [T, R0]);
            if v > bestSwap + 1e-13
                bestSwap = v;
                bT = T;
            end
        end
    end
    if bestSwap > val + 1e-13
        S = bT;
        val = bestSwap;
        improved = true;
    end
end
end

% ==================================================================================================================
% Noise-inflation relaxation and certificate
% ==================================================================================================================
function scen = makeScen(Kj, z, s2, gamList, rho, R0, sigR)
% Relaxed problem over the 12 sensors with the reference set R0 fixed at weight 1, for the scenario covariances.
T = [1:12, R0];
scen.Kt = Kj(T, T);
scen.zt = z(T);
scen.s2 = s2;
scen.nFixed = numel(R0);
scen.Gn = cell(numel(gamList), 1);
scen.rho = cell(numel(gamList), 1);
for j = 1:numel(gamList)
    scen.Gn{j} = gamList{j}(T, T);
    scen.rho{j} = [rho(j) * ones(12, 1); sigR ^ 2 * ones(numel(R0), 1)];
end
end

function [val, grad] = relaxR2(w, scen, j)
% Noise-inflation relaxation of r2 at scenario j (Certified OED eq. 36-39, diagonal inflation R = diag(rho)):
% r2(w) = z' P (I + K P)^-1 z / s2, P = (R + W (Gamma - R))^-1 W; d r2 / d w_i = rho_i ((N' \ v)_i)^2 / s2.
Gn = scen.Gn{j};
rho = scen.rho{j};
wf = [w(:); ones(scen.nFixed, 1)];
m = numel(wf);
N = diag(rho) + bsxfun(@times, wf, Gn - diag(rho));
Pm = N \ diag(wf);
Pm = 0.5 * (Pm + Pm.');
v = (eye(m) + scen.Kt * Pm) \ scen.zt;
val = (scen.zt.' * Pm * v) / scen.s2;
if nargout > 1
    u = N.' \ v;
    grad = rho .* u .^ 2 / scen.s2;
    grad = grad(1:numel(w));
end
end

function [vals, grads] = relaxAll(w, scen)
nS = numel(scen.Gn);
vals = zeros(nS, 1);
grads = zeros(numel(w), nS);
for j = 1:nS
    [vals(j), grads(:, j)] = relaxR2(w, scen, j);
end
end

function out = relaxBound(scen, k)
% Certified upper bound on max_{|S| = k} min_j r2(S u R0; theta_j): Frank-Wolfe bounds of the per-scenario
% relaxations (vertex bound = min over the scenarios) and the max-min dual bound with mixed scenario weights.
n = 12;
nS = numel(scen.Gn);
ubVertex = Inf;
wStart = (k / n) * ones(n, 1);
for j = 1:nS
    f = @(w) relaxR2(w, scen, j);
    [~, ~, ub] = ascend(f, wStart, k, 500, 1e-9);
    ubVertex = min(ubVertex, ub);
end
% max-min relaxation by soft-min continuation; every (lambda, w) pair gives a valid bound
w = wStart;
ubDual = Inf;
val = -Inf;
for beta = [1e2 1e3 1e4 1e5]
    f = @(w) softMin(w, scen, beta);
    w = ascend(f, w, k, 300, 1e-10);
    [vals, grads] = relaxAll(w, scen);
    val = max(val, min(vals));
    for bt = beta * [0.1 1 10 100]
        e = exp(-bt * (vals - min(vals)));
        lam = e / sum(e);
        ubDual = min(ubDual, lam.' * vals + fwGap(grads * lam, w, k));
    end
    ubDual = min(ubDual, dualRefine(vals, grads, w, k));
end
out = struct('ub', min(ubVertex, ubDual), 'ubVertex', ubVertex, 'ubDual', ubDual, 'val', val);
end

function ub = dualRefine(vals, grads, w, k)
% Minimise phi(lambda) = lambda' vals + gamma_FW(grads lambda, w) over the simplex (mirror descent; any iterate valid).
nS = numel(vals);
lam = ones(nS, 1) / nS;
ub = Inf;
scale = max(abs(vals)) + max(abs(grads(:)));
for it = 1:1000
    gl = grads * lam;
    [~, o] = sort(gl, 'descend');
    vstar = zeros(numel(w), 1);
    vstar(o(1:k)) = 1;
    phi = lam.' * vals + gl.' * (vstar - w);
    ub = min(ub, phi);
    sub = vals + grads.' * (vstar - w);
    eta = 2 / (scale * sqrt(it));
    lam = lam .* exp(-eta * (sub - min(sub)));
    lam = lam / sum(lam);
end
end

function [F, gF] = softMin(w, scen, beta)
[vals, grads] = relaxAll(w, scen);
m = min(vals);
e = exp(-beta * (vals - m));
lam = e / sum(e);
F = m - log(sum(e)) / beta;
gF = grads * lam;
end

function gap = fwGap(g, w, k)
% Frank-Wolfe gap on the capped simplex: sum of the k largest gradients minus g'w (Certified OED, Theorem 8).
gs = sort(g, 'descend');
gap = sum(gs(1:k)) - g.' * w;
end

function [w, val, ub] = ascend(f, w, k, maxIt, tol)
% Projected gradient ascent on the capped simplex with Armijo backtracking; UB = smallest Frank-Wolfe bound met.
w = projCapped(w, k);
[val, g] = f(w);
ub = val + fwGap(g, w, k);
t = 1 / max(max(abs(g)), eps);
for it = 1:maxIt
    ok = false;
    for bt = 1:60
        wn = projCapped(w + t * g, k);
        [vn, gn] = f(wn);
        if vn >= val + 1e-4 * (g.' * (wn - w))
            ok = true;
            break
        end
        t = t / 2;
    end
    if ~ok
        break
    end
    step = max(abs(wn - w));
    w = wn;
    val = vn;
    g = gn;
    ub = min(ub, val + fwGap(g, w, k));
    if ub - val <= tol * max(abs(val), 1e-12) || step < 1e-13
        break
    end
    t = 2 * t;
end
end

function w = projCapped(y, k)
% Euclidean projection onto {0 <= w <= 1, sum(w) = k} by bisection on the shift.
lo = min(y) - 1;
hi = max(y);
for it = 1:200
    tau = 0.5 * (lo + hi);
    if sum(min(max(y - tau, 0), 1)) > k
        lo = tau;
    else
        hi = tau;
    end
end
w = min(max(y - 0.5 * (lo + hi), 0), 1);
end

% ==================================================================================================================
% Verification helpers
% ==================================================================================================================
function v = directEig(T, G, h, Gam, B, Dc, sigma, sm, sigR, a, ell)
% Goal information by Gaussian conditioning on x = (m, c) with independent noise blocks (precision form).
S = T(T <= 12);
Rr = T(T > 12) - 12;
n = size(G, 2);
I4 = eye(4);
A = [G(S, :), B(S, :); zeros(numel(Rr), n), I4(Rr, :)];
E = blkdiag(sigma ^ 2 * eye(numel(S)) + sm ^ 2 * exp(-Dc(S, S) / ell), sigR ^ 2 * eye(numel(Rr)));
Lam = blkdiag(inv(Gam), eye(4) / a ^ 2) + A.' * (E \ A);
hx = [h(:); zeros(4, 1)];
vpost = hx.' * (Lam \ hx);
v = 0.5 * log((h * Gam * h.') / vpost);
end

function [v, se] = mcEig(T, G, h, Gam, B, Dc, sigma, sm, sigR, a, ell, nBatch, nPer)
% Monte Carlo: simulate (m, c, noises), regress the goal on the readings; EIG = 1/2 log(var q / residual variance).
S = T(T <= 12);
Rr = T(T > 12) - 12;
n = size(G, 2);
Lm = chol(Gam + 1e-12 * eye(n), 'lower');
Le = chol(sm ^ 2 * exp(-Dc(S, S) / ell) + 1e-14 * eye(numel(S)), 'lower');
vb = zeros(nBatch, 1);
for b = 1:nBatch
    m = Lm * randn(n, nPer);
    c = a * randn(4, nPer);
    y = [G(S, :) * m + B(S, :) * c + Le * randn(numel(S), nPer) + sigma * randn(numel(S), nPer); ...
         c(Rr, :) + sigR * randn(numel(Rr), nPer)];
    q = h * m;
    Cyy = y * y.' / nPer;
    Cyq = y * q.' / nPer;
    vq = q * q.' / nPer;
    vb(b) = 0.5 * log(vq / (vq - Cyq.' * (Cyy \ Cyq)));
end
v = mean(vb);
se = std(vb) / sqrt(nBatch);
end

function [v, se] = mcThreshold(T, G, Hs, Gam, s0, limit, Gn, N)
% Monte Carlo of I(1{s > limit}; y_T) with the exact posterior probability of each simulated data set.
S = T(T <= 12);
n = size(G, 2);
Lm = chol(Gam + 1e-12 * eye(n), 'lower');
Gt = [G(S, :); zeros(numel(T) - numel(S), n)];
A = Gt * Gam * Gt.' + Gn(T, T);
zt = Gt * Gam * Hs.';
kg = A \ zt;
vpost = Hs * Gam * Hs.' - zt.' * kg;
m = Lm * randn(n, N);
y = Gt * m + chol(Gn(T, T), 'lower') * randn(numel(T), N);
p = 0.5 * erfc(-((s0 + kg.' * y - limit) / sqrt(vpost)) / sqrt(2));
p0 = 0.5 * erfc(-((s0 - limit) / sqrt(Hs * Gam * Hs.')) / sqrt(2));
h = hbin(p);
v = hbin(p0) - mean(h);
se = std(h) / sqrt(N);
end

function [v, ess] = exactThreshold(T, G, Hs, Gam, s0, limit, Gn, nIn, nOut)
% exactGoalEig for "supply cell above its limit" with correlated noise: readings whitened by chol(Gamma_TT).
S = T(T <= 12);
n = size(G, 2);
Lm = chol(Gam + 1e-12 * eye(n), 'lower');
Gt = [G(S, :); zeros(numel(T) - numel(S), n)];
Lt = chol(Gn(T, T), 'lower');
mIn = Lm * randn(n, nIn);
Yin = (Lt \ (Gt * mIn)).';
gIn = (s0 + Hs * mIn).' > limit;
mOut = Lm * randn(n, nOut);
Yout = (Lt \ (Gt * mOut + Lt * randn(numel(T), nOut))).';
[v, ess] = certaincoast.network.exactGoalEig(Yin, gIn, Yout, 1:numel(T), 1, 50);
end

function randStream(seed)
% Fixed seeds in MATLAB and GNU Octave.
if exist('OCTAVE_VERSION', 'builtin') ~= 0
    randn('state', seed); %#ok<RAND>
    rand('state', seed); %#ok<RAND>
else
    rng(seed);
end
end

% ==================================================================================================================
% Figure
% ==================================================================================================================
function figRobust(outDir, name, lg, g, U, X, Y, cand, zone, supply, D4, CERT, budgets, colX)
pal = palette();
r1 = D4(1).rules;
r2 = D4(2).rules;
fig = newFigure(16, 13.2);

% ---------------------------------------------------------------- (a) the section, hubs, designs, reference channel
ax = newAxes(fig, [1.45 6.95 8.6 4.3]);
C = reshape(U(g.N + 1:2 * g.N), g.Nx, g.Ny).';
[xy, yy, Cy] = padVertically(g, C);
zx = [min(X(zone)) - g.dx / 2, max(X(zone)) + g.dx / 2];
zy = [min(Y(zone)) - g.dy / 2, max(Y(zone)) + g.dy / 2];
patch('Parent', ax, 'XData', zx([1 2 2 1]), 'YData', zy([1 1 2 2]), 'FaceColor', pal.zoneTint, ...
      'EdgeColor', pal.orange, 'LineWidth', 0.8);
[~, hc] = contour(ax, xy, yy, Cy, [0.5 0.5]);
set(hc, 'LineColor', pal.muted, 'LineWidth', 0.8, 'LineStyle', '--');
for h = 1:4
    plot(ax, colX(h) * [1 1], [0.0625 1.0], '-', 'Color', pal.refGray, 'LineWidth', 0.9);
end
xc = X(cand);
yc = Y(cand);
inNom = ismember(1:12, r1{1}.S);
inRob = ismember(1:12, r1{3}.S);
inRef = ismember(1:12, r1{4}.S);
for j = 1:12
    if inNom(j)
        plot(ax, xc(j), yc(j), 'LineStyle', 'none', 'Marker', 's', 'MarkerSize', 12, 'MarkerFaceColor', 'none', ...
             'MarkerEdgeColor', pal.orange, 'LineWidth', 1.3);
    end
    if inRef(j)
        plot(ax, xc(j), yc(j), 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 9.5, 'MarkerFaceColor', 'none', ...
             'MarkerEdgeColor', pal.aqua, 'LineWidth', 1.5);
    end
    if inRob(j)
        plot(ax, xc(j), yc(j), 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 6, 'MarkerFaceColor', pal.blue, ...
             'MarkerEdgeColor', 'w', 'LineWidth', 0.75);
    else
        plot(ax, xc(j), yc(j), 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 5, 'MarkerFaceColor', 'w', ...
             'MarkerEdgeColor', pal.ink2, 'LineWidth', 0.8);
    end
    text(xc(j) + 0.055, yc(j) + 0.06, sprintf('%d', j), 'Parent', ax, 'HorizontalAlignment', 'left', ...
         'VerticalAlignment', 'bottom', 'FontSize', fs(8), 'Color', pal.ink);
end
plot(ax, X(supply), Y(supply), 'LineStyle', 'none', 'Marker', 'd', 'MarkerSize', 6, 'MarkerFaceColor', pal.ink, ...
     'MarkerEdgeColor', 'w', 'LineWidth', 0.75);
set(ax, 'XLim', [0 g.Lx], 'YLim', [0 g.Ly], 'XTick', 0:0.25:2, 'YTick', 0:0.25:1);
finishAxes(ax, 'Distance from the inland boundary, x (m)', 'Height, y (m)', true);
refHub = r1{4}.R - 12;
for h = 1:4
    fc = 'w';
    if ~isempty(refHub) && h == refHub
        fc = pal.aqua;
    end
    patch('Parent', ax, 'XData', colX(h) + 0.07 * [-1 1 1 -1], 'YData', 1.04 + [0 0 0.075 0.075], ...
          'FaceColor', fc, 'EdgeColor', pal.ink2, 'LineWidth', 0.8, 'Clipping', 'off');
    plot(ax, colX(h) * [1 1], [1.0 1.04], '-', 'Color', pal.refGray, 'LineWidth', 0.9, 'Clipping', 'off');
    text(colX(h) + 0.095, 1.0775, sprintf('hub %d', h), 'Parent', ax, 'HorizontalAlignment', 'left', ...
         'VerticalAlignment', 'middle', 'FontSize', fs(8), 'Color', pal.ink, 'Clipping', 'off');
end
panelLabel(ax, '(a)', 1.4);
refLabel = 'no reference channel';
if ~isempty(refHub)
    refLabel = sprintf('reference channel r%d on hub %d', refHub, refHub);
end
items = {legendItem('marker', 'candidate sensor (number)', 'w', 'o', 5, pal.ink2), ...
         legendItem('line', 'cable to its logger hub', pal.refGray, '-', 0.9), ...
         legendItem('marker', sprintf('interference ignored %s', mat2str(r1{1}.S)), 'none', 's', 10, pal.orange), ...
         legendItem('marker', sprintf('robust %s', mat2str(r1{3}.S)), pal.blue, 'o', 6, 'w'), ...
         legendItem('marker', sprintf('robust + reference %s', mat2str(r1{4}.S)), 'none', 'o', 9, pal.aqua), ...
         legendItem('patch', refLabel, pal.aqua, '', 0, pal.ink2), ...
         legendItem('patch', 'toe zone (salt-mass goal)', pal.zoneTint, '', 0, pal.orange), ...
         legendItem('line', '0.5 isochlor', pal.muted, '--', 0.8), ...
         legendItem('marker', 'supply cell (yes/no goal)', pal.ink, 'd', 6, 'w')};
drawLegend(fig, [10.3 6.95 5.6 4.75], items, 9, 5.6);
text('Parent', ax, 'Units', 'centimeters', 'Position', [8.85 4.95 0], 'String', 'designs for the salt mass:', ...
     'FontSize', fs(8), 'FontWeight', 'bold', 'Color', pal.ink, 'HorizontalAlignment', 'left', ...
     'VerticalAlignment', 'bottom', 'Clipping', 'off');
supplyNote = {sprintf('yes/no goal: ignored %s, robust %s,', mat2str(r2{1}.S), mat2str(r2{3}.S)), ...
              sprintf('robust + reference %s + r%d', mat2str(r2{4}.S), r2{4}.R - 12)};
text('Parent', ax, 'Units', 'centimeters', 'Position', [8.85 -0.72 0], 'String', supplyNote, ...
     'FontSize', fs(7.5), 'Color', pal.ink2, 'HorizontalAlignment', 'left', 'VerticalAlignment', 'top', ...
     'Clipping', 'off');

% ---------------------------------------------------------------- (b) worst-case information of the design rules
cols = {pal.orange, pal.blue, pal.aqua};
labs = {{'interference', 'ignored'}, {'robust', ''}, {'robust +', 'reference'}};
pos = {[1.45 1.25 3.35 3.85], [5.75 1.25 3.35 3.85]};
lims = {[0 2.8], [0 0.7]};
ticks = {0:0.5:2.5, 0:0.1:0.7};
titles = {'salt mass near the toe', 'supply cell above its limit?'};
for gl = 1:2
    rl = D4(gl).rules;
    a2 = newAxes(fig, pos{gl});
    vals = [rl{1}.worst, rl{3}.worst, rl{4}.worst];
    ub = CERT(1, gl).nats.ubRef;
    yr = diff(lims{gl});
    % claimed value of the design that ignores the interference: outline
    patch('Parent', a2, 'XData', 1 + 0.34 * [-1 1 1 -1], 'YData', [0 0 rl{1}.claimed rl{1}.claimed], ...
          'FaceColor', 'none', 'EdgeColor', pal.orange, 'LineWidth', 0.9, 'LineStyle', ':');
    text(1, rl{1}.claimed + 0.015 * yr, {'claimed', sprintf('%.3f', rl{1}.claimed)}, 'Parent', a2, ...
         'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'FontSize', fs(7.5), 'Color', pal.ink2);
    for q = 1:3
        patch('Parent', a2, 'XData', q + 0.34 * [-1 1 1 -1], 'YData', [0 0 vals(q) vals(q)], ...
              'FaceColor', cols{q}, 'EdgeColor', 'none');
        text(q, 0.5 * vals(q), sprintf('%.3f', vals(q)), 'Parent', a2, 'Rotation', 90, ...
             'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', 'FontSize', fs(8), 'Color', 'w', ...
             'FontWeight', 'bold');
        text(q, -0.03 * yr, labs{q}, 'Parent', a2, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', ...
             'FontSize', fs(7.5), 'Color', pal.ink);
    end
    plot(a2, [1.55 3.45], ub * [1 1], '--', 'Color', pal.ink, 'LineWidth', 0.9);
    text(3.45, ub + 0.02 * yr, sprintf('certificate %.3f', ub), 'Parent', a2, 'HorizontalAlignment', 'right', ...
         'VerticalAlignment', 'bottom', 'FontSize', fs(7.5), 'Color', pal.ink);
    set(a2, 'XLim', [0.5 3.5], 'YLim', lims{gl}, 'XTick', [], 'YTick', ticks{gl});
    grid(a2, 'on');
    set(a2, 'XGrid', 'off');
    if gl == 1
        finishAxes(a2, '', 'Worst-case information (nats)', false);
    else
        finishAxes(a2, '', '', false);
    end
    text('Parent', a2, 'Units', 'normalized', 'Position', [0.5, 1.03, 0], 'String', titles{gl}, ...
         'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'FontSize', fs(8), 'Color', pal.ink);
    if gl == 1
        panelLabel(a2, '(b)', 1.4);
    end
end

% ---------------------------------------------------------------- (c) certificate and robust optimum against the budget
axC = newAxes(fig, [11.15 1.25 4.6 3.85]);
nk = numel(budgets);
optN = zeros(nk, 1);
optR = optN;
ubN = optN;
ubR = optN;
gxN = optN;
gxR = optN;
for ik = 1:nk
    n = CERT(ik, 1).nats;
    optN(ik) = n.optNo;
    optR(ik) = n.optRef;
    ubN(ik) = n.ubNo;
    ubR(ik) = n.ubRef;
    gxN(ik) = n.gxNo;
    gxR(ik) = n.gxRef;
end
plot(axC, budgets, ubN, '--', 'Color', pal.blue, 'LineWidth', 1.0);
plot(axC, budgets, ubR, '--', 'Color', pal.aqua, 'LineWidth', 1.0);
plot(axC, budgets, optN, '-', 'Color', pal.blue, 'LineWidth', 1.2);
plot(axC, budgets, optR, '-', 'Color', pal.aqua, 'LineWidth', 1.2);
plot(axC, budgets, optN, 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 5.5, 'MarkerFaceColor', pal.blue, ...
     'MarkerEdgeColor', 'w', 'LineWidth', 0.75);
plot(axC, budgets, optR, 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 5.5, 'MarkerFaceColor', pal.aqua, ...
     'MarkerEdgeColor', 'w', 'LineWidth', 0.75);
plot(axC, budgets, gxN, 'LineStyle', 'none', 'Marker', '+', 'MarkerSize', 7, 'MarkerEdgeColor', pal.ink, ...
     'LineWidth', 0.9);
plot(axC, budgets, gxR, 'LineStyle', 'none', 'Marker', '+', 'MarkerSize', 7, 'MarkerEdgeColor', pal.ink, ...
     'LineWidth', 0.9);
text(budgets(end) + 0.08, optR(end) - 0.012, '+ 1 reference', 'Parent', axC, 'HorizontalAlignment', 'right', ...
     'VerticalAlignment', 'top', 'FontSize', fs(7.5), 'Color', pal.aqua);
text(budgets(end) + 0.08, optN(end) - 0.012, 'sensors only', 'Parent', axC, 'HorizontalAlignment', 'right', ...
     'VerticalAlignment', 'top', 'FontSize', fs(7.5), 'Color', pal.blue);
set(axC, 'XLim', [2.7 6.3], 'XTick', budgets, 'YLim', [1.55 2.1], 'YTick', 1.6:0.1:2.1);
grid(axC, 'on');
finishAxes(axC, 'Number of sensors, k', 'Salt mass: worst case (nats)', false);
text('Parent', axC, 'Units', 'normalized', 'Position', [0.5, 1.03, 0], 'String', 'bound and robust optimum', ...
     'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'FontSize', fs(8), 'Color', pal.ink);
panelLabel(axC, '(c)', 1.4);
itemsC = {legendItem('line', 'certificate (upper bound)', pal.ink2, '--', 1.0), ...
          legendItem('marker', 'exhaustive optimum', pal.ink2, 'o', 5.5, 'w'), ...
          legendItem('marker', 'greedy + exchange', 'none', '+', 7, pal.ink)};
drawLegend(fig, [11.35 1.35 4.3 1.15], itemsC, 3, 4.3);

say(lg, '  plotted (a): salt-mass designs: ignored %s, robust %s, robust + reference %s + r%d; yes/no designs %s, %s,\n', ...
    mat2str(r1{1}.S), mat2str(r1{3}.S), mat2str(r1{4}.S), refHub, mat2str(r2{1}.S), mat2str(r2{3}.S));
say(lg, '               %s + r%d\n', mat2str(r2{4}.S), r2{4}.R - 12);
say(lg, '  plotted (b): worst case (nats) ignored / robust / robust + reference: salt mass %s (claimed %.4f,\n', ...
    mat2str([r1{1}.worst r1{3}.worst r1{4}.worst], 5), r1{1}.claimed);
say(lg, '               certificate %.4f); supply %s (claimed %.4f, certificate %.4f)\n', CERT(1, 1).nats.ubRef, ...
    mat2str([r2{1}.worst r2{3}.worst r2{4}.worst], 5), r2{1}.claimed, CERT(1, 2).nats.ubRef);
say(lg, '  plotted (c): k = %s; salt mass, sensors only: optimum %s, certificate %s, greedy + exchange %s;\n', ...
    mat2str(budgets), mat2str(optN.', 5), mat2str(ubN.', 5), mat2str(gxN.', 5));
say(lg, '               + 1 reference: optimum %s, certificate %s, greedy + exchange %s\n', mat2str(optR.', 5), ...
    mat2str(ubR.', 5), mat2str(gxR.', 5));
saveFigure(fig, outDir, name, lg);
end

% ==================================================================================================================
% Helpers: as in run_all_figures.m (figure, axes, legend, output), and small utilities
% ==================================================================================================================
function pal = palette()
pal.blue = [42 120 214] / 255;
pal.lightBlue = [134 182 239] / 255;
pal.darkBlue = [24 79 149] / 255;
pal.orange = [235 104 52] / 255;
pal.aqua = [27 175 122] / 255;
pal.red = [208 59 59] / 255;
pal.ink = [11 11 11] / 255;
pal.ink2 = [82 81 78] / 255;
pal.muted = [137 135 129] / 255;
pal.refGray = [178 177 170] / 255;
pal.barGray = [195 194 183] / 255;
pal.dotGray = [160 159 152] / 255;
pal.spanGray = [240 239 236] / 255;
pal.alarmTint = [254 236 196] / 255;
pal.zoneTint = [252 228 214] / 255;
pal.grid = [225 224 217] / 255;
pal.ramp = [205 226 251; 183 211 246; 158 197 244; 134 182 239; 109 167 236; 85 152 231; 57 135 229; ...
            42 120 214; 37 106 191; 28 92 171; 24 79 149; 16 66 129; 13 54 107] / 255;
end

function fig = newFigure(w, h)
fig = figure('Visible', 'off', 'Color', 'w', 'Units', 'centimeters', 'Position', [2 2 w h], ...
             'PaperUnits', 'centimeters', 'PaperSize', [w h], 'PaperPosition', [0 0 w h], ...
             'PaperPositionMode', 'manual', 'InvertHardcopy', 'off', ...
             'DefaultAxesFontName', 'Helvetica', 'DefaultAxesFontSize', fs(9), ...
             'DefaultTextFontName', 'Helvetica', 'DefaultTextFontSize', fs(9), ...
             'DefaultAxesLineWidth', 0.5, 'DefaultLineLineWidth', 1.0, 'DefaultAxesTickDir', 'out', ...
             'DefaultAxesXColor', [0.15 0.15 0.15], 'DefaultAxesYColor', [0.15 0.15 0.15], ...
             'DefaultTextColor', [0.1 0.1 0.1]);
if isprop(fig, 'Theme')
    set(fig, 'Theme', 'light');
end
end

function ax = newAxes(fig, pos)
ax = axes('Parent', fig, 'Units', 'centimeters', 'Position', pos);
hold(ax, 'on');
end

function finishAxes(ax, xl, yl, isMap)
pal = palette();
set(ax, 'FontName', 'Helvetica', 'FontSize', fs(9), 'TickDir', 'out', 'LineWidth', 0.5, ...
    'XColor', [0.15 0.15 0.15], 'YColor', [0.15 0.15 0.15], 'Color', 'w', 'GridColor', pal.grid, ...
    'GridAlpha', 1, 'GridLineStyle', '-', 'TickLength', [0.012 0.012]);
if isMap
    set(ax, 'Box', 'on', 'Layer', 'top');
else
    set(ax, 'Box', 'off', 'Layer', 'bottom');
end
if ~isempty(xl)
    xlabel(ax, xl, 'FontName', 'Helvetica', 'FontSize', fs(10), 'Color', [0.1 0.1 0.1]);
end
if ~isempty(yl)
    ylabel(ax, yl, 'FontName', 'Helvetica', 'FontSize', fs(10), 'Color', [0.1 0.1 0.1]);
end
end

function panelLabel(ax, s, offsetCm)
pos = get(ax, 'Position');
text('Parent', ax, 'Units', 'normalized', 'Position', [-offsetCm / pos(3), 1 + 0.1 / pos(4), 0], 'String', s, ...
     'FontName', 'Helvetica', 'FontSize', fs(10), 'FontWeight', 'bold', 'HorizontalAlignment', 'left', ...
     'VerticalAlignment', 'bottom', 'Clipping', 'off');
end

function it = legendItem(kind, label, color, style, width, edge)
if nargin < 6
    edge = 'none';
end
it = struct('kind', kind, 'label', label, 'color', color, 'style', style, 'width', width);
it.edge = edge;
end

function drawLegend(fig, pos, items, nRows, colWidths)
ax = axes('Parent', fig, 'Units', 'centimeters', 'Position', pos);
hold(ax, 'on');
x0s = [0, cumsum(colWidths)];
rowH = pos(4) / nRows;
for k = 1:numel(items)
    it = items{k};
    col = floor((k - 1) / nRows) + 1;
    row = mod(k - 1, nRows) + 1;
    x0 = x0s(col);
    y0 = pos(4) - (row - 0.5) * rowH;
    switch it.kind
        case 'line'
            plot(ax, x0 + [0.05 0.75], [y0 y0], 'Color', it.color, 'LineStyle', it.style, 'LineWidth', it.width);
        case 'marker'
            plot(ax, x0 + 0.4, y0, 'LineStyle', 'none', 'Marker', it.style, 'MarkerSize', it.width, ...
                 'MarkerFaceColor', it.color, 'MarkerEdgeColor', it.edge, 'LineWidth', 0.9);
        case 'patch'
            patch('Parent', ax, 'XData', x0 + [0.1 0.7 0.7 0.1], 'YData', y0 + 0.12 * [-1 -1 1 1], ...
                  'FaceColor', it.color, 'EdgeColor', it.edge);
    end
    text(x0 + 0.9, y0, it.label, 'Parent', ax, 'FontName', 'Helvetica', 'FontSize', fs(8), ...
         'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', 'Clipping', 'off');
end
set(ax, 'XLim', [0 pos(3)], 'YLim', [0 pos(4)], 'Visible', 'off');
end

function [xy, yy, Cy] = padVertically(g, C)
xy = g.xc;
yy = [0, g.yc, g.Ly];
Cy = C([1, 1:g.Ny, g.Ny], :);
end

function [xt, yt] = topOfContour(M)
xt = NaN;
yt = -Inf;
k = 1;
while k < size(M, 2)
    n = M(2, k);
    seg = M(:, k + 1:k + n);
    [ymax, i] = max(seg(2, :));
    if ymax > yt
        yt = ymax;
        xt = seg(1, i);
    end
    k = k + n + 1;
end
end

function saveFigure(fig, outDir, name, lg)
png = fullfile(outDir, [name, '.png']);
pdf = fullfile(outDir, [name, '.pdf']);
print(fig, '-dpng', '-r300', png);
print(fig, '-dpdf', '-painters', pdf);
if exist('OCTAVE_VERSION', 'builtin') ~= 0
    [status, out] = system(sprintf('mogrify -units PixelsPerInch -density 300 "%s" 2>&1', png));
    if status ~= 0
        say(lg, '  PNG left without a resolution tag (ImageMagick: %s)\n', strtrim(out));
    end
end
say(lg, 'saved %s and %s\n', png, pdf);
close(fig);
end

function say(lg, varargin)
fprintf(1, varargin{:});
if lg > 0
    fprintf(lg, varargin{:});
end
end

function v = fs(n)
%FS Font size of the figures: the base size N (points) enlarged by 8 %.
v = 1.08 * n;
end

function s = refName(Rr)
if isempty(Rr)
    s = 'none';
else
    s = sprintf('r%d', Rr - 12);
end
end

function s = refList(T)
S = T(T <= 12);
Rr = T(T > 12);
s = mat2str(S);
if ~isempty(Rr)
    s = [s, ' + ', refName(Rr)];
end
end

function v = tf2(gl, r2, eigFromR2, phiT)
if gl == 1
    v = eigFromR2(r2);
else
    v = phiT(r2);
end
end

function out = ternary(c, a, b)
if c
    out = a;
else
    out = b;
end
end

function x = round4(x)
x = round(x * 1e4) / 1e4;
end

function writeJson(file, R)
% JSON with jsonencode (MATLAB R2016b+, GNU Octave 7+), pretty-printed where supported.
try
    txt = jsonencode(R, 'PrettyPrint', true);
catch
    txt = jsonencode(R);
end
fid = fopen(file, 'w');
fprintf(fid, '%s\n', txt);
fclose(fid);
end
