function demo()
%DEMO  Entry point for the public (synthetic) SWI-OED package.
%
%   Runs the linear-Gaussian verification suite that reproduces the
%   Section 6 results of
%
%     Zeqiraj, D. "Goal-Oriented Bayesian Experimental Design for
%     Variable-Density Seawater Intrusion" (in preparation).
%
%   This public package contains the goal-oriented information operator,
%   the cost-aware greedy design, and the facies-pooling phase boundary,
%   all in the exact linear-Gaussian regime. The variable-density adjoint
%   coupling and the field-application drivers are not included in this
%   release; they will be made available upon publication.
%
%   Usage:  >> demo
%
%   Author: D. Zeqiraj.  License: MIT.

    here = fileparts(mfilename('fullpath'));
    addpath(fullfile(here, '..', 'src'));

    fprintf('====================================================\n');
    fprintf(' SWI-OED (public) — linear-Gaussian verification\n');
    fprintf('====================================================\n\n');

    fprintf('[1/2] Goal-oriented operator (Lemma 1)\n');
    demo_synthetic();

    fprintf('\n[2/2] Poolability phase boundary (Lemma 2)\n');
    demo_phase_boundary();

    fprintf('\nDone. See src/ for the operators; README.md for details.\n');
end
