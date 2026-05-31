function [J,F0] = vd_jacobian_fd(U, theta, g, P, eps_fd)
%VD_JACOBIAN_FD  Dense Jacobian dF/dU by finite-difference coloring (Eq.15/S26).
    if nargin<5, eps_fd=1e-7; end
    n = numel(U); F0 = vd_residual(U,theta,g,P); J = zeros(n,n);
    for k=1:n
        d = eps_fd*max(1.0,abs(U(k)));
        Up = U; Up(k)=Up(k)+d;
        J(:,k) = (vd_residual(Up,theta,g,P)-F0)/d;
    end
end
