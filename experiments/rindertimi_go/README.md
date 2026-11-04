# RINDËRTIMI-GO: all boundary conditions of a coastal aquifer from rain and the Fushë-Kuqe data

Numerical checks of the note *Reconstructing all boundary conditions of a coastal aquifer from rain and the Fushë-Kuqe
data* (November 2026, English, `docs/research_notes/RINDERTIMI-GO_Boundary_Conditions_FunDPS.docx`).

The note builds the boundary and initial conditions of the coastal-aquifer simulation as an inverse problem, after
FunDPS (Yao et al., NeurIPS 2025, arXiv:2505.17004v3):

- **Joint function.** Head h(x, t), sea level η(t), inland inflow q_L(t), recharge r(t) and the rain filtered by the
  unsaturated zone f(t) on one (x, t) grid. The four boundary channels are functions of time, stored as copies along x.
- **Physical prior.** The simulator draws the training set: the SHIU-GO rain law, an Erlang-2 vadose filter,
  r = κ f + e, Gaussian random fields for η, q_L and e, and the initial head from the steady state plus a random field.
- **Denoising neural operator.** An FNO with noise-level conditioning, trained with the EDM loss under GRF noise.
  The projection Π takes the x-mean of the boundary channels; Proposition 1 shows it never increases the denoiser
  error.
- **Sampling.**
  - FunDPS guidance on the filtered rain gives the ensemble of scenario A.
  - Heads (scenario B) and a tide gauge (scenario C) enter through an ensemble smoother with the exact linear solver.
    Every member is then re-simulated.
  - Plain FunDPS guidance with every observation is run as the reference.
- **Exact benchmark.** Given the rain and κ, the problem is linear-Gaussian, so the posterior is a one-dimensional
  mixture over κ (Proposition 3). Every method is scored against it.

## Results (`rgo_fundps.py` → `res/rgo_eval.json`; medians over 12 test cases, paired across scenarios)
The scores are against the exact posterior of each scenario:
- the error ratio is the RMSE of the posterior mean divided by that of the exact posterior mean;
- the spread ratio is the posterior sd divided by the exact sd.

| Scenario and method | Error ratio | Spread ratio | Other |
|---|---|---|---|
| A, rain only: FunDPS, 128 members | 0.97–1.11 | 0.98–1.02 | κ error 0.081 (exact 0.073) |
| B, rain + 4 loggers: FunDPS + ensemble update with the exact solver | 1.26–2.77 | 0.83–2.67 | heads fit 2.1 cm (noise 2 cm); κ error 0.009 (exact 0.005) |
| B: plain FunDPS, every observation in the guidance | 1.92–6.91 | 2.02–6.93 | heads miss 24.5 cm; diverged in 2 of 12 |
| C, B + tide gauge: FunDPS + ensemble update | 1.78–3.88 | 0.87–2.47 | sea-level coverage 57% |
| C: plain FunDPS | 1.63–9.25 | 2.09–8.39 | diverged in 1 of 12 |

- **Rain only.** FunDPS reproduces the exact posterior.
  - The sea level and inflow keep their prior spread.
  - Recharge follows the timing of the rain; its size stays as uncertain as κ.
- **Heads.** Plain guidance does not take them in: its pull ignores the noise level (Remark 1). The ensemble update
  with the exact solver does.
  - With 128 members the update is too narrow in κ (spread 0.0028 against
    0.0112 exact).
  - It is too wide in recharge and the initial head.
- **First training** (weekly rain of the window as the fifth channel; `res/run1_rain_channel/`).
  - On the two validation cases the recharge error with rain alone was 1.68 times the exact error, and 0.78 with the
    filtered rain.
  - Guidance on the head channel fitted the piezometers to 0.3 cm, while the heads re-simulated from the sampled
    boundary conditions missed by 104 cm.

## Files
- `rgo_model.py`: the test bed. It holds the aquifer (implicit Euler), the prior, the observation rows and the exact
  posterior.
- `rgo_net.py`: the FNO denoiser, GRF noise, the EDM loss and training (JAX, CPU). `python rgo_net.py 7000` takes about
  25 minutes and writes `res/rgo_params.npz`, `res/rgo_norm.json` and `res/rgo_train_loss.json`.
- `rgo_fundps.py`: the sampler, the solver as a linear map, the ensemble smoother and the paired evaluation.
  - `python rgo_fundps.py tune` chooses the guidance settings on two validation cases (`res/rgo_tune.json`).
  - `python rgo_fundps.py eval` writes `res/rgo_eval.json` and `res/rgo_case.npz`.
- `rgo_figs.py`: the four figures.
  - The scheme, after Figure 2 of FunDPS.
  - The Fushë-Kuqe boundary-condition map. It needs `../shiu_go/res/shiu_fk.json` and `chloride_fk/derived/`.
  - The results.
  - The data-value ladder.
- `text_rgo.py`: the text. Its numbers come from `res/`.
- `build_rgo_doc.py`: the Word document with OMML equations. It needs pandoc and uses `../ml_paradigms/word/omml.py`
  and `../spiranca_go/certain_coast/build_sota.py`.
- `res/run1_rain_channel/`: the first training, which put the weekly rain of the window in the fifth channel. Its
  diagnosis is described in Section 5 of the note.

Run everything with `bash run_all.sh`.
