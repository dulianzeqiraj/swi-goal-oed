function C = fkcl_config()
%FKCL_CONFIG  Constants, calibration targets and paths of the Fushe-Kuqe chloride study.
%
%   C = FKCL_CONFIG() returns a struct used by every fkcl_* function. Edit the
%   paths here if the workbook is not in the repository's data/ folder.
%
%   Units: lengths in km for the plan grid and in m for depths; conductivity and
%   recharge in m/day; chloride in mg/L.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    here = fileparts(mfilename('fullpath'));          % .../chloride_fk/matlab
    C.root    = fileparts(here);                      % .../chloride_fk
    C.repo    = fileparts(C.root);                    % repository root
    C.xlsx    = fullfile(C.repo, 'data', 'Fushe_Kuqe_All_Data.xlsx');
    C.tsvdir  = fullfile(C.root, 'tsv');              % optional TSV copies of the sheets (GNU Octave)
    C.derived = fullfile(C.root, 'derived');          % shoreline, places (from fkcl_geo.py, GLOBE land mask)
    C.results = fullfile(C.root, 'results');          % reference numbers of the Python implementation
    C.out     = fullfile(C.root, 'results_matlab');   % outputs of this MATLAB code
    C.figdir  = fullfile(C.root, 'figures_matlab');

    % ---- physics -------------------------------------------------------------
    C.delta   = 0.025;     % (rho_s - rho_f)/rho_f
    C.Cl_f    = 12.92;     % mg/L, freshwater end-member (well 193)
    C.Cl_lim  = 250;       % mg/L, drinking-water chloride guideline
    C.screen  = 40;        % m, screen length for the upper, middle and base samples
    C.dx      = 0.25;      % km, plan grid (same as src/fushe_kuqe_field_design.m)
    C.gapMax  = 5.0;       % km, western edge farther than this from the sea = inland margin
    C.yCut    = 24.0;      % km, the chloride model covers the coastal sector north of this line
    C.rhoF    = 0.805;     % field cross-facies correlation of the companion study
    C.Apoly   = 349.09;    % km2, aquifer polygon

    % ---- calibration targets (sheet 7 and sheet 5 of the workbook) ----------
    C.obs = struct('area', 0.15, 'area_sd', 0.05, 'hlit', 3.0, 'hlit_sd', 1.0, ...
                   'f_sw', 0.047, 'f_c', 0.0186, 'logsd', 0.7, 'cl_ne', 30, 'cl_ne_s', 5);
    C.variant = 'second';  % wells 341/503 sample the second aquifer ('shallow' = sensitivity case)

    % ---- seawater reference composition (mg/kg at S = 35, scaled to S = 38.3, rho = 1.0285)
    C.sw35  = struct('Cl', 19353, 'Na', 10781, 'Mg', 1284, 'Ca', 412, 'K', 399, 'SO4', 2712, 'HCO3', 145);
    C.S_adr = 38.3;  C.rho_sw = 1.0285;
    C.molar = struct('Cl', 35.453, 'Na', 22.990, 'Ca', 40.078, 'Mg', 24.305, 'K', 39.098, 'HCO3', 61.017, 'SO4', 96.06);
    C.charge = struct('Cl', 1, 'Na', 1, 'Ca', 2, 'Mg', 2, 'K', 1, 'HCO3', 1, 'SO4', 2);

    % ---- variable-density section -------------------------------------------
    C.ySec = 36.5;         % km, section A-A' (continuous aquifer through the Fushe-Kuqe well field)
    C.secPhi = 0.25; C.secAniso = 0.1; C.secDm = 8.64e-5; C.secAL = 10; C.secAT = 1;

    C.isOctave = exist('OCTAVE_VERSION', 'builtin') ~= 0;
end
