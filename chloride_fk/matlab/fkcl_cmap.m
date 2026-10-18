function cm = fkcl_cmap(name, n)
%FKCL_CMAP  Perceptually uniform colour maps without toolboxes (anchor-point approximations of the
%   matplotlib maps used in the manuscript): 'viridis', 'magma_r', 'cividis_r', 'ylgnbu'.
    if nargin < 2, n = 256; end
    switch lower(name)
        case 'viridis'
            A = [68 1 84; 72 40 120; 62 74 137; 49 104 142; 38 130 142; 31 158 137; 53 183 121; 110 206 88; 181 222 43; 253 231 37];
        case 'magma_r'
            A = flipud([0 0 4; 28 16 68; 79 18 123; 129 37 129; 181 54 122; 229 80 100; 251 135 97; 254 194 135; 252 253 191]);
        case 'cividis_r'
            A = flipud([0 34 78; 18 53 112; 59 73 108; 87 92 109; 112 113 115; 138 134 120; 165 156 116; 194 179 102; 225 204 79; 254 232 56]);
        case 'ylgnbu'
            A = [255 255 217; 237 248 177; 199 233 180; 127 205 187; 65 182 196; 29 145 192; 34 94 168; 37 52 148; 8 29 88];
        otherwise
            error('fkcl:cmap', 'unknown colour map %s', name);
    end
    A = A / 255; t = linspace(0, 1, size(A, 1)); ti = linspace(0, 1, n);
    cm = [interp1(t, A(:, 1), ti)' interp1(t, A(:, 2), ti)' interp1(t, A(:, 3), ti)'];
end
