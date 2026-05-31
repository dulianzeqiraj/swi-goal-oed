function GamF = facies_prior(rhoF, blocks, cross)
%FACIES_PRIOR  Facies-stratified prior covariance Gamma(rhoF) = D + rhoF*C.
%
%   GamF = FACIES_PRIOR(rhoF, blocks, cross)
%
%   Builds the facies-conditional prior covariance parameterized by a single
%   cross-facies correlation rhoF in [0,1] (Eq. 11):
%       Gamma(rhoF) = D + rhoF * C
%   where D is the block-diagonal within-facies covariance and C collects the
%   cross-facies blocks. rhoF -> 1 recovers the pooled (facies-blind) prior.
%
%   INPUTS
%     rhoF   : scalar cross-facies correlation in [0,1]
%     blocks : 1-by-K cell array of within-facies covariance blocks (each SPD);
%              D = blkdiag(blocks{:})
%     cross  : n-by-n symmetric matrix of cross-facies couplings (zero on the
%              diagonal blocks). If omitted, a unit-correlation coupling between
%              facies block means is used (rank structure for a clean phase
%              boundary; see demo_phase_boundary).
%
%   OUTPUT
%     GamF   : n-by-n prior covariance, guaranteed SPD for rhoF in [0,1] when
%              built from the provided factor model.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    D = blkdiag(blocks{:});
    n = size(D, 1);
    if nargin < 3 || isempty(cross)
        % Default: a low-rank cross coupling that is PSD-compatible with D.
        K  = numel(blocks);
        sz = cellfun(@(b) size(b,1), blocks);
        u  = zeros(n, 1); idx = 1;
        for k = 1:K
            u(idx:idx+sz(k)-1) = 1/sqrt(sz(k));
            idx = idx + sz(k);
        end
        cross = (u*u') - blkdiag_mask(sz) .* (u*u');  % off-diagonal blocks only
    end
    GamF = D + rhoF * cross;
    GamF = 0.5 * (GamF + GamF');
end

function Mblk = blkdiag_mask(sz)
%BLKDIAG_MASK  1 on the diagonal blocks, 0 elsewhere.
    n = sum(sz); Mblk = zeros(n);
    idx = 1;
    for k = 1:numel(sz)
        r = idx:idx+sz(k)-1;
        Mblk(r, r) = 1;
        idx = idx + sz(k);
    end
end
