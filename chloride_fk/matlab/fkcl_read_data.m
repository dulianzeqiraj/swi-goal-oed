function D = fkcl_read_data(C)
%FKCL_READ_DATA  Read every sheet of Fushe_Kuqe_All_Data.xlsx that the study uses.
%
%   D = FKCL_READ_DATA(C) returns
%     D.B        aquifer polygon, Gauss-Krueger [m] (3411 x 2)
%     D.wells    struct of column vectors: id (cellstr), X, Y [m], K [m/d], NO3, DRASTIC,
%                depth (Piezometric_Level_m, read as the DRASTIC depth to the aquifer top [m]),
%                inside (logical)
%     D.chem     struct: well (cellstr), and one field per analyte [mg/L] (Table 1 of
%                Cenameri & Beqiraj 2016), plus TDS, sw_pct (source value) and position
%     D.trend    struct: well (cellstr), years [1984 1999 2001], Cl [mg/L] (2 x 3)
%     D.facts    cell array {parameter, value, unit} of sheet 7
%     D.shore    shoreline per model row [y_km shore_x_km] (derived/shoreline_rows.csv)
%     D.coast    shoreline polyline [segment x_km y_km] (derived/shoreline_polyline.csv)
%     D.places   struct: name (cellstr), x, y [km]
%     D.x0, D.y0 origin of the local km coordinates (south-west corner of the polygon)

    S3 = fkcl_readcell(C, '3_Boundary_Coords');
    B = cell2num(S3(2:end, 2:3));
    D.B = B(all(isfinite(B), 2), :);
    D.x0 = min(D.B(:, 1)); D.y0 = min(D.B(:, 2));

    S2 = fkcl_readcell(C, '2_All_Wells');
    hdr = cellfun(@char, S2(1, :), 'UniformOutput', false);
    col = @(name) find(strcmp(hdr, name), 1);
    body = S2(2:end, :);
    body = body(~cellfun(@isempty, body(:, 1)), :);
    W.id = cellfun(@any2str, body(:, col('Well_ID')), 'UniformOutput', false);
    W.X = cell2num(body(:, col('X_GaussKruger')));
    W.Y = cell2num(body(:, col('Y_GaussKruger')));
    W.K = cell2num(body(:, col('K_m_per_day')));
    W.NO3 = cell2num(body(:, col('NO3_mg_per_L')));
    W.DRASTIC = cell2num(body(:, col('DRASTIC_Index')));
    W.depth = cell2num(body(:, col('Piezometric_Level_m')));
    W.inside = strcmpi(cellfun(@any2str, body(:, col('Inside_Aquifer')), 'UniformOutput', false), 'YES');
    D.wells = W;

    S5 = fkcl_readcell(C, '5_Cenameri2016_Chemistry');
    r0 = find(cellfun(@(v) ischar(v) && strcmp(v, 'Well_no'), S5(:, 1)), 1);
    h5 = cellfun(@any2str, S5(r0, :), 'UniformOutput', false);
    rows = S5(r0 + 1:r0 + 4, :);
    ch.well = cellfun(@any2str, rows(:, 1), 'UniformOutput', false);
    map = {'HCO3','HCO3_mg_L'; 'SO4','SO4_mg_L'; 'Cl','Cl_mg_L'; 'Ca','Ca_mg_L'; 'Mg','Mg_mg_L'; ...
           'Na','Na_mg_L'; 'K','K_mg_L'; 'NO3','NO3_mg_L'; 'TDS','Mp_TDS_mg_L'; 'sw_pct','Seawater_fraction_pct'; ...
           'T','T_degC'; 'pH','pH'};
    for q = 1:size(map, 1)
        ch.(map{q, 1}) = cell2num(rows(:, strcmp(h5, map{q, 2})));
    end
    ch.position = cellfun(@any2str, rows(:, strcmp(h5, 'Transect_position')), 'UniformOutput', false);
    D.chem = ch;

    S6 = fkcl_readcell(C, '6_Cenameri2016_Cl_Trend');
    r0 = find(cellfun(@(v) ischar(v) && strcmp(v, 'Well_no'), S6(:, 1)), 1);
    rows = S6(r0 + 1:r0 + 2, :);
    D.trend.well = cellfun(@any2str, rows(:, 1), 'UniformOutput', false);
    D.trend.years = [1984 1999 2001];
    D.trend.Cl = cell2num(rows(:, 2:4));

    S7 = fkcl_readcell(C, '7_Cenameri2016_SWI_Facts');
    r0 = find(cellfun(@(v) ischar(v) && strcmp(v, 'Parameter'), S7(:, 1)), 1);
    D.facts = S7(r0 + 1:end, 1:3);

    D.shore = fkcl_readnum(fullfile(C.derived, 'shoreline_rows.csv'));
    D.coast = fkcl_readnum(fullfile(C.derived, 'shoreline_polyline.csv'));
    txt = fileread(fullfile(C.derived, 'places.csv'));
    L = regexp(txt, '\r?\n', 'split'); L = L(2:end); L = L(~cellfun(@isempty, L));
    D.places.name = cell(numel(L), 1); D.places.x = zeros(numel(L), 1); D.places.y = zeros(numel(L), 1);
    for k = 1:numel(L)
        p = regexp(L{k}, ',', 'split');
        D.places.name{k} = p{1}; D.places.x(k) = str2double(p{2}); D.places.y(k) = str2double(p{3});
    end
end

function v = cell2num(c)
    v = nan(size(c));
    for k = 1:numel(c)
        x = c{k};
        if isnumeric(x) && ~isempty(x), v(k) = double(x);
        elseif ischar(x), v(k) = str2double(x);
        end
    end
end

function s = any2str(x)
    if ischar(x), s = x;
    elseif isnumeric(x) && ~isempty(x), s = num2str(x);
    elseif isempty(x), s = '';
    else, s = char(x);
    end
end
