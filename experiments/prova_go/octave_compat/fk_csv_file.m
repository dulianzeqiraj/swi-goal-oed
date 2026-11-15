function f = fk_csv_file(file, varargin)
%FK_CSV_FILE  Map (xlsxfile,'Sheet',name) to the CSV export in ../data (Octave stand-ins only).
    here = fileparts(mfilename('fullpath'));
    [~, ~, ext] = fileparts(file);
    if strcmpi(ext, '.csv'), f = file; return; end
    sheet = '';
    for k = 1:2:numel(varargin)-1
        if strcmpi(varargin{k}, 'Sheet'), sheet = varargin{k+1}; end
    end
    switch sheet
        case '3_Boundary_Coords', f = fullfile(here, '..', 'data', 'fk_boundary.csv');
        case '2_All_Wells',       f = fullfile(here, '..', 'data', 'fk_wells.csv');
        otherwise
            error('octave_compat:sheet', 'No CSV export for sheet "%s" of %s.', sheet, file);
    end
    if exist(f, 'file') ~= 2
        error('octave_compat:csv', 'Missing %s: run python3 export_fk_csv.py once.', f);
    end
end
