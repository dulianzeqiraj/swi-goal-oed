function make_all_figures(outdir, xlsx_path)
%MAKE_ALL_FIGURES  Regenerate the article figures from MATLAB.
%
%   make_all_figures(outdir, xlsx_path)
%
%   Writes the data-free figures directly and the data-dependent ones if the
%   workbook is present. Outputs are 600 dpi PNGs in OUTDIR (default: current
%   folder). The mapping follows the figure numbering of the article:
%
%     Fig2  poolability phase boundary ... demo_phase_boundary   (rho_c = 0.762)
%     Fig3  size invariance .............. demo_phase_boundary
%     Fig4  Henry benchmark .............. gate2_henry           (toe 1.38 m)
%     Fig5  well/facies map .............. fig5_facies_map       (17/16/10 wells)
%     Fig6a MAR effectiveness map ........ fushe_kuqe_eig_map
%     Fig6b monitoring EIG map ........... fushe_kuqe_eig_map
%     Fig7  recommended design map ....... fushe_kuqe_design
%
%   Figure 1 of the article is a schematic drawn outside MATLAB; the workflow
%   sketch written by make_fig1_workflow is a different rendering of the same
%   pipeline and is produced here only as an optional extra.
%
%   Note: demo/henry_benchmark_figure.m and demo/section8_design.m are earlier
%   prototypes kept for reference. They use a different discretization and are
%   not called here, because they do not produce any figure or number of the
%   article.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 1 || isempty(outdir), outdir = pwd; end
    if nargin < 2, xlsx_path = ''; end
    here = fileparts(mfilename('fullpath'));
    if isempty(xlsx_path), xlsx_path = fullfile(here,'..','data','Fushe_Kuqe_All_Data.xlsx'); end
    addpath(here, fullfile(here,'..','src'), fullfile(here,'..','demo'));
    fprintf('Writing figures to %s\n', outdir);

    % --- Fig 2 and Fig 3: phase boundary and size invariance ---------------
    demo_phase_boundary(outdir);                fprintf('  Fig2, Fig3 (phase boundary) done\n');

    % --- Fig 4: Henry benchmark (writes Fig4_HenryBenchmark.png) -----------
    try
        gate2_henry(outdir);                    fprintf('  Fig4 (Henry benchmark) done\n');
    catch ME
        fprintf('  Fig4 skipped (%s)\n', ME.message);
    end

    if ~exist(xlsx_path,'file')
        fprintf('  Fig5, Fig6, Fig7 skipped: dataset not found (%s) - pass its path as 2nd arg.\n', xlsx_path);
        fprintf('Done.\n');
        return
    end

    % --- Fig 5: well/facies map --------------------------------------------
    try
        fig5_facies_map(xlsx_path, outdir);     fprintf('  Fig5 (well/facies map) done\n');
    catch ME
        fprintf('  Fig5 skipped (%s)\n', ME.message);
    end

    % --- Fig 6a/6b: the two field maps (written in the working folder) -----
    try
        cwd = pwd; cd(outdir);
        fushe_kuqe_eig_map(xlsx_path);
        if exist('fushe_kuqe_mar_map.png','file')
            movefile('fushe_kuqe_mar_map.png','Fig6a_MAR_map.png');
        end
        if exist('fushe_kuqe_eig_map.png','file')
            movefile('fushe_kuqe_eig_map.png','Fig6b_EIG_map.png');
        end
        cd(cwd); fprintf('  Fig6a, Fig6b (field maps) done\n');
    catch ME
        fprintf('  Fig6 skipped (%s)\n', ME.message);
    end

    % --- Fig 7: recommended design map -------------------------------------
    try
        cwd = pwd; cd(outdir);
        fushe_kuqe_design(xlsx_path);
        if exist('fushe_kuqe_design.png','file')
            movefile('fushe_kuqe_design.png','Fig7_DesignMap.png');
        end
        cd(cwd); fprintf('  Fig7 (design map) done\n');
    catch ME
        fprintf('  Fig7 skipped (%s)\n', ME.message);
    end

    fprintf('Done.\n');
end
