function g = make_grid(Nx, Ny, Lx, Ly)
%MAKE_GRID  Rectangular cell-centred grid for the Henry-class domain.
    if nargin < 3, Lx = 2.0; end
    if nargin < 4, Ly = 1.0; end
    g.Nx = Nx; g.Ny = Ny; g.Lx = Lx; g.Ly = Ly;
    g.dx = Lx/Nx; g.dy = Ly/Ny; g.N = Nx*Ny;
    g.xc = ((1:Nx)-0.5)*g.dx;   % cell-centre x
    g.yc = ((1:Ny)-0.5)*g.dy;   % cell-centre y
end
