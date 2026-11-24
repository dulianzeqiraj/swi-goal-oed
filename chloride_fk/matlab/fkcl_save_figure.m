function fkcl_save_figure(f, folder, name)
%FKCL_SAVE_FIGURE  Save a figure as PNG (600 dpi) and PDF (vector) with EXPORTGRAPHICS when
%   available (MATLAB R2020a or newer), and with PRINT otherwise (GNU Octave).
    if ~exist(folder, 'dir'), mkdir(folder); end
    png = fullfile(folder, [name '.png']); pdf = fullfile(folder, [name '.pdf']);
    if exist('exportgraphics', 'file') == 2 || exist('exportgraphics', 'builtin') == 5
        exportgraphics(f, png, 'Resolution', 600);
        exportgraphics(f, pdf, 'ContentType', 'vector');
    else
        print(f, png, '-dpng', '-r300');
        print(f, pdf, '-dpdf');
    end
end
