# Synthesis of reviews 42 and 43: chloride sufficiency, the time-scale atlas and the system figure

Code for the synthesis article *The trace and the rhythm: an augmented transient system of variable-density flow and
multi-species transport for coastal aquifers, and what chemistry and time-dependent data can identify*, which collects
the innovations of literature reviews 42 (GJURMA-GO, `../gjurma_go`) and 43 (RITMI-GO, `../ritmi_go`) and adds one new
result.

## The new result: chloride sufficiency and the price of the cut (`synth_cut.py`)

Linearised at the prior-mean truth of RITMI-GO, with the history (34 data) and five years of status-quo monitoring
(monthly Cl and half-yearly ions at wells 503, 341, 340; 360 data): 190 chloride data and 204 data of the other ions.
The twelve standardised parameters are split into transport and memory (`s_v, alpha_L, f_0, a_1, b_1, a_2, b_2`) and
exchange and reaction (`E, K_K, K_Ca, K_Mg, k_sr`). For the three 2045 goals the script compares the joint fit, chloride
data only, ion data only and the linear-Gaussian cut (transport and memory from chloride alone, exchange and reaction
from all data given them), and computes the shift of each goal when the ion data carry a systematic error.

| Result | Value |
|---|---|
| Rank of the chloride Jacobian on the 7 transport and memory parameters | 7 (the chloride goal is fully seen by chloride) |
| Posterior sd of Cl at 5 km in 2045, joint / cut | 1.09 / 1.25 mg/L (+15%) |
| Na at 3 km, joint / cut | 3.23 / 4.28 mg/L (+32%) |
| Shift of the Cl goal for a one-sd bias of all Na data, joint / cut | 0.59 / 0 mg/L |
| Worst-case shift of the Cl goal, ion errors with RMS of one sd, joint / cut | 7.4 (6.8 posterior sd) / 0 mg/L |

## Figures (`synth_figs.py`)

- `figA1_system.png`: the augmented transient system drawn on a schematic Fushë-Kuqe cross-section, with equation
  numbers of the article.
- `figA2_atlas.png`: the time-scale atlas (what the system remembers, what forces it, what the data resolve, what the
  goals need) on one axis of period.
- `figA3_cut.png`: price and protection of the cut, and coverage in the nonlinear twin of GJURMA-GO.

## Running

`./run_all.sh` (a few seconds; needs `../ritmi_go` and `../gjurma_go/gjurma_summary.json`).
