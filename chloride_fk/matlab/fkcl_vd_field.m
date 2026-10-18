function F = fkcl_vd_field(s, v)
%FKCL_VD_FIELD  Map a vector over the active cells of a section onto the nz x nx grid (NaN outside).
    F = nan(s.nz, s.nx); F(s.act) = v;
end
