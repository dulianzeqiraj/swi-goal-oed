function I = prova_index_check(outFile, H)
%PROVA_INDEX_CHECK  Qualitative checks of the robust Gittins index against Fig. 1 of
%   Cohen & Treetanthiploet (2022): gamma - p at p = 0.1, 0.3, 0.5 for counts n up
%   to 1000 (1/sqrt(n) -> 0), for k = 0, 0.2, 0.5, 0.8 at beta = 0.95 and for
%   beta = 0.90, 0.99 at k = 0.5 (remaining horizon H). Saved to outFile.
    if nargin < 2, H = 60; end
    nl = [1 2 5 10 20 50 100 200 500 1000]; pq = [0.1 0.3 0.5];
    ks = [0 0.2 0.5 0.8]; bs = [0.9 0.95 0.99];
    G = nan(numel(ks), numel(bs), numel(nl), 3);
    for a = 1:numel(ks)
        for b = 1:numel(bs)
            if bs(b) ~= 0.95 && ks(a) ~= 0.5, continue; end
            T = robust_gittins_table(ks(a), bs(b), H, 101, nl, 201);
            for c = 1:3, G(a, b, :, c) = interp1(T.p, T.gam, pq(c)) - pq(c); end
        end
    end
    I = struct('n', nl, 'k', ks, 'beta', bs, 'p', pq, 'gamMinusP', G, 'H', H);
    if nargin >= 1 && ~isempty(outFile), save(outFile, 'I', '-v7'); end
end
