function T = fkcsvtable(hdr, C)
%FKCSVTABLE  Minimal table object returned by the Octave READTABLE stand-in.
    s.names = hdr(:)';
    s.cols = cell(1, size(C, 2));
    for c = 1:size(C, 2)
        v = str2double(C(:, c));
        isnum = all(isnan(v) == cellfun(@isempty, C(:, c)));   % every non-empty cell is a number
        if isnum, s.cols{c} = v; else, s.cols{c} = C(:, c); end
    end
    T = class(s, 'fkcsvtable');
end
