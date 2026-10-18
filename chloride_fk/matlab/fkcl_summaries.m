function [S, names, mk] = fkcl_summaries(m, o, mk)
%FKCL_SUMMARIES  Summary statistics of one model run (the quantities the calibration compares).
%
%   [S, names, mk] = FKCL_SUMMARIES(m, o) returns the row vector S with
%    1 area250_sh   area with upper-layer Cl > 250 mg/L / polygon area        (target T1 ~ 0.15)
%    2 h_lit        median head, 0.5-2.5 km from the shoreline, y = 30-40 km   (target T2 ~ 3 m)
%    3 f_sw         median upper-layer seawater fraction, same band
%    4 f_c          median upper-layer seawater fraction, 3-6 km               (held-out check, well 340)
%    5 cl_ne        median upper-layer Cl, >= 7 km, y = 36-46 km               (target T3c < 30 mg/L)
%    6 toe_area     area of the seawater wedge at the aquifer base [km2]
%    7 area250_dp   base-layer area with Cl > 250 / polygon area
%    8 fdp_sw       median base-layer seawater fraction, SW band
%    9 clmax_sh     max upper-layer Cl in the transect bands; 10 clmax_dp the same at the base
%   11 fmid_sw      median mid-depth seawater fraction, SW band                 (target T3a ~ 4.7 %)
%   12 clsh_sw, 13 clmid_sw   median Cl in the SW band; 14 area250_mid; 15 fmid_c (held-out)
%   mk holds the band masks; pass it back in to avoid rebuilding them.

    C = m.C;
    if nargin < 3 || isempty(mk)
        sea = m.sea_row(m.aj) & m.valid;
        fs = sea & m.cy >= 30 & m.cy <= 40;
        mk.sw = fs & m.dist >= 0.5 & m.dist <= 2.5;
        mk.c = fs & m.dist >= 3 & m.dist <= 6;
        mk.ne = sea & m.cy >= 36 & m.cy <= 46 & m.dist >= 7;
    end
    v = m.valid; A = m.area / 1e6;
    tr = mk.sw | mk.c;
    S = [sum(o.Cl_sh > C.Cl_lim & v) * A / C.Apoly, ...
         median(o.h(mk.sw)), median(o.f_sh(mk.sw)), median(o.f_sh(mk.c)), median(o.Cl_sh(mk.ne)), ...
         sum(o.wedge & v) * A, sum(o.Cl_dp > C.Cl_lim & v) * A / C.Apoly, median(o.f_dp(mk.sw)), ...
         max([o.Cl_sh(tr); 0]), max([o.Cl_dp(tr); 0]), median(o.f_mid(mk.sw)), ...
         median(o.Cl_sh(mk.sw)), median(o.Cl_mid(mk.sw)), sum(o.Cl_mid > C.Cl_lim & v) * A / C.Apoly, ...
         median(o.f_mid(mk.c))];
    names = {'area250_sh', 'h_lit', 'f_sw', 'f_c', 'cl_ne', 'toe_area_km2', 'area250_dp', 'fdp_sw', ...
             'clmax_sh_transect', 'clmax_dp_transect', 'fmid_sw', 'clsh_sw', 'clmid_sw', 'area250_mid', 'fmid_c'};
end
