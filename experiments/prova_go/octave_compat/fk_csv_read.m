function [hdr, C] = fk_csv_read(f)
%FK_CSV_READ  Header row and body cells (char) of a CSV file with optional "quoted" fields.
    txt = fileread(f);
    lines = regexp(txt, '\r?\n', 'split');
    lines = lines(~cellfun(@isempty, lines));
    hdr = split_line(lines{1});
    C = cell(numel(lines) - 1, numel(hdr)); C(:) = {''};
    for r = 2:numel(lines)
        v = split_line(lines{r});
        C(r-1, 1:numel(v)) = v;
    end
end
function v = split_line(s)
    v = {}; cur = ''; inq = false; k = 1;
    while k <= numel(s)
        c = s(k);
        if inq
            if c == '"'
                if k < numel(s) && s(k+1) == '"', cur(end+1) = '"'; k = k + 1; else, inq = false; end
            else
                cur(end+1) = c; %#ok<AGROW>
            end
        elseif c == '"'
            inq = true;
        elseif c == ','
            v{end+1} = cur; cur = ''; %#ok<AGROW>
        else
            cur(end+1) = c; %#ok<AGROW>
        end
        k = k + 1;
    end
    v{end+1} = cur;
end
