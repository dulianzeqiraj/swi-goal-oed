function r2_step0_reproduce()
%R2_STEP0_REPRODUCE  Reproduce the published R1 numbers as-is (anchor run).
%
%   Runs, in order: demo_phase_boundary, gate1_henry_vd, gate3_field and
%   gate2_henry, exactly as released, writing figures to r2_results/. Every
%   number the manuscript/README claim is re-printed here so that all later
%   R2 analyses are compared against a REPRODUCED baseline, not a remembered
%   one. No parameters are changed in this step.
%
%   Published targets (README + manuscript):
%     demo_phase_boundary : rho_c ~ 0.760, max pooling loss ~19% of pooled EIG
%     gate1_henry_vd      : min rel. error 7.46e-6 (PASS, tol 1e-5)
%     gate3_field         : rho_c = 0.762, rho_F = 0.805, gain ~10%
%                           (0.595 vs 0.537 nats), N=5 monitoring + M=3 MAR
%     gate2_henry         : mid-isochlor toe in the classic-Henry band
%
%   Part of the HYDROL82304R1 -> R2 revision. Author: D. Zeqiraj.

    here = fileparts(mfilename('fullpath'));
    root = fullfile(here, '..');
    addpath(fullfile(root, 'src'), fullfile(root, 'demo'));
    outdir = fullfile(here, 'r2_results');
    if ~exist(outdir, 'dir'), mkdir(outdir); end
    xlsx = fullfile(root, 'data', 'Fushe_Kuqe_All_Data.xlsx');

    t0 = tic;
    fprintf('\n================ STEP 0.1: demo_phase_boundary =================\n');
    try, demo_phase_boundary(outdir); catch e, fprintf('FAILED: %s\n', getReport(e, 'basic')); end

    fprintf('\n================ STEP 0.2: gate1_henry_vd ======================\n');
    try, gate1_henry_vd; catch e, fprintf('FAILED: %s\n', getReport(e, 'basic')); end

    fprintf('\n================ STEP 0.3: gate3_field =========================\n');
    try, gate3_field(xlsx); catch e, fprintf('FAILED: %s\n', getReport(e, 'basic')); end

    fprintf('\n================ STEP 0.4: gate2_henry =========================\n');
    try, gate2_henry(outdir); catch e, fprintf('FAILED: %s\n', getReport(e, 'basic')); end

    fprintf('\nSTEP 0 done in %.1f s. Figures in %s\n', toc(t0), outdir);
end
