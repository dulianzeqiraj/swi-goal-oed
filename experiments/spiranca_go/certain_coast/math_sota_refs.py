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
    # 4. initial state
    'B1': '(Carrillo et al., 2024; Calvello et al., 2026)',
    'B1frame': '(Calvello et al., 2025)',
    'B1small': '(Al-Ghattas and Sanz-Alonso, 2024)',
    'B2': '(Cartis et al., 2024)',
    'B2lm': '(Bergou et al., 2016)',
    'B3': '(Hartland et al., 2023; Kim et al., 2023)',
    'B3warn': '(Henneking et al., 2026)',
    # 5. propagation
    'B4': '(for groundwater flow with random coefficients, Istratuca and Teckentrup, 2025)',
    'B4smooth': '(Haji-Ali et al., 2022; Bayer et al., 2024)',
    'B5': '(Peherstorfer et al., 2016; Gruber et al., 2023)',
    'B6': '(Trémolet, 2007)',
    'B6cov': '(Babyale et al., 2025)',
    'B6limit': '(Laloyaux et al., 2020)',
    'B6hydro': '(Renard et al., 2010)',
    'B7': '(Hoyos, 2025)',
    'B7hydro': '(Jachens et al., 2020)',
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
    'Al-Ghattas, O., & Sanz-Alonso, D. (2024). Non-asymptotic analysis of ensemble Kalman updates: effective dimension and localization. Information and Inference: A Journal of the IMA 13(1), iaad043. https://doi.org/10.1093/imaiai/iaad043',
    'Babyale, S. R., Mead, J., Calhoun, D., & Azike, P. O. (2025). Model error covariance estimation for weak constraint variational data assimilation. SIAM/ASA Journal on Uncertainty Quantification 13(4), 1828–1861. https://doi.org/10.1137/24M1695889',
    'Bayer, C., Ben Hammouda, C., & Tempone, R. (2024). Multilevel Monte Carlo with numerical smoothing for robust and efficient computation of probabilities and densities. SIAM Journal on Scientific Computing 46(3), A1514–A1548. https://doi.org/10.1137/22M1495718',
    'Bergou, E., Gratton, S., & Vicente, L. N. (2016). Levenberg–Marquardt methods based on probabilistic gradient models and inexact subproblem solution, with application to data assimilation. SIAM/ASA Journal on Uncertainty Quantification 4(1), 924–951. https://doi.org/10.1137/140974687',
    'Calvello, E., Monmarché, P., Stuart, A. M., & Vaes, U. (2026). Accuracy of the ensemble Kalman filter in the near-linear setting. SIAM Journal on Numerical Analysis 64(2), 391–429. https://doi.org/10.1137/25M1732544',
    'Calvello, E., Reich, S., & Stuart, A. M. (2025). Ensemble Kalman methods: a mean-field perspective. Acta Numerica 34, 123–291. https://doi.org/10.1017/S0962492924000060',
    'Carrillo, J. A., Hoffmann, F., Stuart, A. M., & Vaes, U. (2024). The mean-field ensemble Kalman filter: near-Gaussian setting. SIAM Journal on Numerical Analysis 62(6), 2549–2587. https://doi.org/10.1137/24M1628207',
    'Cartis, C., Kaouri, M. H., Lawless, A. S., & Nichols, N. K. (2024). Convergent least-squares optimization methods for variational data assimilation. Optimization 73(11), 3451–3485. https://doi.org/10.1080/02331934.2024.2390119',
    'Evensen, G. (1994). Sequential data assimilation with a nonlinear quasi-geostrophic model using Monte Carlo methods to forecast error statistics. Journal of Geophysical Research: Oceans 99(C5), 10143–10162. https://doi.org/10.1029/94JC00572',
    'Giles, M. B. (2008). Multilevel Monte Carlo path simulation. Operations Research 56(3), 607–617. https://doi.org/10.1287/opre.1070.0496',
    'Giles, M. B. (2015). Multilevel Monte Carlo methods. Acta Numerica 24, 259–328. https://doi.org/10.1017/S096249291500001X',
    'Gruber, A., Gunzburger, M., Ju, L., Lan, R., & Wang, Z. (2023). Multifidelity Monte Carlo estimation for efficient uncertainty quantification in climate-related modeling. Geoscientific Model Development 16(4), 1213–1229. https://doi.org/10.5194/gmd-16-1213-2023',
    'Haji-Ali, A.-L., Spence, J., & Teckentrup, A. L. (2022). Adaptive multilevel Monte Carlo for probabilities. SIAM Journal on Numerical Analysis 60(4), 2125–2149. https://doi.org/10.1137/21M1447064',
    'Hartland, T., Stadler, G., Perego, M., Liegeois, K., & Petra, N. (2023). Hierarchical off-diagonal low-rank approximation of Hessians in inverse problems, with application to ice sheet model initialization. Inverse Problems 39(8), 085006. https://doi.org/10.1088/1361-6420/acd719',
    'Henneking, S., Venkat, S., & Ghattas, O. (2026). Goal-oriented real-time Bayesian inference for linear autonomous dynamical systems with application to digital twins for tsunami early warning. Journal of Computational Physics 552, 114682. https://doi.org/10.1016/j.jcp.2026.114682',
    'Hoyos, M. (2025). Estimation bias in the Ornstein–Uhlenbeck process with flow data. Econometric Reviews 44(9), 1411–1435. https://doi.org/10.1080/07474938.2025.2515518',
    'Istratuca, A., & Teckentrup, A. L. (2025). Smoothed circulant embedding with applications to multilevel Monte Carlo methods for PDEs with random coefficients. IMA Journal of Numerical Analysis 45(5), 3138–3178. https://doi.org/10.1093/imanum/drae102',
    'Jachens, E. R., Rupp, D. E., Roques, C., & Selker, J. S. (2020). Recession analysis revisited: impacts of climate on parameter estimation. Hydrology and Earth System Sciences 24(3), 1159–1170. https://doi.org/10.5194/hess-24-1159-2020',
    'Kim, K.-T., Villa, U., Parno, M., Marzouk, Y., Ghattas, O., & Petra, N. (2023). hIPPYlib-MUQ: a Bayesian inference software framework for integration of data with complex predictive models under uncertainty. ACM Transactions on Mathematical Software 49(2), 1–31. https://doi.org/10.1145/3580278',
    'Laloyaux, P., Bonavita, M., Chrust, M., & Gürol, S. (2020). Exploring the potential and limitations of weak-constraint 4D-Var. Quarterly Journal of the Royal Meteorological Society 146(733), 4067–4082. https://doi.org/10.1002/qj.3891',
    'Peherstorfer, B., Willcox, K., & Gunzburger, M. (2016). Optimal model management for multifidelity Monte Carlo estimation. SIAM Journal on Scientific Computing 38(5), A3163–A3194. https://doi.org/10.1137/15M1046472',
    'Renard, B., Kavetski, D., Kuczera, G., Thyer, M., & Franks, S. W. (2010). Understanding predictive uncertainty in hydrologic modeling: the challenge of identifying input and structural errors. Water Resources Research 46(5). https://doi.org/10.1029/2009WR008328',
    'Spantini, A., Baptista, R., & Marzouk, Y. (2022). Coupling techniques for nonlinear ensemble filtering. SIAM Review 64(4), 921–953. https://doi.org/10.1137/20M1312204',
    'Stuart, A. M. (2010). Inverse problems: a Bayesian perspective. Acta Numerica 19, 451–559. https://doi.org/10.1017/S0962492910000061',
    'Trémolet, Y. (2007). Model-error estimation in 4D-Var. Quarterly Journal of the Royal Meteorological Society 133(626), 1267–1280. https://doi.org/10.1002/qj.94',
]

REFERENCES = sorted(REFS_A + REFS_B, key=lambda r: r.lower())
