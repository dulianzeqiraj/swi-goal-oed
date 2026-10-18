function R = fkcl_run_all(opts)
%FKCL_RUN_ALL  Every computation and figure of the Fushe-Kuqe chloride study, in MATLAB R2026b.
%
%   R = FKCL_RUN_ALL() runs, in order,
%     1 the hydrochemistry of the four analyses (seawater fraction, ion exchange, BEX, trend);
%     2 the areal chloride model and its calibration (20 000 prior draws, importance weights);
%     3 the posterior ensemble (2 000 members) and the chloride maps;
%     4 the goal-oriented chloride sampling design (first- and second-aquifer goals);
%     5 the Henry check of the section solver and the variable-density sections A-A';
%     6 the eight figures, and a text report that compares the numbers with the Python reference.
%   By default the random inputs of the Python run are read from results/ (prior draws and the
%   posterior resample), so the numbers coincide with those of the manuscript. Options (struct):
%     N, M          ensemble sizes (20000, 2000)
%     src           'python' (default when the CSV files exist) or an integer seed
%     sections      'all' (default: P5, P50, P95 at 100 x 5 m, P50 at 50 x 4 m, alpha_T 0.1 and 3 m),
%                   'quick' (P50 at 100 x 5 m only) or 'none'
%     figures       true (default) or a vector of figure numbers
%   Run time in MATLAB: about 4 minutes without the sections; the sections add 10-20 minutes.
%   Outputs: results_matlab/ (MAT file, CSV tables, report) and figures_matlab/. The figures can be
%   redrawn from the saved results without rerunning:  fkcl_figures(load('.../fkcl_results.mat'))
%
%   Requirements: base MATLAB (R2019b or newer; written and checked for R2026b). No toolboxes.
%   GNU Octave 8 runs everything as well, with the workbook sheets exported to TSV.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 1, opts = struct(); end
    C = fkcl_config();
    if isfield(opts, 'tsvdir'), C.tsvdir = opts.tsvdir; end
    def = struct('N', 20000, 'M', 2000, 'sections', 'all', 'figures', 1:8);
    if exist(fullfile(C.results, 'calib_prior_draws.csv'), 'file'), def.src = 'python'; else, def.src = 11; end
    fn = fieldnames(def);
    for q = 1:numel(fn), if ~isfield(opts, fn{q}), opts.(fn{q}) = def.(fn{q}); end, end
    if ~exist(C.out, 'dir'), mkdir(C.out); end
    t0 = tic;
    fprintf('[1] data and hydrochemistry\n');
    D = fkcl_read_data(C); H = fkcl_hydrochem(C, D);
    fprintf('    seawater fraction %%: %s  |  BEX meq/L: %s\n', sprintf('%.2f ', 100 * H.f), sprintf('%.2f ', H.BEX));
    fprintf('[2] areal model and calibration (N = %d)\n', opts.N);
    m = fkcl_model_init(C, D);
    fprintf('    %d cells in the coastal sector, %d sea-contact cells\n', nnz(m.valid), numel(m.sea_idx));
    Cal = fkcl_calibrate(m, opts.N, opts.src);
    fprintf('    effective sample size %.0f\n', Cal.ess);
    fprintf('[3] posterior ensemble (M = %d)\n', opts.M);
    Post = fkcl_posterior(m, Cal, opts.M, opts.src);
    fprintf('    area with Cl > 250 mg/L, km2 (5/50/95 %%): upper %s | middle %s | base %s | wedge %s\n', ...
            sprintf('%.1f ', Post.area_q(:, 1)), sprintf('%.1f ', Post.area_q(:, 2)), sprintf('%.1f ', Post.area_q(:, 3)), sprintf('%.1f ', Post.area_q(:, 4)));
    fprintf('[4] chloride sampling design\n');
    rng(3);
    Des.sh = fkcl_design(m, D, Post, 'sh'); Des.mid = fkcl_design(m, D, Post, 'mid');
    fprintf('    best single sample %s (%.2f nats); best triple %s\n', Des.sh.labels{Des.sh.top(1)}, Des.sh.single(Des.sh.top(1)), strjoin(Des.sh.k(3).exhaustive.sites, ', '));
    fprintf('[5] variable-density sections\n');
    [toeH, ~] = fkcl_henry_check(41, 21);
    fprintf('    Henry 41 x 21 toe %.4f m (repository solver 1.3918 m)\n', toeH);
    Sec = struct('henry_toe', toeH);
    if ~strcmpi(opts.sections, 'none')
        [~, ord] = sort(Post.area(:, 4)); Mn = numel(ord);
        pick = struct('p05', ord(floor(0.05 * Mn) + 1), 'p50', ord(floor(0.5 * Mn) + 1), 'p95', ord(floor(0.95 * Mn) + 1));
        % many members share a wedge area and the two sort routines break ties differently, so with
        % the Python inputs the members of the Python run are used (0-based indices in the summary)
        js = fullfile(C.results, 'section_summary.json');
        if ischar(opts.src) && strcmpi(opts.src, 'python') && exist(js, 'file')
            J = jsondecode(fileread(js)); tg = fieldnames(pick);
            for q = 1:numel(tg), pick.(tg{q}) = J.runs.(tg{q}).index + 1; end
        end
        jobs = {'p50', pick.p50, struct()};
        if strcmpi(opts.sections, 'all')
            jobs = [jobs; {'p05', pick.p05, struct(); 'p95', pick.p95, struct(); ...
                     'p50_fine', pick.p50, struct('dxs', 50, 'dzs', 4); 'aT01', pick.p50, struct('aT', 0.1); 'aT3', pick.p50, struct('aT', 3)}];
        end
        for q = 1:size(jobs, 1)
            tq = tic;
            S = fkcl_section(m, fkcl_member(Cal.P, Post.idx(jobs{q, 2})), jobs{q, 3});
            S.member = jobs{q, 2};
            Sec.(jobs{q, 1}) = S;
            fprintf('    %-9s toe VD %.0f m, sharp interface %.0f m, w_sim %.1f m, gap %.1e (%.0f s)\n', jobs{q, 1}, S.toe_vd, S.toe_strack, S.w_sim, S.s.gap, toc(tq));
        end
        if ~isfield(Sec, 'p50_fine') && isfield(Sec, 'p50'), Sec.p50_fine = Sec.p50; end
        if ~isfield(Sec, 'p05') && isfield(Sec, 'p50'), Sec.p05 = Sec.p50; Sec.p95 = Sec.p50; end
    end
    R = struct('C', C, 'D', D, 'H', H, 'm', m, 'Cal', Cal, 'Post', Post, 'Des', Des, 'Sec', Sec, 'opts', opts);
    write_outputs(R);
    if ~isempty(opts.figures) && ~isequal(opts.figures, false)
        fprintf('[6] figures -> %s\n', C.figdir);
        figs = opts.figures; if isequal(figs, true), figs = 1:8; end
        if strcmpi(opts.sections, 'none'), figs = setdiff(figs, 6); end
        fkcl_figures(R, figs);
    end
    fprintf('done in %.0f s\n', toc(t0));
end

function write_outputs(R)
    C = R.C; out = C.out;
    % hydrochemistry table
    H = R.H; fid = fopen(fullfile(out, 'hydrochem.csv'), 'w');
    fprintf(fid, 'well,f_pct,dNa,dCa,dMg,dK,dSO4,NaCl_molar,revelle,BEX,class\n');
    for k = 1:numel(H.well)
        fprintf(fid, '%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%s\n', H.well{k}, 100 * H.f(k), H.dNa(k), H.dCa(k), ...
                H.dMg(k), H.dK(k), H.dSO4(k), H.NaCl(k), H.revelle(k), H.BEX(k), H.class{k});
    end
    fclose(fid);
    % per-cell posterior products
    c = R.Post.cells; m = R.m; fnm = fieldnames(c);
    fid = fopen(fullfile(out, 'post_cells.csv'), 'w');
    fprintf(fid, 'cell,x_km,y_km,valid,dist_shore_km,cover_m,K_idw'); fprintf(fid, ',%s', fnm{:}); fprintf(fid, '\n');
    for k = 1:m.Nc
        fprintf(fid, '%d,%.3f,%.3f,%d,%.4g,%.4g,%.4g', k, m.cx(k), m.cy(k), m.valid(k), m.dist(k), m.cover(k), m.Kidw(k));
        for q = 1:numel(fnm), fprintf(fid, ',%.5g', c.(fnm{q})(k)); end
        fprintf(fid, '\n');
    end
    fclose(fid);
    % report with the Python reference numbers alongside
    fid = fopen(fullfile(out, 'report.txt'), 'w');
    fprintf(fid, 'Fushe-Kuqe chloride study: MATLAB results (opts.src = %s)\n\n', num2str(R.opts.src));
    fprintf(fid, 'calibration: N = %d, effective sample size %.1f\n', size(R.Cal.S, 1), R.Cal.ess);
    ref = fullfile(C.results, 'calib_summary.json');
    if exist(ref, 'file'), J = jsondecode(fileread(ref)); fprintf(fid, '   Python reference ESS %.1f\n', J.ess); end
    nm = R.Cal.names;
    for k = 1:numel(nm)
        fprintf(fid, '  %-18s posterior 5/50/95 %%: %s', nm{k}, sprintf('%.4g ', R.Cal.post.(nm{k})));
        if exist(ref, 'file'), fprintf(fid, '   | Python: %s', sprintf('%.4g ', fkcl_json(J, 'posterior', nm{k}))); end
        fprintf(fid, '\n');
    end
    fprintf(fid, '\nposterior areas, km2 (5/50/95 %%):\n');
    lab = {'Cl > 250 upper', 'Cl > 250 middle', 'Cl > 250 base', 'seawater wedge'};
    ref2 = fullfile(C.results, 'post_summary.json'); kk = {'Cl_sh', 'Cl_mid', 'Cl_dp', 'wedge'};
    if exist(ref2, 'file'), J2 = jsondecode(fileread(ref2)); end
    for k = 1:4
        fprintf(fid, '  %-16s %s', lab{k}, sprintf('%.2f ', R.Post.area_q(:, k)));
        if exist(ref2, 'file'), fprintf(fid, '  | Python: %s', sprintf('%.2f ', fkcl_json(J2, 'area_km2', kk{k}))); end
        fprintf(fid, '\n');
    end
    fprintf(fid, '\nsampling design (goal: upper-layer area), exact EIG [nats]:\n');
    for k = 1:5
        fprintf(fid, '  k = %d  greedy %.3f (%s)   pairwise %.3f (%s)\n', k, R.Des.sh.k(k).greedy.eig_exact, strjoin(R.Des.sh.k(k).greedy.sites, ' '), ...
                R.Des.sh.k(k).pair.eig_exact, strjoin(R.Des.sh.k(k).pair.sites, ' '));
    end
    fprintf(fid, '  exhaustive pair %s %.3f, triple %s %.3f; published sites in the sector %.3f\n', strjoin(R.Des.sh.k(2).exhaustive.sites, ' '), ...
            R.Des.sh.k(2).exhaustive.eig_exact, strjoin(R.Des.sh.k(3).exhaustive.sites, ' '), R.Des.sh.k(3).exhaustive.eig_exact, R.Des.sh.published.eig_exact);
    fprintf(fid, '  Spearman, linear vs exact EIG of single samples: %.3f (upper goal), %.3f (second-aquifer goal)\n', R.Des.sh.spearman_single, R.Des.mid.spearman_single);
    fprintf(fid, '\nsection solver, Henry 41 x 21 toe: %.4f m (repository solver 1.3918 m)\n', R.Sec.henry_toe);
    f = fieldnames(R.Sec);
    for q = 1:numel(f)
        if isstruct(R.Sec.(f{q}))
            S = R.Sec.(f{q}); fprintf(fid, '  %-9s Qin %.2f m2/d, toe VD %.0f m, sharp %.0f m, w_sim %.1f m, w %.1f m\n', f{q}, S.Qin, S.toe_vd, S.toe_strack, S.w_sim, S.w);
        end
    end
    fclose(fid);
    Rs = R; Rs.Post = rmfield(Rs.Post, {'Cl_sh', 'Cl_mid', 'Cl_dp', 'h', 'zeta', 'wedge'});
    if isfield(Rs, 'Sec')
        f = fieldnames(Rs.Sec);
        keep = {'xe', 'ze', 'xc', 'zc', 'nx', 'nz', 'gap'};          % enough to redraw Fig. 6
        for q = 1:numel(f)
            if isstruct(Rs.Sec.(f{q})) && isfield(Rs.Sec.(f{q}), 's')
                s0 = Rs.Sec.(f{q}).s; s1 = struct();
                for k = 1:numel(keep), if isfield(s0, keep{k}), s1.(keep{k}) = s0.(keep{k}); end, end
                Rs.Sec.(f{q}).s = s1;
            end
        end
    end
    save(fullfile(out, 'fkcl_results.mat'), '-struct', 'Rs', '-v7');
end
