function save_figure(f, filename, dpi)
%SAVE_FIGURE  Write a figure to PNG at a given resolution, robustly.
%
%   save_figure(f, filename, dpi)
%
%   Uses exportgraphics where available and falls back to print otherwise.
%   The figure handle is validated first, so a figure that has been closed
%   (for example by clicking the window shut while a script is running)
%   produces a clear message instead of an "Invalid graphics object" error
%   from inside print. The destination folder is created if it is missing.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 3 || isempty(dpi), dpi = 600; end
    if nargin < 1 || isempty(f), f = gcf; end

    if ~(isgraphics(f, 'figure') && isvalid(f))
        error('save_figure:invalidFigure', ...
              ['The figure to be written no longer exists (it may have been ' ...
               'closed while the script was running). Re-run the script and ' ...
               'leave its figure windows alone, or start MATLAB with ' ...
               'set(0,''DefaultFigureVisible'',''off'').']);
    end

    [folder, ~, ext] = fileparts(filename);
    if isempty(ext), filename = [filename '.png']; end
    if ~isempty(folder) && ~isfolder(folder), mkdir(folder); end

    try
        exportgraphics(f, filename, 'Resolution', dpi);
    catch ME
        if exist('exportgraphics', 'file') ~= 2
            % older MATLAB: fall back to print, which takes the stem
            [folder, base, ~] = fileparts(filename);
            print(f, fullfile(folder, base), '-dpng', sprintf('-r%d', dpi));
        else
            rethrow(ME);
        end
    end
end
