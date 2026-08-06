function r2_run_all()
%R2_RUN_ALL  Run every new R2 analysis, with a diary log in r2_results/.
%   Order: cheap data analyses first, physics runs last. Each step is
%   try/catch-isolated so one failure does not kill the batch.
%   Part of the HYDROL82304R1 -> R2 revision. Author: D. Zeqiraj.

    here = fileparts(mfilename('fullpath'));
    outdir = fullfile(here, 'r2_results');
    if ~exist(outdir, 'dir'), mkdir(outdir); end
    logf = fullfile(outdir, 'r2_run_all_log.txt');
    if exist(logf, 'file'), delete(logf); end
    diary(logf); cleanup = onCleanup(@() diary('off'));

    steps = { 'r2_rhoF_uncertainty',            @r2_rhoF_uncertainty;
              'r2_rhoc_sensitivity',            @r2_rhoc_sensitivity;
              'r2_facies_threshold_sensitivity',@r2_facies_threshold_sensitivity;
              'r2_intruded_area',               @r2_intruded_area;
              'r2_fit_extras',                  @r2_fit_extras;
              'r2_phase_boundary_henry',        @r2_phase_boundary_henry;
              'r2_gate2_refine',                @r2_gate2_refine;
              'r2_gate1_floor',                 @r2_gate1_floor;
              'r2_gate1_multidir',              @r2_gate1_multidir };

    tAll = tic;
    for s = 1:size(steps, 1)
        fprintf('\n########################################################\n');
        fprintf('### %d/%d  %s\n', s, size(steps, 1), steps{s, 1});
        fprintf('########################################################\n');
        ts = tic;
        try
            steps{s, 2}();
            fprintf('--- %s OK (%.1f s)\n', steps{s, 1}, toc(ts));
        catch e
            fprintf('--- %s FAILED (%.1f s):\n%s\n', steps{s, 1}, toc(ts), getReport(e, 'extended', 'hyperlinks', 'off'));
        end
    end
    fprintf('\n=== r2_run_all finished in %.1f s ===\n', toc(tAll));
end
