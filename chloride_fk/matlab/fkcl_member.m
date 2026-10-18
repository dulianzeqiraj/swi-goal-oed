function p = fkcl_member(P, i)
%FKCL_MEMBER  Parameter set i of an ensemble struct (rows = members).
    fn = fieldnames(P);
    for q = 1:numel(fn)
        v = P.(fn{q});
        if strcmp(fn{q}, 'theta'), p.theta = v(i, :)'; else, p.(fn{q}) = v(i); end
    end
end
