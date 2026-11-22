function varargout = sort(varargin)
%SORT  GNU Octave stand-in that adds the MATLAB option 'MissingPlacement' (used by
%   pick_topk of the builder: sort(v,'descend','MissingPlacement','last')) and
%   otherwise calls the built-in sort unchanged. Octave only (shadows the built-in).
    k = find(cellfun(@(a) ischar(a) && strcmpi(a, 'MissingPlacement'), varargin), 1);
    if isempty(k)
        [varargout{1:max(nargout, 1)}] = builtin('sort', varargin{:});
        return
    end
    place = lower(varargin{k+1}); args = varargin([1:k-1, k+2:end]);
    [s, i] = builtin('sort', args{:});
    if isvector(s) && any(strcmp(place, {'last', 'first'}))
        m = isnan(s);
        if strcmp(place, 'last'), o = [find(~m(:)); find(m(:))]; else, o = [find(m(:)); find(~m(:))]; end
        s = s(o); i = i(o);
    end
    varargout{1} = s; if nargout > 1, varargout{2} = i; end
end
