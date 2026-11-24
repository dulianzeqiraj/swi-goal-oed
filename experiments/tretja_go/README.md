# TRETJA-GO: non-equilibrium calcite dissolution in the coastal mixing zone

*Tretja* means "the dissolution". In the freshwater–seawater mixing zone of a coastal aquifer, both end-member
waters are in equilibrium with calcite. Their mixtures are not: the saturation state is a nonlinear function of the
mixing fraction (mixing corrosion), so calcite dissolves. How much dissolves depends on non-equilibrium kinetics:
- a field rate prefactor that is uncertain by orders of magnitude (the gap between laboratory and field rates);
- a nonlinear rate law that changes mechanism (a kink) at a critical saturation.

TRETJA-GO asks which measurements best decide whether the local-equilibrium model is adequate for the mixing
zone, and compares the goal-oriented choice with a parameter-oriented one.

**Chemistry.** The PHREEQC speciation (phreeqc.dat database, 15 °C) is tabulated once as Ω(f, ΔCa): the calcite
saturation ratio for seawater fraction f after ΔCa of calcite has dissolved. The two end members are:
- fresh groundwater at log pCO₂ = −2.0;
- intruded seawater at log pCO₂ = −2.5.

Both are at calcite equilibrium. The mixtures reach Ω = 0.58 at 25% seawater, and up to 0.13 mmol/L of calcite
can dissolve.

**Transport.** Transverse mixing between parallel fresh and saline flows, marched along the flow:
- velocity 0.2 m/day;
- transverse dispersivity 0.05 m;
- length 1 km;
- implicit diffusion with operator-split, capped kinetic dissolution.

**Rate law.** r = κ g(Ω), with reaction order n₁ near equilibrium and n₂ far from it. The law switches from one
order to the other at Ω_c. The local-equilibrium limit and a linear law (n = 1) are also computed.

**Prior.** A uniform grid of 1950 parameter sets:

| Parameter | Range |
|---|---|
| log₁₀ κ | −6 to −2 mmol/L/day |
| n₁ | 0.5 to 2 |
| n₂ | 2 to 5 |
| Ω_c | 0.6 to 0.9 |

**Goal.** G, the calcite dissolved in the first kilometre per metre of coast per year. The decision is whether the
local-equilibrium model is adequate, taken as G ≥ 0.8 G_LEA.

**Designs.**

| Code | Data |
|---|---|
| LF | 8 lab rates far from equilibrium (Ω = 0.05–0.40) |
| LN | 8 lab rates near equilibrium (Ω = 0.60–0.95) |
| LS | 8 lab rates spread over 0.05–0.97 |
| F | Ca excess at 5 depths of one multilevel well at 500 m |
| F+LF, F+LN, F+LS | the field well combined with each lab design |

Lab rates carry a ±20% error and an unknown laboratory prefactor, so they constrain only the shape of the rate law.
The field Ca excess carries an error of 0.02 mmol/L; 0.01 and 0.05 mmol/L are also tested.

| File | What it does |
|---|---|
| `tretja.py` | PHREEQC table (needs `pip install phreeqpython`), the mixing-zone model, the rate laws. |
| `tretja_exp.py` | Grid runs, structural comparisons and the preposterior design analysis. Writes `tretja_results.json` and `tretja_grid.npz`. Takes about 5 minutes. |
| `tretja_figs.py` | Draws `figT1_kinetics.png` and `figT2_design.png`. |
| `tretja_table.npz` | The cached PHREEQC table; it is rebuilt in a few seconds if deleted. |

```
pip install phreeqpython
python3 tretja_exp.py
python3 tretja_figs.py
```

## Main results

**Local equilibrium overestimates dissolution.** Over the prior:
- the median overestimate is a factor of 1.6;
- one case in ten is overestimated by more than 29 times, and the largest overestimate is 264 times;
- 43% of the prior is kinetically limited (G < 0.5 G_LEA).

**A linear rate law with the same prefactor errs by a factor of about 2.6 either way.** Between the 10th and 90th
percentiles it gives 0.38 to 1.84 times the true dissolution.

**κ dominates.** κ explains 78% of the variance of log G; n₁, Ω_c and n₂ explain 6.5%, 3.5% and 0.8%.

**The parameter criterion picks lab programmes; the goal picks the field well.** Correct decisions on the
equilibrium question, at a field error of 0.02 mmol/L:

| Design | Correct decisions | Posterior SD of log₁₀ G | Information about the rate law |
|---|---|---|---|
| no data | 59.2% | 0.60 | 0 |
| lab far | 59.2% | 0.60 | 0.92 nats |
| lab near | 61.0% | 0.54 | 3.10 nats |
| lab spread | 61.6% | 0.54 | 4.17 nats |
| field well | 95.1% | 0.19 | 1.22 nats |
| well + lab far | 95.2% | 0.19 | 2.13 nats |
| well + lab near | 95.9% | 0.17 | 4.23 nats |
| well + lab spread | 96.0% | 0.17 | 5.29 nats |

- **Lab data alone barely beat no data.** The best lab programme carries 3.4 times more parameter information
  than the well, yet it decides the field question correctly only 61.6% of the time, against 95.1% for the well.
- **Far-from-equilibrium rates, the usual lab practice, add nothing, even to the field well.** Near-equilibrium
  rates add a little.
- **Field precision matters.** With a field error of 0.01 or 0.05 mmol/L, the well alone decides correctly 97.0% or
  87.7% of the time.
- **Reading the well with a linear rate law costs accuracy.** The decisions fall to 93.8%, and the mean absolute
  error in log₁₀ G is 0.15, about a factor of 1.4.

The report is
`docs/literature/Literature_review_Nonequilibrium_Nonlinear_Hydrogeochemistry_Oxford_Caltech_Princeton_2020-2026.docx`
(section 8).
