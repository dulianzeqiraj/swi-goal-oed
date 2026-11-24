function x = fkcl_vd_toe(s, level)
%FKCL_VD_TOE  Distance from the sea [m] where c in the deepest active cell of each column crosses level.
    if nargin < 2, level = 0.5; end
    Cf = fkcl_vd_field(s, s.c); base = nan(1, s.nx);
    for i = 1:s.nx
        j = find(s.act(:, i), 1, 'last');
        if ~isempty(j), base(i) = Cf(j, i); end
    end
    x = NaN;
    for i = 1:s.nx - 1
        if (base(i) - level) * (base(i + 1) - level) < 0
            x = s.xc(i) + (level - base(i)) / (base(i + 1) - base(i)) * (s.xc(i + 1) - s.xc(i));
            return
        end
    end
end
