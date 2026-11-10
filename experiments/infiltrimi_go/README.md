# INFILTRIMI-GO: rain, infiltration and soil moisture from groundwater levels

Synthetic checks for the working document *Rain, infiltration and soil moisture from groundwater levels*
(`docs/research_notes/Zeqiraj_Rain_Infiltration_Soil_Moisture_from_Groundwater_Levels.docx`).

The chain, on a daily step for one well:
gauge rain × m → infiltration min(P, Ic) → root-zone store (field capacity θfc, evapotranspiration
k_et·PET·min(1, θ/θfc)) → drainage (θ − θfc)⁺/τs = recharge → head (specific yield Sy, drainage time τa).

| Check | What it tests |
|---|---|
| Water-table fluctuation (Proposition 1) | daily and monthly recharge from 1 cm heads when Sy is known; errors telescope |
| Jacobian (Proposition 2) | exact scale symmetry of (m, k_et, Ic, θfc, Sy); one zero singular value; any anchor lifts it |
| Bayesian inversion | five data sets: heads and gauge (S0); + pumping test (S1); + soil probe (S2); + chloride balance (S3); all (S4) |
| No storms above Ic (Proposition 4) | infiltration capacity reduced to a lower bound |

Method: bounded least squares from eight starts for the most probable parameters, then differential-evolution
MCMC (ter Braak, 2006) with 64 chains in two halves and a symmetric move along the scale direction.

Run:

    python infiltrimi_exp.py infiltrimi_results.json      # numpy, scipy; about 8 minutes
    python infiltrimi_figs.py infiltrimi_results.json figs
    python build_infiltrimi_doc.py infiltrimi_results.json figs ../../docs/research_notes/Zeqiraj_Rain_Infiltration_Soil_Moisture_from_Groundwater_Levels.docx
