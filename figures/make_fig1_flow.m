function make_fig1_flow(outPath)
%MAKE_FIG1_FLOW  Figure 1, the computational workflow, at journal print size.
%
%   Reproduces the flow chart of the article: the facies-conditional prior and the
%   variable-density forward model feed the discrete adjoint; one coupled Jacobian
%   yields the two sensitivities from two solves sharing its transpose; these
%   assemble the information operator, the expected information gain and the joint
%   objective. The notation is that of Table 1 of the article.
%
%   Author: D. Zeqiraj.  License: MIT.

    if nargin < 1 || isempty(outPath), outPath = 'Fig1_Workflow.png'; end

    W = 9.5; H = 14.8;                       % cm, the printed size
    f = figure('Color','w','Units','centimeters','Position',[2 2 W H], ...
               'PaperUnits','centimeters','PaperPosition',[0 0 W H],'PaperSize',[W H]);
    ax = axes('Position',[0 0 1 1]); axis(ax,[0 100 0 100]); axis off; hold on

    cOrange = [0.99 0.91 0.80];  eOrange = [0.85 0.62 0.30];
    cBlue   = [0.87 0.91 0.96];  eBlue   = [0.55 0.65 0.80];
    cGreen  = [0.88 0.94 0.86];  eGreen  = [0.55 0.72 0.52];
    cPink   = [0.98 0.89 0.90];  ePink   = [0.82 0.55 0.58];

    function box(x, y, w, h, fc, ec, head, body, fsBody)
        rectangle('Position',[x y w h],'FaceColor',fc,'EdgeColor',ec,'LineWidth',0.9);
        text(x+w/2, y+h*0.70, head, 'HorizontalAlignment','center', ...
             'VerticalAlignment','middle','FontSize',8,'FontWeight','bold', ...
             'FontName','Arial','Interpreter','none');
        if ~isempty(body)
            text(x+w/2, y+h*0.30, body, 'HorizontalAlignment','center', ...
                 'VerticalAlignment','middle','FontSize',fsBody, ...
                 'Interpreter','latex');
        end
    end

    function arrow(x, y0, y1)
        plot([x x],[y0 y1],'-','Color',[0.35 0.35 0.35],'LineWidth',1.0);
        patch(x+[0 -1.6 1.6], y1+[0 2.6 2.6], [0.35 0.35 0.35], 'EdgeColor','none');
    end

    L = 6; Wb = 88;

    box(L, 89.5, Wb, 9.0, cOrange, eOrange, 'Facies prior', ...
        '$\Gamma_F = \Gamma_W + \rho_F\,\Gamma_X$', 9);
    arrow(50, 89.5, 85.8);

    box(L, 76.5, Wb, 9.0, cBlue, eBlue, 'Variable-density forward model', ...
        '$\mathcal{R}(u;\theta,d) = 0$', 9);
    arrow(50, 76.5, 72.8);

    box(L, 63.5, Wb, 9.0, cBlue, eBlue, 'Discrete adjoint', ...
        'assemble $J$ by sparsity-colored finite differences', 7.5);
    arrow(50, 63.5, 59.8);

    box(L, 49.0, 42.5, 11.0, cGreen, eGreen, 'Observation adjoint', ...
        '$J^{\top}\zeta = (\partial\mathcal{O}/\partial u)^{\top} \Rightarrow G_F$', 8);
    box(51.5, 49.0, 42.5, 11.0, cGreen, eGreen, 'Goal adjoint', ...
        '$J^{\top}\xi = (\partial Q/\partial u)^{\top} \Rightarrow H_F$', 8);
    arrow(50, 49.0, 45.3);

    box(L, 31.0, Wb, 14.0, cBlue, eBlue, 'Goal-oriented information operator', ...
        ['$\mathcal{I}_F = H_F\,\Gamma_F\,G_F^{\top}' ...
         '\left(G_F\,\Gamma_F\,G_F^{\top}+\Gamma_n\right)^{-1}G_F\,\Gamma_F\,H_F^{\top}$'], 7.5);
    arrow(50, 31.0, 27.3);

    box(L, 16.0, Wb, 11.0, cBlue, eBlue, 'Expected information gain', ...
        '$\mathrm{EIG}_Q = -\frac{1}{2}\log \left(1-\mathcal{I}_F/\sigma_0^{2}\right)$', 9);
    arrow(50, 16.0, 12.3);

    box(L, 1.0, Wb, 11.0, cPink, ePink, 'Joint monitoring-recharge objective', ...
        '$U(d) = \mathrm{E}_F \left[\mathrm{EIG}_Q\right] - \lambda \, \mathcal{C}(d)$', 9);

    try, exportgraphics(f, outPath, 'Resolution', 600);
    catch, print(f, outPath(1:end-4), '-dpng','-r600'); end
    fprintf('written: %s\n', outPath);
end
