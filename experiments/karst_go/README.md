# KARST-GO: what changes in the model when the aquifer is karstic

One diagram (A3 landscape) that shows how a coastal karst aquifer is modelled and what changes with respect to a porous
aquifer. Word version: `docs/research_notes/Karst_Aquifer_What_Changes_In_The_Model.docx`, six A4 landscape pages in
large type: the section, the section enlarged in two halves, the innovation written out with its equations, and the
eight panels four to a page. Every equation of the innovation and the panels is editable Word math (OMML).

**The section.** A coastal karst massif: sea with a submarine spring, a coastal spring (brackish) and an overflow spring,
seawater entering the conduits at a deep inlet, the seawater wedge in the matrix, dolines and vadose shafts, a polje whose
stream sinks into a ponor, a cave, the epikarst, the water table, a trunk conduit with a deep branch, conduits not yet
mapped, a tracer test from the ponor to the coastal spring and the impervious base. An inset shows the spring record
(fast discharge peak from the conduits, slow tail from the matrix, EC dropping when new water arrives); a legend gives
the line and area styles. Eight numbered badges point to eight panels.

**The eight panels** (each with the porous counterpart, the karst equations and what changes in the model):
1. Flow in the conduits: Hagen–Poiseuille (laminar), Darcy–Weisbach with Colebrook (turbulent).
2. Two media that exchange: matrix and conduit heads with exchange α_ex (h_m − h_c).
3. Recharge through the epikarst: an epikarst store split into concentrated (β) and diffuse (1 − β) recharge.
4. Springs are the outlets: Q_s = C_s (h_c − z_s)_+ and the multi-exponential (Maillet) recession.
5. Seawater in the conduits: Q_sea = C_i (h_f^sea(z_i) − h_c(z_i))_+ with h_f^sea(z) = η + δ(η − z); spring salinity by
   mixing; a fresh spring is a censored observation.
6. Fast and slow transport: the mobile–immobile model.
7. The network is an unknown: N = (V, E, {D_e, ε_e}) conditioned on tracer tests, spring discharge and EC.
8. Floods, a regime of their own: the conduit capacity Q_max and overflow springs and estavelles above it.

**Innovation (KARST-GO).** The conduit network itself is assimilated: stochastic networks generated from geology,
fractures and base level are weighted by tracer tests, the spring hydrograph and its EC. Every pipe law, exchange and
switching outlet is monotone in the head, so the update stays stable; the EC of a coastal spring observes the conduit
head at the sea inlet.

**Check of the stability claim** (`check_monotone_karst.py`, log in `check_monotone_log.txt`). Dual continuum on 30
random conduit graphs (25 conduit nodes, 25 matrix cells, a chain plus 10 random links), laminar–turbulent pipe law
f(d) = C d / √(|d| + ε), linear exchange, a switching spring and a sinking stream; two runs with different initial heads
and forcings, implicit Euler with Newton. Monotone laws give ‖Δh_n‖ ≤ ‖Δh_0‖ + Σ dt ‖S⁻¹Δb_k‖ in the storage norm. The
largest ratio of the head difference to this bound over the 30 networks is 0.3273 (it must stay at or below 1).

## Build
```
npm install                 # once: KaTeX 0.16.11 for the equations
python3 karst_diagram.py    # -> karst_diagram.html (section in SVG, panels in HTML, equations typeset by KaTeX)
node render.js 1.5          # -> karst_diagram.png (3600 x 2546) and karst_diagram.pdf (vector, one A3 landscape page)
./build_word.sh            # -> word_karst/Karst_Aquifer_What_Changes_In_The_Model.docx (OMML, large type)
python3 check_monotone_karst.py
```
`build_word.sh` runs `word_content.py` (the text, equations and crops of the diagram) and the Word builder of
`../ml_paradigms/word` (`paradigms_word.js`, docx from npm; `omml.py`, pandoc 3 and lxml).
`make_docx.py karst_diagram.png <out>.docx` still makes a one-page picture copy.
`render.js` needs Playwright with Chromium; it shrinks an equation that is wider than its panel and exits with an error if
an equation falls below 19 px, a panel or the innovation band overflows, the title meets the header tags, or a label
overlaps another label, a badge, the inset or the legend, or leaves the section. `make_docx.py` needs python-docx.

## Files
- `karst_diagram.py`: geometry, labels, inset, legend, the eight panels and the page layout.
- `katex_render.js`: typesets the equations (LaTeX → KaTeX HTML).
- `render.js`: PNG, vector PDF and the layout checks.
- `word_content.py`, `build_word.sh`: the Word version with OMML equations.
- `make_docx.py`: a one-page picture copy in Word.
- `check_monotone_karst.py`, `check_monotone_log.txt`: the stability check.
