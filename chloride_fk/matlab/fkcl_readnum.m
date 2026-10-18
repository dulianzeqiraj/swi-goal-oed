function M = fkcl_readnum(file)
%FKCL_READNUM  Numeric CSV with one header line (MATLAB readmatrix; Octave dlmread).
    if exist('readmatrix', 'file') == 2 || exist('readmatrix', 'builtin') == 5
        M = readmatrix(file, 'NumHeaderLines', 1);
    else
        M = dlmread(file, ',', 1, 0);
    end
end
