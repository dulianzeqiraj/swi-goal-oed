"""The innovation of each of the 32 papers of the state of the art of the proposal (sota_data.py), one sentence each,
for the INNOVATION line of the paper cards in the complete state of the art. Each sentence restates what the card's
summary ('done') says the paper does, as the paper's own contribution; it adds no number and no claim."""

INNOV = {
    1: 'InSAR as a groundwater-management tool: a sustainable yield set from three decades of surface motion and '
       'pumping records, with independent component analysis separating deep and shallow aquifer signals where no '
       'water levels exist.',
    2: 'The switch from elastic to irreversible compaction of an over-drafted aquifer detected from InSAR, GNSS and '
       'wells during a drought, and space geodesy proposed as its early warning.',
    3: 'Geodesy that separates the inelastic from the elastic part of compaction: a sizeable inelastic share at '
       'Groningen and a purely elastic seasonal storage cycle at Norg.',
    4: 'Vertical land motion at tide gauges treated as a rate that changes with fluid withdrawal and earthquakes, with '
       'the projection error of the linear assumption measured.',
    5: 'A near-global probabilistic reconstruction of relative sea level and of its causes since 1900, whose budget '
       'closes only once local land motion is included.',
    6: 'Attribution of the change in extreme sea levels to human forcing from long tide-gauge records, with mean '
       'relative sea level, not surge or tide, identified as the driver.',
    7: 'Physics-based coupled rainfall and surge simulation driven by synthetic tropical and extratropical cyclones, '
       'giving how the return period of a compound flood changes to 2100 and that sea-level rise dominates.',
    8: 'A compound-event risk framework for ports at continental scale, which measures how much ignoring hazard '
       'interactions underestimates the losses.',
    9: 'An asset-level multi-hazard risk analysis of the world\'s ports that adds logistics losses, damage to nearby '
       'infrastructure and trade at risk to physical damage.',
    10: 'Spatially correlated random liquefaction maps: a latent Gaussian process on a geospatial proxy, conditioned on '
        'the areal fraction that liquefied, for the risk of distributed systems.',
    11: 'Traffic noise on a telecom fibre images shallow shear-wave velocity at sub-kilometre scale, and shows that '
        'aftershock shaking varies at the same scale, stronger in soft-sediment micro-basins.',
    12: 'Borehole earthquake and cross-hole data show that shallow shear-wave velocity follows the depth of the water '
        'table, with the largest changes near the surface.',
    13: 'A one-dimensional pile design model calibrated on three-dimensional finite-element analyses and field tests, '
        'reproducing the 3-D results at a fraction of their cost within its calibration space.',
    14: 'A test of soil-reaction curves from uniform soils in layered profiles, with the combinations of very soft clay '
        'and very dense sand where they fail.',
    15: 'A pile model that couples the PISA model with a ratcheting model to predict permanent rotation from a single '
        'storm to the whole lifetime.',
    16: 'Ambient-noise velocity changes as a groundwater monitor: two decades of water-table fluctuations mapped with '
        'better time and depth resolution than wells and InSAR.',
    17: 'Fibre-optic seismic sensing of the unsaturated zone: recharge pulses and the water lost in a drought resolved '
        'from traffic noise.',
    18: 'A record of seismic velocity changes at about 700 stations that separates wet winters, droughts and '
        'postseismic signals, and links site variations to subsidence and uplift.',
    19: 'Conformal risk control: the split-conformal guarantee extended from coverage to the expected value of any '
        'monotone bounded loss, a miss rate included.',
    20: 'Online conformal prediction with decaying step sizes: long-run coverage for arbitrary sequences together '
        'with convergence to the true quantile when the data are i.i.d.',
    21: 'Discounted adaptive online learning that forgets history gracefully, giving instance-dependent coverage when '
        'applied to online conformal prediction in nonstationary environments.',
    22: 'Adaptive conformal sets for multistep-ahead predictions without exchangeability, used inside a '
        'model-predictive controller.',
    23: 'A risk-controlling quantile neural operator that bounds, with probability at least 1 − δ, the expected '
        'fraction of the domain outside its band.',
    24: 'Full conformal prediction computed from existing posterior samples, giving Bayesian models finite-sample '
        'coverage even under misspecification.',
    25: 'Discretisation-invariant neural operators, with universal approximation of continuous nonlinear operators.',
    26: 'Nonlinear PDEs solved and learned as the maximum a posteriori of a Gaussian process at collocation points, with '
        'convergence guarantees and inverse problems solved jointly.',
    27: 'Robust optimisation, Bayesian inference and hypothesis testing in one estimator: the optimal estimate and its '
        'worst-case risk are the centre and radius of a minimum enclosing ball.',
    28: 'A mean-field view that unifies ensemble Kalman methods for filtering, inversion and sampling as particle '
        'approximations, exact in the linear-Gaussian case.',
    29: 'Certified dimension reduction of the likelihood: a ridge approximation chosen by minimising a computable bound '
        'on the KL divergence between the exact and the approximate posterior.',
    30: 'A unified treatment of optimal experimental design, from Bayesian to goal-oriented criteria, and of their '
        'computation.',
    31: 'A combinatorial view of causal structure learning: the Markov equivalence classes data cannot split, how '
        'interventions refine them, and the open design problems with hidden confounders and feedback loops.',
    32: 'Valid treatment effects when the outcome is predicted rather than annotated, through conditional calibration '
        'of the predictor and a causal-lifting constraint that transfers validity from a similar annotated experiment.',
}
