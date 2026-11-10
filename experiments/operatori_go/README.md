# OPERATORI-GO: boundary conditions as operators

Synthetic checks for the working document *Boundary conditions as operators*
(`docs/research_notes/Zeqiraj_Boundary_Conditions_as_Operators.docx`). It revises the boundary part of
the deterministic-first treatment of boundary and initial conditions, using the operator-learning study of
de Hoop, Huang, Qian and Stuart (2022, *J. Mach. Learn.* 1(3): 299–341).

Dimensionless coastal strip: L = 1, D = 1, sea at x = 0, no flow at x = 1, τ₁ = 4/π². Sea-level residual:
Ornstein–Uhlenbeck with τ_int = 0.02 τ₁. Tolerance δ = 0.25 s.

| Check | What it tests | Main number |
|---|---|---|
| 1 | Input dimension set by the aquifer (Proposition A); operator-weighted modes (Proposition C) | 46 modes at x = 0.1 vs 1010 for 99 % input PCA; 2–3 vs 89–219 modes in the shell |
| 2 | Compute, do not learn, a linear boundary operator (Proposition B) | learned error = computed × √(1 + r/(N−r−1)), within 0.1 % from N = 460 |
| 3 | Kinked boundary map (capped recharge) (Proposition D) | learned maps level off or decay like N^-0.16; cap on the input is exact |
| 4 | Certified guard and sharp alarm (Proposition E) | alarm 0.9 % in distribution, 99.98 % at doubled amplitude |

Run:

    python operatori_exp.py operatori_results.json        # numpy, about 15 s
    python operatori_figs.py operatori_results.json figs
    python build_operatori_doc.py operatori_results.json figs ../../docs/research_notes/Zeqiraj_Boundary_Conditions_as_Operators.docx
