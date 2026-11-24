function varargout = size(T, d)
%SIZE  Rows and columns of the table.
    sz = [numel(T.cols{1}) numel(T.cols)];
    if nargin > 1, varargout{1} = sz(d); elseif nargout <= 1, varargout{1} = sz; else, varargout = num2cell(sz); end
end
