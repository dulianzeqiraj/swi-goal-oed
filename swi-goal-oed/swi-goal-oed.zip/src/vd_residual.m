function F = vd_residual(U, theta, g, P)
%VD_RESIDUAL  Coupled steady variable-density residual F(U;theta), U=[h;c].
%   Equivalent-freshwater-head form (dissertation eqs 1.1/1.2/4.1):
%     flow:      div[ K (grad h + eps c ez) ] = 0          (ez=(0,1) upward)
%     transport: div(q c) - div(phi D grad c) = 0,  q = -K(grad h + eps c ez)
%   Cell-centred finite volume; harmonic-mean face K; first-order upwind
%   advection. BCs (Henry): left x=0 freshwater inflow flux Q with c=0;
%   right x=L sea with c=1 and hydrostatic equivalent-freshwater head;
%   top/bottom no-flow with zero diffusive flux.
%
%   State packing mirrors the Python reference: flat index k=(j-1)*Nx+i,
%   i = column (x), j = row (y).  Returns F of length 2N.
%
%   Author: D. Zeqiraj.  License: MIT.
    Nx=g.Nx; Ny=g.Ny; dx=g.dx; dy=g.dy; N=g.N;
    h = reshape(U(1:N),    Nx, Ny).';   % h(j,i)
    c = reshape(U(N+1:2*N),Nx, Ny).';   % c(j,i)
    K = reshape(P.Kref*exp(theta), Nx, Ny).';
    eps=P.eps; phi=P.phi; D=P.Dmol; Q=P.Q;
    Kf = @(a,b) 2*a.*b./(a+b);          % harmonic mean

    qx = zeros(Ny,Nx+1);  qy = zeros(Ny+1,Nx);
    % x-internal faces (no buoyancy: ez_x=0)
    for j=1:Ny
        for i=1:Nx-1
            Kh = Kf(K(j,i),K(j,i+1));
            qx(j,i+1) = -Kh*(h(j,i+1)-h(j,i))/dx;
        end
    end
    % y-internal faces (buoyancy active)
    for j=1:Ny-1
        for i=1:Nx
            Kh = Kf(K(j,i),K(j+1,i)); cf = 0.5*(c(j,i)+c(j+1,i));
            qy(j+1,i) = -Kh*((h(j+1,i)-h(j,i))/dy + eps*cf);
        end
    end
    % boundary faces (flow)
    for j=1:Ny
        qx(j,1) = Q;                                  % left freshwater inflow (+x)
        hR = eps*(g.Ly - g.yc(j));                    % sea-side equivalent freshwater head
        qx(j,Nx+1) = -K(j,Nx)*(hR - h(j,Nx))/(0.5*dx);
    end
    % top/bottom no-flow: qy(1,:)=qy(Ny+1,:)=0 (already)

    Fh = zeros(Ny,Nx); Fc = zeros(Ny,Nx);
    % FLOW residual: div q = 0
    for j=1:Ny
        for i=1:Nx
            Fh(j,i) = (qx(j,i+1)-qx(j,i))/dx + (qy(j+1,i)-qy(j,i))/dy;
        end
    end
    % TRANSPORT residual: div(q c) - div(phi D grad c) = 0, upwind advection
    for j=1:Ny
        for i=1:Nx
            qw = qx(j,i);
            if qw>0, if i>1, cw=c(j,i-1); else, cw=0.0; end, else, cw=c(j,i); end
            qe = qx(j,i+1);
            if qe>0, ce=c(j,i); else, if i<Nx, ce=c(j,i+1); else, ce=1.0; end, end
            adv = (qe*ce - qw*cw)/dx;
            qs = qy(j,i);
            if qs>0, if j>1, cs=c(j-1,i); else, cs=c(j,i); end, else, cs=c(j,i); end
            qn = qy(j+1,i);
            if qn>0, cn=c(j,i); else, if j<Ny, cn=c(j+1,i); else, cn=c(j,i); end, end
            adv = adv + (qn*cn - qs*cs)/dy;
            if i>1,  cW=c(j,i-1); else, cW=0.0; end
            if i<Nx, cE=c(j,i+1); else, cE=1.0; end
            if j>1,  cS=c(j-1,i); else, cS=c(j,i); end
            if j<Ny, cN=c(j+1,i); else, cN=c(j,i); end
            lap = (cE-2*c(j,i)+cW)/dx^2 + (cN-2*c(j,i)+cS)/dy^2;
            Fc(j,i) = adv - phi*D*lap;
        end
    end
    F = [reshape(Fh.',[],1); reshape(Fc.',[],1)];
end
