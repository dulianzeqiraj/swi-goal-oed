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
1. *S1, human error is a smaller licence.* With the overshoot independent of the aquifer, the certified risk is the
   convolution over the overshoot; it is non-decreasing in s and E and non-increasing in q, so the admissible pumping is
   an interval at each recharge level and the plan stays decisive; P̄(s) ≤ P(s(1+e_β)) + β for the upper β quantile e_β.
2. *S2, crisis perception is a tighter limit.* Prelec weighting w_γ(P) ≤ α is the calm rule with the limit
   α_γ = exp(−(−log α)^(1/γ)): 0.080, 0.059, 0.037 for γ = 0.9, 0.8, 0.7; polarisation κ multiplies a belief's relative
   entropy by about κ².
3. *S3, the year as a whole.* Yearly risk = Σ_r π_r Σ_r' M(r'|r) P̄_r(a_r'); for nested plans a trigger error towards
   severity never raises anyone's risk and one towards mildness does; triggers should err towards severity.
4. *S4, emergency stop.* With no pumping a draw fails iff f_R < f_θ = max over A1, P10 of (T − q RS + E RH)/phi0; the stop
   is safe iff f_R ≥ f* = max_k of the (1 − α) quantile of f_θ under belief k; f* falls with recharge and rises with E,
   and the recharge that makes a stop safe follows by bisection.

## Files
- `moti.py` → `res/moti.json` and `res/run_log.txt` (about 3 minutes on 4 cores; imports `../vendimi_go/vendimi.py`, which needs
  `../pusi_go/res/ens.npz`, made by `../pusi_go/pusi_run.py`).
- `moti_figs.py` → `res/figM1_moti.png`.
- `run_all.sh`.

## Results (same 2 000 truths and five stakeholders as VENDIMI-GO; α = 10%; no new data)
- Normal year: all rules choose s = 0.8, q = 5 000 m³/d per site; realised risk 0.044 (0.094 for the most cautious
  stakeholder).
- Dry year: the fair-weather plan fails, realised risk 0.231 (0.400 for the most cautious). Pre-committed plan s = 0.70,
  q = 10 000: 0.053 (0.094); with physics only s = 0.75 (0.100). Decided in the crisis: s = 0 at the same recharge,
  0.027 (0.052), 8 442 m³/d of supply lost to fear; one subjective factor at a time gives s = 0.6 (polarisation), 0.55
  (salience) and 0.4 (probability weighting).
- Extreme drought (with heatwave): fair-weather plan 0.739 (0.822). Every adaptive rule ends in the emergency stop,
  realised risk 0.288 (0.311), most cautious 0.418 (0.446). Banning the unlicensed coastal pumping during the stop gives
  0.263. A safe stop at f_R = 0.5 needs 13 973–14 714 m³/d of recharge per site with the certified margin (13 118–13 843
  nominal); with it the stop's risk is 0.060, 0.107 ± 0.009 for the most cautious stakeholder.
- Shapley attribution of the fair-weather plan's risk (base 0.045): dry year climate 0.161, overshoot 0.018, unlicensed
  pumping 0.007; extreme drought 0.619, 0.049, 0.026; with heatwave 0.648, 0.086, 0.043 (human share of the excess 13%,
  11% and 17%).
- Year as a whole (present climatology 60/25/10/5%): fair-weather 0.199 (0.292); pre-committed 0.084 (0.134), stop in
  15% of years; a trigger too mild in 20% of years gives 0.100, too severe 0.078; with the emergency recharge 0.049
  (0.086). Drier future (35/30/20/15%): fair-weather 0.356, pre-committed 0.135, with emergency recharge 0.052 (0.092).
- Emergency-stop threshold f* (group): 1.011 without recharge, 0.781–0.813 with 5 000 m³/d per site and 0.601–0.626
  with 10 000, for unlicensed pumping 0–4 000 m³/d; checked directly: 0.115 at f* − 0.02 and 0.087 at f* + 0.02.
- Checks: all monotonicity checks hold, phi0 > 0 for every draw, the plans are nested in every regime, the S1 bound
  holds at every scale tested, and probability weighting alone gives exactly the caps of the limit α_γ.

Net water (pumped − 0.5 × recharged) is negative in dry and extreme years because large recharge is needed; pumped water
and recharge are reported separately in the review.
