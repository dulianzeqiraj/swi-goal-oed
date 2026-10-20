# NGARKESA-GO: what to measure in a coastal aquitard, with electroneutral ion transport

*Ngarkesa* means "the charge". The base article (Van-Brunt, Farrell & Monroe, *Structural electroneutrality in
Onsager–Stefan–Maxwell transport with charged species*, arXiv:2211.13505) builds electroneutrality into the
structure of electrolyte transport. In groundwater the same structure appears in its dilute limit:
zero-current Nernst–Planck transport.

NGARKESA-GO uses that model as the forward model of a goal-oriented design. The question is which porewater or
geophysical measurements best predict when a freshened coastal aquifer recovers from the salt stored in its
clay aquitard.

**Setting.** A clay aquitard, 3 m thick, under the aquifer of a coastal well field:
- **Salinization phase (40 years):** the aquifer carries 25% seawater, and salt diffuses into the clay.
- **Freshening phase (60 years):** the aquifer is fresh, and the clay returns the salt by back-diffusion.

**Goals.** The recovery times after which the flux from the clay keeps the aquifer below the drinking-water
values for chloride (250 mg/L) and sodium (200 mg/L). The throughflow is 0.07 m/yr per m² of aquitard. The
decision is whether recovery happens within 20 years.

**Model.**
- **Ions:** Na⁺, K⁺, Ca²⁺, Mg²⁺, Cl⁻, SO₄²⁻ and HCO₃⁻, with free-water tracer coefficients scaled to 16 °C.
- **Transport:** zero-current Nernst–Planck fluxes divided by the formation factor F. Electroneutrality holds by
  construction: the largest charge error is about 3e-11 mmol/L.
- **Exchange:** Gaines–Thomas, with PHREEQC constants and Davies activity coefficients.
- **Numerics:** finite volumes, 60 cells.

**Compared with two common simplifications:**
- one diffusion coefficient for all ions (electroneutral, but salt moves at the chloride rate);
- each ion with its own coefficient and no electrical coupling (charge is not conserved).

**Uncertain parameters.** F, log-uniform on 3.5–12, and the cation-exchange capacity, uniform on 5–30 meq/100 g.
Both lie on a 25 × 21 grid.

**Designs.**

| Code | Design | Error |
|---|---|---|
| R | resistivity log (formation factor) | 20% |
| L | lab CEC | 15% |
| C | porewater chloride at 4 depths | 5% |
| I | porewater Cl, Na, Ca and Mg at 4 depths | 5% |

Pairs of these are also tested. For each design the preposterior analysis draws 40 noisy data sets for every
grid point and computes the exact posterior. Each design is scored two ways:
- **goal-oriented:** the probability of a correct deadline decision, for chloride and for sodium;
- **parameter-oriented:** the expected information gained about F and CEC.

| File | What it does |
|---|---|
| `ngarkesa.py` | Electroneutral multicomponent transport with exchange (batched over parameter sets) and the two simplified models. |
| `ngarkesa_exp.py` | Grid runs of the three models, recovery times and preposterior design analysis. Writes `ngarkesa_results.json` and `ngarkesa_grid.npz`. Takes about 6 minutes on 4 cores. |
| `ngarkesa_figs.py` | Draws `figN1_transport.png` and `figN2_design.png`. |

```
python3 ngarkesa_exp.py
python3 ngarkesa_figs.py
```

## Main results

**The simplifications are biased** (mean error over the prior, range in brackets):

| Model | Chloride recovery time | Sodium recovery time | Charge error |
|---|---|---|---|
| One coefficient for all ions | +9.5% (+7.1 to +17.2%) | +18.6% (+3.9 to +26.1%) | none |
| Own coefficients, no coupling | +9.5% (+7.1 to +17.2%) | −6.6% (−8.6 to −4.5%) | up to 27.9 mmol/L |

**What to measure depends on the goal.** Correct deadline decisions, electroneutral model:

| Design | Chloride | Sodium | Information about F and CEC |
|---|---|---|---|
| no data | 63.6% | 64.6% | 0 |
| lab CEC | 63.6% | 67.4% | 1.16 nats |
| resistivity log | 87.4% | 79.8% | 0.72 nats |
| resistivity + CEC | 87.8% | 88.1% | 1.88 nats |
| chloride profile | 97.4% | 85.8% | 2.26 nats |
| major-ion profile | 98.8% | 98.1% | 5.19 nats |

- **Parameter information picks the wrong cheap measurement.** It ranks the lab CEC above the resistivity
  log. Yet the CEC adds nothing to the chloride decision, and it is also worse than the log for sodium.
- **A second reversal.** The chloride profile carries more parameter information than resistivity + CEC. Yet
  for sodium, resistivity + CEC gives more correct decisions.

**The model used to read the data matters.**
- **Calibration hides the error only for the calibrated ion.** When the one-coefficient model is fitted to
  the chloride profile, its chloride forecast is almost unbiased. Its sodium forecast is late by 1.6 years.
- **More data can make the wrong model worse.** Fitted to the full major-ion profile, the one-coefficient
  model gets chloride decisions right 94.0% of the time, against 97.1% with chloride alone. The electroneutral
  model goes the other way, rising from 97.4% to 98.8%.

The report is `docs/literature/Literature_review_Charged_Species_Transport_Hydrogeochemistry_2020-2026.docx`
(section 10).
