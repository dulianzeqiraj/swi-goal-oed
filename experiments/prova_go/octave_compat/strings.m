function s = strings(varargin)
%STRINGS  GNU Octave stand-in: a cell array of empty character vectors of the given size. Octave only.
    s = cell(varargin{:}); s(:) = {''};
end
