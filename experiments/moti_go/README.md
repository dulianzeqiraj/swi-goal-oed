# MOTI-GO: one decisive rule for every weather, with margins for human error (Fushë-Kuqe stakeholders)

Innovation of literature review 59 (decisive stakeholder decisions from normal to extreme conditions, with objective and
subjective human factors: 20 more papers of 2020–2026 from Oxford, Caltech, MIT and ETH Zürich). *Moti* is Albanian for
the weather.

**Idea.** VENDIMI-GO (review 57, `../vendimi_go`) and RREZJA-GO (review 58, `../rrezja_go`) choose one pumping scale and
one recharge per site for a normal year, with calm stakeholders and perfect execution. MOTI-GO agrees the rule for every
weather *before* the weather comes. A weather regime is a storyline of a few numbers applied to the same calibrated
chloride ensemble of PUSI-GO, because the steady potential is linear in the recharge and in every well:

    phi = f_R · phi0 − s (1 + eps) · dd + q · RS − E · RH,     eps ~ N(mu_r, sigma_r)

- f_R: recharge factor (1 normal, 0.75 dry, 0.5 extreme drought);
- eps: implementation slippage, operators pumping more than licensed (objective human factor);
- E: unlicensed pumping by hotels and irrigators at four coastal cells near the supply wells (objective human factor);
- q_max: recharge capacity (5 000 m³/d per site in an extreme drought, 10 000 otherwise);
- crisis beliefs (subjective human factors, for decisions taken in the crisis only): polarisation of the stakeholders'
  tilts (kappa), a common pessimistic shift along the mixing-zone width (delta) and Prelec probability weighting (gamma).

Rules compared in each regime (no new data): **FW** the fair-weather plan of a normal year used in every regime;
**IC** the decision taken in the crisis (VENDIMI-GO rule with crisis beliefs and perceived risks, no allowance for
slippage or unlicensed pumping); **PC0** the pre-committed plan with the regime's physics only; **PC** the pre-committed
plan of MOTI-GO (regime physics, calm beliefs, exact Gauss–Hermite convolution over the slippage, unlicensed pumping
included; if nothing is admissible: emergency stop, no pumping and the largest recharge).

**Propositions (section 9 of the review).**
1. *S1, slippage.* With the slippage independent of the aquifer the certified risk is the exact convolution
   ∫ P_k(s(1+e), q) N(e; mu, sigma) de; it is non-decreasing in s, so the admissible set stays an interval and the rule
   stays decisive; the allowance is a smaller licence, not a vote.
2. *S2, the year as a whole.* Annual risk = Σ_r π_r R_r. A trigger that mistakes a regime for the next milder one with
   probability m adds m·Σ_r π_r (R_r(milder plan) − R_r) ≥ 0; mistaking it for a severer one never adds risk; triggers
   should be biased towards severity.
3. *S3, emergency stop.* With no pumping a draw fails iff f_R < f_i = max over A1, P10 of (T20 − q RS + E RH)/phi0, so the
   stop is safe for belief k iff f_R ≥ f*_k, the (1 − α) quantile of f_i under belief k; the group threshold is
   f* = max_k f*_k, falling linearly in the recharge.

## Files
- `moti.py` → `res/moti.json` (about 3 minutes on 4 cores; imports `../vendimi_go/vendimi.py`, which needs
  `../pusi_go/res/ens.npz`, made by `../pusi_go/pusi_run.py`).
- `moti_figs.py` → `res/figM1_moti.png`.
- `run_all.sh`.

## Results (same 2 000 truths and five stakeholders as VENDIMI-GO; α = 10%; no new data)
- Normal year: all rules choose s = 0.8, q = 5 000 m³/d per site; realised risk 0.044 (0.094 for the most cautious
  stakeholder).
- Dry year: the fair-weather plan fails, realised risk 0.231 (0.400 for the most cautious). Pre-committed plan s = 0.70,
  q = 10 000: 0.053 (0.094). Decided in the crisis: s = 0 (all supply pumping stopped) at the same recharge, 0.027
  (0.052), 8 442 m³/d of supply lost to fear; one subjective factor at a time gives s = 0.6 (polarisation), 0.55
  (salience) and 0.4 (probability weighting).
- Extreme drought (with heatwave): fair-weather plan 0.739 (0.822). Every adaptive rule ends in the emergency stop,
  realised risk 0.288 (0.311), most cautious 0.418 (0.446): the limit cannot be met with 5 000 m³/d of recharge.
  Banning the unlicensed coastal pumping during the stop gives 0.263 in both; a safe stop at f_R = 0.5 needs
  13 118–13 843 m³/d of recharge per site (5 825–6 533 at f_R = 0.75).
- Shapley attribution of the fair-weather plan's risk (base 0.045 in a normal year): dry year climate 0.161,
  operational slippage 0.018, unlicensed pumping 0.007; extreme drought 0.619, 0.049, 0.026; with heatwave 0.648,
  0.086, 0.043.
- Year as a whole (present climatology 60/25/10/5%): fair-weather 0.199 (0.292); pre-committed 0.084 (0.134), stop in
  15% of years; a trigger that is too mild 20% of the time raises it to 0.100, one that is too severe lowers it to
  0.081. Drier future (35/30/20/15%): fair-weather 0.356, pre-committed 0.135, stops in 35% of years.
- Emergency-stop threshold f* (group): 1.011 without recharge (a stop is never safe without recharge), 0.781–0.813
  with 5 000 m³/d per site and 0.601–0.626 with 10 000, for unlicensed pumping 0–4 000 m³/d; checked directly: risk
  0.115 at f* − 0.02 and 0.087 at f* + 0.02 (q = 5 000, E = 2 000).
- All monotonicity checks hold; phi0 > 0 for every draw.

Net water (pumped − 0.5 × recharged) is negative in dry and extreme years because large recharge is needed; pumped water
and recharge are reported separately in the review.
