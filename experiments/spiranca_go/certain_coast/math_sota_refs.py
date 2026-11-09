"""Citations and reference list for build_math_sota.py. Every reference was checked in Crossref (title, authors,
journal, volume, pages, DOI); see the commit message of the build for the date of the check."""
from collections import defaultdict

# keys used in the text; '' means no citation is shown at that place
CITE = defaultdict(str)

REFERENCES = [
    'Carrillo, J. A., Hoffmann, F., Stuart, A. M., & Vaes, U. (2024). The mean-field ensemble Kalman filter: near-Gaussian setting. SIAM Journal on Numerical Analysis 62(6), 2549–2587. https://doi.org/10.1137/24M1628207',
    'Rodriguez-Iturbe, I., Porporato, A., Ridolfi, L., Isham, V., & Cox, D. R. (1999). Probabilistic modelling of water balance at a point: the role of climate, soil and vegetation. Proceedings of the Royal Society A 455(1990), 3789–3805.',
    'Spantini, A., Baptista, R., & Marzouk, Y. (2022). Coupling techniques for nonlinear ensemble filtering. SIAM Review 64(4), 921–953. https://doi.org/10.1137/20M1312204',
    'Strack, O. D. L. (1976). A single-potential solution for regional interface problems in coastal aquifers. Water Resources Research 12(6), 1165–1174. https://doi.org/10.1029/WR012i006p01165',
]
