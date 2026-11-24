# ZGJEDHJA-GO: sharp identification of a dynamic pumping-choice model with an unseen salinized state

Innovation of review 39, "Dynamic discrete choice, incomplete data and sharp identification: 20 papers for the
seawater-intrusion problem" (2020–2026). *Zgjedhja* is Albanian for choice.

**The problem.** The anchor paper of review 39 (Sasaki, Takahashi, Xin & Hu, "Dynamic discrete choice models with
incomplete data: sharp identification", Journal of Econometrics 236(1), 2023,
https://doi.org/10.1016/j.jeconom.2023.04.005) shows that when some states or transitions never appear in the data,
a dynamic discrete choice model is only set-identified, and it gives the sharp identified set. In a coastal well
field the state that matters most is exactly the one that is never seen: a well is abandoned once it salinizes, so
the panel contains no transitions into, and no payoffs in, the salinized state. ZGJEDHJA-GO asks:
* which pumping policies the data can still evaluate;
* which information (physics, sentinel wells, a survey) shrinks the identified set of each policy effect;
* how to split a monitoring budget so that the set of the effect the decision needs is as small as possible.

**The model.**
* States: covered salinity classes s = 0, …, 4 (class 4 is the frontier, where the front has arrived) and an
  absorbing salinized state B.
* Actions: light (a = 0) or hard (a = 1) pumping, logit shocks, discount factor β = 0.9.
* Payoffs: hard pumping pays θ_s = 1.5 − 0.25 s.
* Transitions on the covered states: one class up with probability (0.10, 0.40) and one class down with probability
  (0.30, 0.08) under (light, hard) pumping.
* The unseen part: from the frontier under hard pumping the well salinizes with probability q = 0.15. The salinized
  well is worth w = −1 per season (the cost of replacement water).
* Two policies, for wells that start in class 3, over 10 seasons:
  * a fee of τ = 0.5 per hard-pumping season (goal 1: fall in the 10-season risk of salinization);
  * managed recharge that halves q (goal 2: gain in hard-pumping seasons).

**The theory (section 9 of the review).**
* Proposition L:
  * (i) the value function on the covered states and θ_0, …, θ_3 are identified from light pumping
    (Magnac–Thesmar normalization);
  * (ii) the data identify only the index c(q) = θ_4 + β q w / (1 − β) for each anticipated intrusion
    probability q;
  * (iii) the fee effect depends on q only (checked numerically to 1e−16), while the recharge effect depends
    on (q, w);
  * (iv) the sharp identified sets of the two effects are images of H* = (Q × W) ∩ {θ_min ≤ θ_4 ≤ θ_3}, with
    θ_min = −1 (the shape restriction: salinity cannot raise the profit of hard pumping, and the payoff stays above
    a floor).
* Corollary: an analysis that builds transitions from the observed frequencies (q = 0) attributes the anticipated
  risk to low profits (θ_4 ≈ −1.8 instead of 0.5) and predicts that neither policy changes anything.
* Information sources:
  * a hydrogeological ensemble of the sharp-interface model gives q ∈ [0.08, 0.25];
  * sentinel wells at a stretch of coast where the front has already arrived give a Clopper–Pearson 95% interval
    for q;
  * a survey of n_s farmers on the cost of replacement water gives w within ±1.96/√n_s of the mean answer;
  * the shape restriction above.
* The ZGJEDHJA procedure:
  1. estimate the choice probabilities and the covered transitions from the panel;
  2. compute V, θ_0, …, θ_3 and c(q) by Proposition L;
  3. intersect the available information into H* and report the sharp sets of the policy effects, with
     Imbens–Manski intervals from a well-level bootstrap;
  4. to plan monitoring, choose the split of a budget between sentinel well-seasons (cost 1 each) and survey answers
     (cost 0.05 each) that minimizes the expected width of the identified set of the policy effect that the decision
     needs (goal-oriented value of information, Proposition 8 of the review).

## Results

**Sharp identified sets of the two policy effects (population, `zgjedhja.json`, part A).** Truth: the fee lowers the
10-season risk by 1.03 percentage points; recharge adds 0.51 hard-pumping seasons.

| Information | Fee effect (pp of risk) | Recharge effect (seasons) |
|---|---|---|
| Economic data only | −0.70 to 1.11 | 0.00 to 3.23 |
| + shape restriction | 0.21 to 1.11 | 0.14 to 0.66 |
| + shape + physics range of q | 0.70 to 1.11 | 0.14 to 0.65 |
| + shape + survey (100 answers) | 0.45 to 1.10 | 0.14 to 0.60 |
| + shape + physics + survey (100) | 0.70 to 1.10 | 0.20 to 0.60 |
| + shape + sentinels (200, k = 30) + survey (400) | 0.84 to 1.09 | 0.30 to 0.59 |
| Naive analysis (q = 0) | 0 (point) | 0 (point) |

With the economic data alone the sign of the fee effect is not identified: a fee can raise the risk when the
anticipated intrusion probability is large, because it lowers the value of keeping the well fresh. The shape
restriction fixes the sign. Physics information acts on the fee goal and the survey on the recharge goal; through
the shape restriction, information about w also narrows q.

**Goal-oriented monitoring (part B).** Expected width of the identified set at the best split and for single-source
designs (sentinels cost 1 per well-season, survey answers 0.05 each).

| Budget | Best share on sentinels: fee | Best share: recharge | Fee width (pp): best / all survey / all sentinels | Recharge width (seasons): best / all survey / all sentinels | Fee width with the recharge plan | Recharge width with the fee plan |
|---|---|---|---|---|---|---|
| 20 | 30% | 10% | 0.38 / 0.39 / 0.39 | 0.37 / 0.37 / 0.50 | 0.38 | 0.37 |
| 50 | 80% | 50% | 0.35 / 0.38 / 0.36 | 0.35 / 0.37 / 0.50 | 0.36 | 0.36 |
| 100 | 90% | 75% | 0.31 / 0.38 / 0.33 | 0.33 / 0.36 / 0.49 | 0.32 | 0.33 |
| 200 | 95% | 80% | 0.25 / 0.38 / 0.26 | 0.28 / 0.36 / 0.48 | 0.26 | 0.30 |
| 400 | 95% | 85% | 0.18 / 0.37 / 0.19 | 0.23 / 0.36 / 0.47 | 0.19 | 0.24 |

The best design depends on the goal: 90–95% of budgets of 100–400 on sentinels for the fee, 75–85% for recharge.
Using the plan of one goal for the other costs only a few per cent of width, but single-source designs are costly:
with a budget of 400, all sentinels leaves the recharge set 2.03 times wider than necessary, and all survey leaves
the fee set 2.06 times wider. The expected coverage of the truth by the design sets is at least 95% for the fee and
96% for recharge.

**Finite-sample inference (`zgjedhja_mc.json`, part C).** 500 panels of 300 wells over 12 seasons, physics range of
q, a survey of 400 answers and the shape restriction; 100 well-level bootstrap draws per panel.

| Policy effect | Truth | Mean estimated set | Mean Imbens–Manski 95% interval | Coverage of the truth | Interval excludes zero |
|---|---|---|---|---|---|
| Fee (pp of risk) | 1.03 | 0.70 to 1.08 | 0.53 to 1.32 | 96.0% | 100% |
| Recharge (seasons) | 0.51 | 0.22 to 0.59 | 0.17 to 0.69 | 99.6% | 100% |

The recharge interval is conservative, as expected when the truth lies inside a wide set. Across panels the naive
analysis gives θ_4 = −1.81 (standard deviation 0.17), far from the true 0.50.

## Files

| File | What it does |
|---|---|
| `zgjedhja_model.py` | Constants, covered transitions, Newton–Kantorovich solution of the model, inversion of choice probabilities (Proposition L), index c(q), policy paths, the two policy effects, panel simulation and estimation |
| `zgjedhja_ident.py` | Grids over (q, w), Clopper–Pearson interval, effect tables, identified sets under each combination of information, survey interval |
| `zgjedhja_exp.py` | Part A (identified sets), part B (monitoring design), part C (Monte Carlo with bootstrap Imbens–Manski intervals) |
| `zgjedhja_figs.py` | `figZ1_identified.png` (what the data identify) and `figZ2_design.png` (goal-oriented monitoring) |
| `zgjedhja.json`, `zgjedhja_mc.json` | Results used by review 39 |
| `run_all.sh` | Runs every stage in order |

## Run

```
bash experiments/zgjedhja_go/run_all.sh
```

The whole script takes about 25 minutes on 4 cores, most of it in part C (Python 3, NumPy, SciPy, Matplotlib).

## Limitations

* One well, one unseen state and a known discount factor. Real wells interact through shared drawdown (a dynamic
  game), and the discount factor should be bounded rather than fixed.
* The salinized state is reached only from the frontier under hard pumping. If light pumping can also salinize, the
  value function on the covered states is no longer identified from light pumping alone, and the sets widen.
* The sentinel wells are assumed exchangeable with the field's wells after the front arrives; a regime-switching
  model with covariate-dependent transitions would relax this.
* Choice probabilities are estimated by frequencies on five classes; a continuous salinity state needs a sieve or
  moment-inequality treatment.
* The test is a simulation with known truth. Applying it to Fushë-Kuqe needs pumping records, salinity classes per
  well and season, and a survey of replacement-water costs.
