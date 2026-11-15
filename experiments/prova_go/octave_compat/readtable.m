function T = readtable(file, varargin)
%READTABLE  GNU Octave stand-in for the MATLAB call readtable(xlsxfile,'Sheet',name).
%   T = READTABLE(FILE,'Sheet',NAME) reads the CSV export of the sheet (see
%   READMATRIX) and returns a small table object that supports what
%   src/fushe_kuqe_field_design.m uses: brace indexing T{:,c} giving a numeric
%   column (NaN for empty cells) when the column is numeric and a cell array of
%   character vectors otherwise, plus T.Properties.VariableNames. Octave only.
    [hdr, C] = fk_csv_read(fk_csv_file(file, varargin{:}));
    T = fkcsvtable(hdr, C);
end
