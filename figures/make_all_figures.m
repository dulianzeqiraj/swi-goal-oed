function make_all_figures(outdir, xlsx_path)
%MAKE_ALL_FIGURES  Regenerate the manuscript figures from MATLAB.
%
%   make_all_figures(outdir, xlsx_path)
%
%   Writes the data-free theory figures directly and attempts the data-
%   dependent figures if their inputs are present. Outputs are PNGs in OUTDIR
%   (default: current folder). All sources are BENCHMARK-VERIFIED (see README map):
%
%     Fig1  conceptual workflow ...... make_fig1_workflow      (schematic)
%     Fig2  phase boundary ........... demo_phase_boundary     (rho_c ~ 0.76)
%     Fig3  structural invariance .... demo_phase_boundary     (data collapse)
%     Fig4  Henry benchmark .......... henry_benchmark_figure  (benchmark-verified solver)
%     Fig5  Fushe-Kuqe design map .... fushe_kuqe_design       (real geometry + K)
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 1 || isempty(outdir), outdir = pwd; end
    if nargin < 2, xlsx_path = ''; end
    here = fileparts(mfilename('fullpath'));
    if isempty(xlsx_path), xlsx_path = fullfile(here,'..','data','Fushe_Kuqe_All_Data.xlsx'); end
    addpath(here, fullfile(here,'..','src'), fullfile(here,'..','demo'));
    fprintf('Writing figures to %s\n', outdir);

    make_fig1_workflow(outdir);                 fprintf('  Fig1 (workflow) done\n');
    demo_phase_boundary(outdir);                fprintf('  Fig2, Fig3 (phase boundary) done\n');

    % Fig 4 -- benchmark-verified Henry benchmark (writes henry_benchmark.png in cwd)
    try
        cwd = pwd; cd(outdir);
        henry_benchmark_figure();
        if exist('henry_benchmark.png','file')
            movefile('henry_benchmark.png','Fig4_HenryBenchmark.png');
        end
        cd(cwd); fprintf('  Fig4 (Henry benchmark) done\n');
    catch ME
        fprintf('  Fig4 skipped (%s)\n', ME.message);
    end

    % Fig 5 -- Fushe-Kuqe design map (needs the dataset)
    if exist(xlsx_path,'file')
        try
            cwd = pwd; cd(outdir);
            fushe_kuqe_design(xlsx_path);
            if exist('fushe_kuqe_design.png','file')
                movefile('fushe_kuqe_design.png','Fig5_FusheKuqeDesign.png');
            end
            cd(cwd); fprintf('  Fig5 (Fushe-Kuqe design) done\n');
        catch ME
            fprintf('  Fig5 skipped (%s)\n', ME.message);
        end
    else
        fprintf('  Fig5 skipped: dataset not found (%s) — pass its path as 2nd arg.\n', xlsx_path);
    end
    fprintf('Done.\n');
end
