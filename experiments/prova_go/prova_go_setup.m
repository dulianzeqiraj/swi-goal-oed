function here = prova_go_setup()
%PROVA_GO_SETUP  Path setup for PROVA-GO (MATLAB R2021+ or GNU Octave 8.4).
%   here = PROVA_GO_SETUP() adds this folder and ../../src (the user's model code,
%   used unchanged) to the path. In GNU Octave only, it also adds octave_compat
%   (readmatrix/readtable from the CSV exports in data/, string/strings and the
%   'MissingPlacement' option of sort), so MATLAB keeps its built-ins.
    here = fileparts(mfilename('fullpath'));
    addpath(here);
    addpath(fullfile(here, '..', '..', 'src'));
    if exist('OCTAVE_VERSION', 'builtin') ~= 0
        warning('off', 'Octave:shadowed-function');
        addpath(fullfile(here, 'octave_compat'));
    end
end
