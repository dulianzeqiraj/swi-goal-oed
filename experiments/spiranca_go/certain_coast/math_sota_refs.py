"""Citations and reference list for build_math_sota.py. Every reference was checked in Crossref (title, authors,
journal, volume, pages or article number, DOI) on 9 November 2026, and each 2023-2026 paper is cited only for what
its abstract (or, for Ciotir et al. 2025, its title) states."""
from collections import defaultdict

# keys used in the text; a missing key shows no citation at that place
CITE = defaultdict(str, {
    # 2. random forcing
    'A1path': '(Fehrman and Gess, 2019)',
    'A1clini': '(Clini, 2023)',
    'A1entropy': '(Fehrman and Gess, 2024; Popat, 2025)',
    'A1stab': '(Vázquez, 2006)',
    'A3': '(He, 2023; Nie et al., 2025)',
    'A2split': '(Bréhier et al., 2024)',
    'A2fem': '(Grillmeier and Grün, 2019)',
    'A2deg': '(Baňas et al., 2024)',
    'A4': '; for the water table, Laio et al., 2009',
    # 3. boundaries
    'A6robin': 'Ciotir et al. (2025)',
    'A6when': 'Peeters and Turnadge (2019)',
    'A5local': '(Müller, 2018)',
    'A5max': '(Antonopoulou et al., 2025)',
    'A6bias': '(Erdal and Cirpka, 2016)',
    'A6da': '(Coulon et al., 2024)',
})

REFS_A = [
    'Antonopoulou, D. C., Farazakis, D., & Karali, G. (2025). Existence of maximal solutions for the financial stochastic Stefan problem of a volatile asset with spread. Stochastic Processes and their Applications 179, 104506. https://doi.org/10.1016/j.spa.2024.104506',
    'Baňas, Ľ., Gess, B., & Vieth, C. (2024). Numerical approximation of singular-degenerate parabolic stochastic partial differential equations. IMA Journal of Numerical Analysis 44(4), 2090–2137. https://doi.org/10.1093/imanum/drad061',
    'Bréhier, C.-E., Cohen, D., & Ulander, J. (2024). Analysis of a positivity-preserving splitting scheme for some semilinear stochastic heat equations. ESAIM: Mathematical Modelling and Numerical Analysis 58(4), 1317–1346. https://doi.org/10.1051/m2an/2024032',
    'Ciotir, I., Goreac, D., Li, J., & Tonnoir, A. (2025). Stochastic porous media equation with Robin boundary conditions, gravity-driven infiltration and multiplicative noise. Journal of Differential Equations 438, 113363. https://doi.org/10.1016/j.jde.2025.113363',
    'Clini, A. (2023). Porous media equations with nonlinear gradient noise and Dirichlet boundary conditions. Stochastic Processes and their Applications 159, 428–498. https://doi.org/10.1016/j.spa.2023.02.007',
    'Coulon, C., White, J. T., Pryet, A., Gatel, L., & Lemieux, J.-M. (2024). An ensemble-based approach for pumping optimization in an island aquifer considering parameter, observation and climate uncertainty. Hydrology and Earth System Sciences 28(1), 303–319. https://doi.org/10.5194/hess-28-303-2024',
    'Erdal, D., & Cirpka, O. A. (2016). Joint inference of groundwater–recharge and hydraulic–conductivity fields from head data using the ensemble Kalman filter. Hydrology and Earth System Sciences 20(1), 555–569. https://doi.org/10.5194/hess-20-555-2016',
    'Fehrman, B., & Gess, B. (2019). Well-posedness of nonlinear diffusion equations with nonlinear, conservative noise. Archive for Rational Mechanics and Analysis 233(1), 249–322. https://doi.org/10.1007/s00205-019-01357-w',
    'Fehrman, B., & Gess, B. (2024). Well-posedness of the Dean–Kawasaki and the nonlinear Dawson–Watanabe equation with correlated noise. Archive for Rational Mechanics and Analysis 248(2), 20. https://doi.org/10.1007/s00205-024-01963-3',
    'Grillmeier, H., & Grün, G. (2019). Nonnegativity preserving convergent schemes for stochastic porous-medium equations. Mathematics of Computation 88(317), 1021–1059. https://doi.org/10.1090/mcom/3372',
    'He, Y. (2023). On the convergence rate of the splitting-up scheme for rough partial differential equations. Computers & Mathematics with Applications 139, 1–6. https://doi.org/10.1016/j.camwa.2023.03.001',
    'Laio, F., Tamea, S., Ridolfi, L., D\'Odorico, P., & Rodriguez-Iturbe, I. (2009). Ecohydrology of groundwater-dependent ecosystems: 1. Stochastic water table dynamics. Water Resources Research 45(5). https://doi.org/10.1029/2008WR007292',
    'Müller, M. S. (2018). A stochastic Stefan-type problem under first-order boundary conditions. The Annals of Applied Probability 28(4), 2335–2369. https://doi.org/10.1214/17-AAP1359',
    'Nie, D., Sun, J., & Deng, W. (2025). Numerical approximation for stochastic nonlinear fractional diffusion equation driven by rough noise. ESAIM: Mathematical Modelling and Numerical Analysis 59(1), 389–418. https://doi.org/10.1051/m2an/2024080',
    'Peeters, L., & Turnadge, C. (2019). When to account for boundary conditions in estimating hydraulic properties from head observations? Groundwater 57(3), 351–355. https://doi.org/10.1111/gwat.12880',
    'Popat, S. (2025). Well-posedness of the generalised Dean–Kawasaki equation with correlated noise on bounded domains. Stochastic Processes and their Applications 179, 104503. https://doi.org/10.1016/j.spa.2024.104503',
    'Rodriguez-Iturbe, I., Porporato, A., Ridolfi, L., Isham, V., & Cox, D. R. (1999). Probabilistic modelling of water balance at a point: the role of climate, soil and vegetation. Proceedings of the Royal Society A 455(1990), 3789–3805.',
    'Strack, O. D. L. (1976). A single-potential solution for regional interface problems in coastal aquifers. Water Resources Research 12(6), 1165–1174. https://doi.org/10.1029/WR012i006p01165',
    'Vázquez, J. L. (2006). The Porous Medium Equation: Mathematical Theory. Oxford University Press. https://doi.org/10.1093/acprof:oso/9780198569039.001.0001',
]

REFS_B = [
    'Carrillo, J. A., Hoffmann, F., Stuart, A. M., & Vaes, U. (2024). The mean-field ensemble Kalman filter: near-Gaussian setting. SIAM Journal on Numerical Analysis 62(6), 2549–2587. https://doi.org/10.1137/24M1628207',
    'Spantini, A., Baptista, R., & Marzouk, Y. (2022). Coupling techniques for nonlinear ensemble filtering. SIAM Review 64(4), 921–953. https://doi.org/10.1137/20M1312204',
]

REFERENCES = sorted(REFS_A + REFS_B, key=lambda r: r.lower())
