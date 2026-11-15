function M = readmatrix(file, varargin)
%READMATRIX  GNU Octave stand-in for the MATLAB call readmatrix(xlsxfile,'Sheet',name).
%   M = READMATRIX(FILE,'Sheet',NAME) serves exactly the calls of
%   src/fushe_kuqe_field_design.m: it reads the CSV export of sheet NAME of
%   Fushe_Kuqe_All_Data.xlsx (data/fk_boundary.csv for '3_Boundary_Coords',
%   data/fk_wells.csv for '2_All_Wells', made by export_fk_csv.py) and returns,
%   as MATLAB does, the numeric block below the header row with NaN for text or
%   empty cells. FILE itself may also be a .csv file. Only on the path in Octave
%   (prova_go_setup adds this folder when exist('OCTAVE_VERSION','builtin')).
    [hdr, C] = fk_csv_read(fk_csv_file(file, varargin{:})); %#ok<ASGLU>
    M = nan(size(C));
    for k = 1:numel(C)
        v = str2double(C{k});
        if ~isnan(v), M(k) = v; end
    end
end
