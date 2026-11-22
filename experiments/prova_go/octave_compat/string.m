function s = string(x)
%STRING  GNU Octave stand-in (Octave has no string class): returns a cell array of
%   character vectors of the same shape, which the builder then uses through
%   cellstr/strcmp exactly as a MATLAB string array. Octave only.
    if iscell(x), s = cellfun(@to_char, x, 'UniformOutput', false);
    elseif ischar(x), s = {x};
    else, s = arrayfun(@(v) num2str(v), x, 'UniformOutput', false);
    end
end
function c = to_char(v)
    if ischar(v), c = v; else, c = num2str(v); end
end
