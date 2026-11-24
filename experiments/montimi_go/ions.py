"""The ion block of the assembled system: seven major ions transported with the salt operator of the step, Gaines-Thomas
exchange of Na, K, Ca, Mg in every cell (local equilibrium, sequential non-iterative coupling), immobile zones as for
the salt. Exchange routines and end-members from GJURMA-GO (../gjurma_go/gjurma_model.py) and PUSI-GO.
The block reads the flow and the salt of the step and writes nothing back: it is one-way coupled."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'gjurma_go'))
import gjurma_model as G  # noqa: E402

FRESH = G.FRESH.copy()                                   # well 193 (mmol/L)
SEA = G.SEA_MGL * 38.3 / 35.0 * 1.0285 / G.MW            # Adriatic sea water (mmol/L)
LOGK = np.log(G.K_TRUE)
MW = G.MW
SPECIES = G.SPECIES


class IonBlock:
    def __init__(self, m, y):
        self.m = m
        N = m.g.N
        f = np.clip(y[N:], 0.0, 1.0)
        self.c = FRESH[None, :] + f[:, None] * (SEA - FRESH)[None, :]          # mixing initial state (N, 7)
        self.E = np.full(N, m.P['E'])
        self.beta = G.exchanger(self.c, LOGK)
        self.ck = [self.c.copy(), self.c.copy()]
        g = m.g
        self.inl = (g.kind == 3)

    def step(self, lu_c, Q, ghost_sea):
        m, g = self.m, self.m.g
        sea_in = ghost_sea > 0
        new = np.empty_like(self.c)
        for s in range(7):
            gh = np.where(sea_in, SEA[s], 0.0) + np.where(self.inl, FRESH[s], 0.0)
            rhs = m.st_c * self.c[:, s] + m.mc_coef[0] * self.ck[0][:, s] + m.mc_coef[1] * self.ck[1][:, s] \
                - g.Div @ (Q * gh) + m.W_in * FRESH[s]
            new[:, s] = lu_c.solve(rhs)
        # exchange: the exchanger stays during transport, then the cell re-equilibrates at fixed cation totals
        T = G.ZC * new[:, G.IC] + self.E[:, None] * self.beta
        y = G.solve_cations(T, self.E, LOGK, np.maximum(new[:, G.IC], 1e-6), iters=12)
        new[:, G.IC] = y
        self.beta = G.exchanger(new, LOGK)
        self.c = new
        for k in range(2):
            a, b = m.alpha_c[k], m.beta_c[k]
            self.ck[k] = a * self.ck[k] + b * new

    def screen_mgL(self):
        w = self.m.wJ
        return (w @ self.c) * MW
