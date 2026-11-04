# MATJA-GO: the guaranteed value of a measurement

Code and results of the second state-of-the-art review, *State of the art II: inputs, dispersion and boundary
conditions from rain*. It covers twenty more papers from Oxford, Caltech, Berkeley and MIT (2020–2026), chosen for
direct use, and gives a "state of the art and beyond" table for a NATO proposal. It also presents the MATJA-GO
innovation (November 2026, English). It is the companion of review I (`../garancia_go`, GARANCIA-GO). It is built to
`docs/literature/Literature_review_State_of_the_Art_II_Inputs_Dispersion_Boundary_Conditions_from_Rain_MATJA-GO_Oxford_Caltech_Berkeley_MIT_2020-2026.docx`.

**The question.** Only the rain is known. Which instrument should come first: an automatic head logger at one of eight
sites, or a tide gauge? And what is it guaranteed to buy?

**The idea.**
- The value of an instrument is the guaranteed band width it removes, `W(D) = λ̂_D · s̄_D`.
- `λ̂_D` is the conformal-risk-control multiplier, calibrated on simulated aquifers that carry the data of design `D`.
- Designs are chosen on pool A (150 aquifers). Each chosen design is recalibrated on a fresh pool B (300 aquifers), so
  the guarantee holds for the design that was chosen (Proposition M1).
- Two other criteria are compared: the raw ensemble (`1.645 s̄_D`) and the exact posterior (an oracle, available only
  because the test bed is linear).

**Proposition M3.**
- Setting: an instrument whose data are independent of the goal, added with no other data.
- An N-member stochastic ensemble smoother shrinks the expected spread variance by `1 − δ_N`.
- It grows the expected error variance by `1 + ε_N`.
- These are exact identities, with `δ_N = E tr[Ĉ(Ĉ+R)⁻¹]/(N−1)` and `ε_N = E tr[Ĉ(Ĉ+R)⁻¹(C+R)(Ĉ+R)⁻¹]/(N−1)`.
- For large N both are about `d_s/(N−1)`.

**Remark M3, a first-order price rule.** An informative instrument still has a negative guaranteed value when its
exact variance reduction `ρ_c < ε_N/(1+ε_N)`.

## Results

| Test | What it shows |
|---|---|
| T6, single instruments, fresh pool (`res/matja_single.json`) | **Tide gauge, rain only:** the exact value for recharge, inflow and κ is zero. The raw ensemble promises −15%, while the guaranteed band widens by 16–21%. For the sea level it is worth a factor 14. **Logger at 0.25 km for the inflow:** exact −7%, ensemble −17%, guaranteed +9%. **Overall:** 10 of 36 instrument–goal pairs have a negative guaranteed value. |
| Remark M3 (`res/matja_price.json`) | The sign is predicted for 36/36 pairs. The median error of the half-width factor is 2.4% (largest 8.2%). |
| T7, greedy choice of three instruments (`res/matja.json`) | **Recharge and inflow:** the criteria agree within 9%; for the recharge, MATJA-GO took a tie at step 2. **κ:** the raw ensemble claims 0.002 for its design, against 0.018 exact and 0.026 guaranteed. After two loggers the guaranteed κ width stays at 0.023–0.026, so the reconstructor is the limit. **Fresh pool:** every guarantee held (share of weeks outside 0.092–0.101, whole-function coverage 0.90). |
| T8, ensemble size 32–512 (`res/matja_spur.json`) | **Spread factors:** match `1−δ_N` within 0.003. **Error factors:** match `1+ε_N` within 18%. **With 512 members:** the worthless tide gauge still widens the guaranteed band by 6–9%. |

## Files

- `matja_exp.py`: test bed wrapper, the three criteria, greedy paths and fresh-pool scores.
- `matja_single.py`: T6 and signal degrees of freedom.
- `matja_spur.py`: T8, with Monte Carlo `δ_N` and `ε_N`.
- `matja_price.py`: the Remark M3 check.
- `matja_figs.py`: figures (scheme, single, paths, spur); the map figure comes from `../garancia_go/gar_figs.py`.
- `cards_matja.py`: the twenty cards. Each has links, evidence, the state of the art it sets, what it cannot yet do, three lessons and an innovation step.
- `text_matja.py`: the text of the review.
- `build_matja_doc.py`: the Word builder, using helpers from `../garancia_go/build_gar_doc.py`.
- `run_all.sh`: runs everything, about 20 minutes on 4 cores.

Dependencies: `../rindertimi_go/rgo_model.py` (test bed), `../garancia_go` (CRC helpers, style, results of review I) and
pandoc (OMML equations, through `../ml_paradigms/word/omml.py`).

Every card is partly verified. Landing pages were reached through search results only, because doi.org, arxiv.org
and most publisher hosts were blocked in this environment.
