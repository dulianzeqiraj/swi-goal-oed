# TRONDITJA-GO: the earthquake, the aquifer and liquefaction, implemented

*Tronditja*: the jolt. Steps 1–3 of the working note on the earthquake, the aquifer and floods (TERMETET, 31 October
2026) as tested code, with the innovation of the series.

| File | What it does |
|---|---|
| `liq.py` | Boulanger–Idriss (2014) CPT triggering and LPI with the pore pressure of the day, `u = γw (z − zw)+ + f Δp0`; the closed form `∂ln FS/∂zw = (γw/σ′v)(1 − Cσ/Kσ)`; the step coefficient `κ = (2GB/3)(1+νu)/(1−νu)` of a layer under the free surface; the drainage share `f` |
| `okada85.py` | Okada (1985) surface displacement and strain of a rectangular fault (numpy) |
| `okada_checks.py` | five independent checks of `okada85.py` → `res/okada_checks.json` |
| `tronditja_exp.py` | E1 liquefaction module, E2 coseismic step from four published source models, E3 hindcast design, E4 joint safe window and daily bulletin → `res/tronditja.json`, `res/tronditja_series.npz` |
| `tronditja_figs.py` | the six figures |
| `text_tronditja.py`, `build_tronditja_doc.py` | the English report with OMML equations |
| `fix_termetet.py` | the revision of the author's Albanian note (text, OMML equations, a table row, references) |

Run everything: `./run_all.sh` (Python 3 with numpy, scipy, matplotlib, python-docx; pandoc for the equations).

## Main results (synthetic plain, soils and port; local coordinates)

- **Correction of magnitude.** A soft layer under the free surface takes the horizontal strain of the crust and
  deforms at almost constant volume, so its static step is `Δp0 = −κ Δεa` with `κ ≈ 2GB`. Over the four source models
  the head falls 7–12 cm in soft surface sand (G = 50 MPa) and 0.6–1.0 m in a stiffer confined aquifer (G = 0.5 GPa);
  equation (2.2) as written gives 35 times the soft-sand value. For liquefaction of the surface sands the static step
  is negligible; for the confined aquifer and its wells it is not.
- The LPI of the example profile falls about 6 per metre of deeper water table; re-normalising the CPT resistance with
  the stress of the day understates that slope by 33%.
- The earthquake is a free pumping test: a 0.3 m step in the confined aquifer pins the leakage time 5.8 times more
  sharply than a year of seasonal heads.
- The 2019 liquefaction map cannot test the step (power below 50% with 480 CPT sites even for the upper bound).
- **Innovation:** which aquifer feels the earthquake (the step coefficient of a layer under the free surface), the
  earthquake as a free pumping test, and the design result for the 2019 hindcast. The certified safe window and the
  daily state "if the design earthquake struck now" are concepts of the CERTAIN-COAST proposal; computed here, the
  window between liquefaction and intrusion closes at 0.29 m of sea-level rise for 0.20 g at the synthetic port and is
  already closed at 0.22 g, and P(LPI > 5 | earthquake today) moves between 0.16 and 0.26 over the year.

Report: `docs/research_notes/TRONDITJA-GO_Earthquake_Aquifer_Liquefaction_Implementation.docx`.
Revised note: `docs/research_notes/TERMETET_CERTAIN-COAST_Termeti_Akuiferi_Permbytjet_Sistemi_i_Ekuacioneve_rishikuar.docx`.
