function Cc = fkcl_readcell(C, sheet)
%FKCL_READCELL  One worksheet of the Fushe-Kuqe workbook as a cell array.
%
%   Cc = FKCL_READCELL(C, sheet) reads the sheet with READCELL (MATLAB R2019b or
%   newer). Empty cells become [] and text stays char, so the result is the same
%   whichever reader is used. GNU Octave has no READCELL; there the function reads
%   C.tsvdir/<sheet>.tsv, a tab-separated copy of the sheet (fkcl_export.py --tsv).

    if exist('readcell', 'file') == 2 || exist('readcell', 'builtin') == 5
        Cc = readcell(C.xlsx, 'Sheet', sheet);
        for k = 1:numel(Cc)
            v = Cc{k};
            if (isobject(v) && ismissing(v)) || (isnumeric(v) && isempty(v))
                Cc{k} = [];
            elseif isstring(v)
                Cc{k} = char(v);
            end
        end
        return
    end
    f = fullfile(C.tsvdir, [sheet '.tsv']);
    if ~exist(f, 'file')
        error('fkcl:readcell', ['No READCELL and no TSV copy %s. In GNU Octave, export the sheets with ' ...
              'python3 chloride_fk/python/fkcl_export.py --tsv chloride_fk/tsv'], f);
    end
    txt = fileread(f);
    lines = regexp(txt, '\r?\n', 'split');
    while ~isempty(lines) && isempty(lines{end}), lines(end) = []; end
    parts = cellfun(@(s) regexp(s, '\t', 'split'), lines, 'UniformOutput', false);
    nc = max(cellfun(@numel, parts));
    Cc = cell(numel(parts), nc);
    for r = 1:numel(parts)
        for c = 1:numel(parts{r})
            s = strtrim(parts{r}{c});
            if isempty(s)
                Cc{r, c} = [];
            else
                v = str2double(s);
                if isnan(v) && ~strcmpi(s, 'nan'), Cc{r, c} = s; else, Cc{r, c} = v; end
            end
        end
    end
end
