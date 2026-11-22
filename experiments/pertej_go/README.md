# PËRTEJ-GO: the boundary condition the flow equation is missing

Code and results of the theory note (November 2026, English):
`docs/research_notes/PERTEJ-GO_Transparent_Learnable_Boundary_Flow_Equation.docx`.
*Përtej* is Albanian for "beyond": the note is about the aquifer beyond the cut of a model.

**The question.** The assembly note (MONTIMI-GO, `docs/research_notes/Assembled_System_Equations_Placing_Recharge_and_Pumping_Wells.docx`)
writes the flow equation with two added terms: the lens memory and the learned closure Ψ. Its inland boundary is a
prescribed inflow or a closed margin. Which term should be added where the model is cut, so that the boundary is the
true one? Can a neural network (a "neural regularizer") learn it?

**The answer, in four propositions** (`text_pertej.py`, with proofs):
1. *Structure.* For any linear exterior, the exact boundary is a conductance plus positive first-order compartments:
   `q·n = C u + Σ w_m (u − y_m)`, with `y_m' = μ_m (u − y_m)` and `C, w_m ≥ 0`. This is the lens memory of the
   assembly note moved onto the boundary. Conversely, every such network is a physical exterior.
2. *Passivity.* With `C, w_m ≥ 0` the model loses energy, whatever the rest of it is. A neural network may supply the
   forcing (the inflow from rain) and monotone conductances, but not the storages. A negative conductance can be
   stable in one model and unstable in a longer one.
3. *Approximation.* About 3–4 compartments per decade of period are enough. The half-order boundary of a
   semi-infinite strip needs `M ≈ 1 + ln(1/ε)/π² [ln(ω_max/ω_min) + 4 ln(2/(πε))]` compartments.
4. *Identifiability.* Two piezometers between the closure and the cut learn the boundary apart from everything else,
   on the band of periods the pumping excites. A source inside the band confounds it. Design rule: vary the pumping.

**Test bed.** A 1-D coastal aquifer:
- 10 km long, T = 500 m²/d, S = 0.05;
- 100 m cells, daily implicit Euler, 20 years;
- the model sees the first 2 km; the 8 km beyond are closed and are what the boundary must replace.

The parameters are illustrative.

**Results** (`res/pertej.json`, all from `pertej_exp.py`, about 2 minutes):

| Check | What | Result |
|---|---|---|
| N1 | exact network (80 compartments), positive reductions, classical boundaries | exact to 1.3×10⁻¹³ m. Boundary-cell rms over 20 years: 6 compartments 7.8 mm, 12 compartments 0.44 mm. Calibrated GHB 147.9 mm, no flow 242.0 mm, fixed head 305.8 mm |
| N2 | count of compartments for the half-order boundary | the formula's count reaches 1.8–2.4 ε; reaching ε itself takes 19–21% more |
| N3 | passivity | passive energy is monotone. C = −0.2c grows ×3.4×10⁵² in 5 years, at exactly the predicted discrete rate. C = −0.02c is stable at 2 and 4 km and unstable at 6 and 8 km |
| N4 | learning from two piezometers (output error) | varied pumping, 2 mm noise: 1.3% impedance error in the band and 6.1 mm on a new drought-and-pumping regime (calibrated GHB: 372 mm). Steady pumping: 5.1%, 35 mm. A closure in the band: 47% error |
| N5 | learned prior from 400 simulated exteriors (right and wrong geology) | error at unexcited periods falls 3.9–4.4 times; every prediction improves, also with the wrong prior. A prior does not replace varied pumping |
| N6 | sea rise of 0.5 m in 20 years: fresh water that does not reach the sea | truth 154 m³/m. Prescribed inflow (the assembly note's boundary) 49, fixed head 462, calibrated GHB 237, PËRTEJ-GO with 6 compartments 160 |

**Files**
- `pertej_exp.py`: the six checks N1–N6, written to `res/pertej.json`, `res/pertej_series.npz` and `res/pertej_stdout.txt`.
- `pertej_figs.py`: the five figures, rendered into a temporary folder when the note is built.
- `text_pertej.py`: the text, as a list of blocks. Every number is filled in from `res/pertej.json`.
- `build_pertej_doc.py`: builds the Word file, with equations as native Word math (OMML, through pandoc).
- `run_all.sh`: runs everything.

The references [1–21] were checked in Crossref (DOI, authors, title, venue), November 2026. The note was drafted with
the help of an AI assistant.

**Limits.**
- The exterior is linear and fresh, and the checks are one-dimensional. In 2-D and 3-D the exact boundary is nonlocal
  along the cut.
- The neural density for the prior is proposed but not tested; a Gaussian on 48 impedance features stands in for it.
- The inflow from rain was zero in the test bed.
- Gradients come from finite differences, not an adjoint.
