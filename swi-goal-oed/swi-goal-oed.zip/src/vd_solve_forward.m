function [U,nF,it] = vd_solve_forward(theta, g, P, tol, maxit)
%VD_SOLVE_FORWARD  Newton solve of the coupled VD system with damping.
    if nargin<4, tol=1e-10; end
    if nargin<5, maxit=60; end
    N=g.N; U=zeros(2*N,1); U(N+1:2*N)=0.1;     % init c=0.1
    nF=inf; it=0;
    for it=1:maxit
        [J,F]=vd_jacobian_fd(U,theta,g,P);
        nF=norm(F);
        if nF<tol, break; end
        dU = -(J\F);
        lam=1.0;
        for s=1:20
            if norm(vd_residual(U+lam*dU,theta,g,P))<nF, break; end
            lam=lam*0.5;
        end
        U = U + lam*dU;
    end
end
