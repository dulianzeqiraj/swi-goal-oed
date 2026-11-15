function out = subsref(T, S)
%SUBSREF  T{:,c} (one column: numeric or cellstr) and T.Properties.VariableNames.
    switch S(1).type
        case '{}'
            sub = S(1).subs; c = sub{2}; r = sub{1};
            if ischar(c) && strcmp(c, ':'), c = 1:numel(T.cols); end
            if numel(c) ~= 1, error('fkcsvtable:index', 'Only one column at a time: T{:,c}.'); end
            out = T.cols{c};
            if ~(ischar(r) && strcmp(r, ':')), out = out(r); end
        case '.'
            if strcmp(S(1).subs, 'Properties'), out = struct('VariableNames', {T.names}); else
                error('fkcsvtable:field', 'Unknown field %s.', S(1).subs); end
        otherwise
            error('fkcsvtable:index', 'Unsupported indexing.');
    end
    if numel(S) > 1, out = subsref(out, S(2:end)); end
end
