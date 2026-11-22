# HIPOTEZA-GO: hypotheses as terms of the differential equations

Where does the chloride of a coastal aquifer come from? With tracers alone the question is often left open
(`../zanafilla_go`). Here the equations of variable-density flow and transport supply the missing information:
every hypothesis about the origin is a term of the transport equation (the sea is a boundary condition, the lagoon
a leakage through the top, the anthropogenic and the legacy chloride source terms, the deep saline water a flux
through the base), and the physics links the wells.

For given hydraulic parameters the tracers of all samples are linear in a short vector of source strengths and
signatures shared by the samples. The set of strengths and signatures that reproduce the data is then an exact
polytope, and the share of each source at each well has sharp bounds by linear programming (Charnes-Cooper). The
hydraulic parameters are covered by an ensemble of simulations; the answer is the union over the members that the
data do not rule out. A hypothesis is tested by dropping its term: if no simulation reproduces the data with the
reduced library, the reduced library is falsified.

Everything here is synthetic. No field data are used or stored.

## Files

| File | Content |
|---|---|
| `hip_core.py` | Variable-density section (finite volumes, 120 x 20), steady state by Anderson-accelerated Picard iteration, tagged sources and waters, tritium with decay, transient march under a pumping history |
| `hip_ensemble.py` | Ensemble of simulations over the hydraulic parameters (`res/ensemble.npz`) |
| `hip_infer.py` | Polytope per member, tolerance factor kappa, sharp share bounds, union with the minimum-population rule, sub-library tests |
| `hip_exp.py` | The numerical test: calibration by leaving members out, attribution with and without the physics, tests of terms, a missing source, model error (`res/hipoteza.json`) |
| `hip_dyn.py` | Pumping histories against the steady states of the extreme rates (`res/dyn.json`) |
| `hip_figs.py` | Figures |
| `text_hip.py`, `build_hip_doc.py` | The note (Word, equations in OMML) |

## Run

```
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python hip_ensemble.py 4000 4 2026 ensemble.npz   # about 13 minutes on four cores
python hip_exp.py 24 4                             # about 15 minutes
python hip_dyn.py                                  # about 2 minutes
python hip_figs.py res/figs
python build_hip_doc.py HIPOTEZA-GO.docx     # needs pandoc
```

Needs numpy, scipy (HiGHS through `linprog`), matplotlib, python-docx. The comparison without physics imports
`../zanafilla_go/wrr/field_model.py`.

## Checks

- Without pumping and without the extra sources the solver agrees with `chloride_fk/python/fkcl_vd.py` to 2e-7 in
  the salinity.
- The tagged water fractions sum to one to 1e-10.
- A linear programme that the solver does not finish is replaced by an outer bound computed from the intervals of
  the strengths, never by a guess; a pair of sample and source for which no member gives a bound carries no
  statement.

## Limits

Two-dimensional section; steady state for the attribution; truths and ensemble share one solver (one test of a
departure, a layered conductivity, is included); the places of the sources and the pumping are taken as known; the
certified bound over all pumping histories (sum-of-squares, Fantuzzi and Goluskin 2020) is stated in the note but
not computed here.

## Fushë-Kuqe: HIPOTEZA-GO on today's data

The same method on the section A-A' of the chloride manuscript (`../../chloride_fk`), with the pumping of the
Gorre-Fushë-Kuqe well field, calibrated with the three documented heads and tested against the four analyses of
Cenameri & Beqiraj (2016).

| File | Content |
|---|---|
| `fk_core.py` | The Fushë-Kuqe section: geometry and conductivity from a calibrated member of the areal model, inert cover and base, pumping, the library with physics gates (lagoon leakage only below the lagoon level, anthropogenic input only where the aquifer is not artesian) |
| `fk_ensemble.py` | Ensemble of the class (`res_fk/ensemble_fk.npz`) |
| `fk_infer.py` | Unknown well positions as discrete unknowns: tolerance factor and sharp share bounds by mixed-integer linear programming (HiGHS through `scipy.optimize.milp`) |
| `fk_run.py` | Calibration with the heads, threshold by leaving members out, all 16 sub-libraries, union of the share bounds |
| `fk_diag.py` | Why "sea and fresh recharge only" fails: what the sea brings to well 340 against what it leaves at wells 503 and 341 |
| `fk_sparse.py` | Completes the share bounds and adds those of the sparsest accepted libraries |
| `fk_figs.py`, `fk_text.py`, `build_fk_doc.py` | Figures and the internal note |

```
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python fk_ensemble.py 2400 4 2027                 # about 15 minutes on four cores
python fk_run.py 4                                # about 6 minutes
FK_VARIANT=shallow FK_SHARES=0 python fk_run.py 4 # wells 341 and 503 in the first aquifer
python fk_diag.py; FK_VARIANT=shallow python fk_diag.py
python fk_sparse.py 4
python build_fk_doc.py FK_HIPOTEZA-GO.docx
```

The results (`res_fk/`) and the note are not in the repository: they are derived from the workbook
`data/Fushe_Kuqe_All_Data.xlsx`, whose owners (the Albanian Geological Survey and A. Beqiraj) gave permission for
the chloride manuscript only.
