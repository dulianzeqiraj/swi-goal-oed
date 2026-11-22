function v = fkcl_json(s, varargin)
%FKCL_JSON  Read a JSON file (first argument a file name) or index into a decoded JSON struct by the
%   original keys, whatever valid field names JSONDECODE made of them ('240' -> 'x240',
%   '1000|op+D' -> 'x1000_op_D' and similar):  v = fkcl_json(S, 'E1', '240', 'kalib', 'cov').
    if ischar(s)
        v = jsondecode(fileread(s));
        if isempty(varargin), return, end
        s = v;
    end
    v = s;
    for k = 1:numel(varargin)
        key = varargin{k};
        if isnumeric(key), v = v(key); continue, end
        fn = fieldnames(v); norm = @(x) regexprep(lower(x), '[^a-z0-9]', '');
        nk = norm(key); hit = 0;
        for q = 1:numel(fn)
            f = norm(fn{q});
            if strcmp(f, nk) || (numel(f) > 1 && f(1) == 'x' && strcmp(f(2:end), nk)), hit = q; break, end
        end
        if ~hit, error('fkcl:json', 'key %s not found', key); end
        v = v.(fn{hit});
    end
end
