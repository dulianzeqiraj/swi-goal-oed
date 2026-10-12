# KRITIK-GO: monitoring design for the early warning of a seawater-intrusion tipping point

A pumping well near a straight coast has a critical pumping rate, `Q_c`, beyond which the toe of
the saltwater interface jumps to the well. In Strack's (1976) single-potential solution for a
confined aquifer, this is a saddle-node bifurcation. As `Q -> Q_c`, the recovery rate `k` of the
toe falls to zero roughly as `sqrt(1 - Q/Q_c)`: this is critical slowing down. These scripts ask
where, and with which sensors, the approach to `Q_c` can be detected. The test aquifer has the
representative Fushë-Kuqe parameters `K = 100 m/d`, `B = 30 m`, `delta = 0.025`, `q0 = 1.5 m2/d`
and a well at `d = 2 km`, giving `Q_c = 3 651 m3/d`.

Requirements: Python 3 with NumPy, SciPy and matplotlib.

| File | What it does |
|---|---|
| `kritik.py` | Model, prior (30 % CV on K, 20 % on q0) and the classical early-warning test. 400 runs ramp pumping from 0.5 to 1.3 Q_c over 40 years and 400 null runs keep it constant. The alarm fires on the trend of the rolling lag-1 autocorrelation of salinity or head, with its threshold set for 5 % false alarms. Writes `kritik_results.json`. |
| `kritik2.py` | The KRITIK-GO criterion: the Fisher information on ln k at near-critical states, from paired head and salinity loggers (input–output identification, gain as a nuisance parameter). It is compared with the passive (salinity-only) criterion and with the status criterion. Validation uses 300 prior draws, with 10 years of weekly data at 0.85 Q_c and 0.6 Q_c, the input–output and passive estimators of k, and the oracle (toe observed without error). Writes `kritik2_results.json`. `python3 kritik2.py 300 200` also runs the preliminary ramp alarm with the input–output estimator. |
| `kritik_figs.py` | The two figures of the report. |

## Run

```bash
python3 kritik.py 400      # ~1 min
python3 kritik2.py 300     # ~10 min
python3 kritik_figs.py
```

## Main numbers

- Classical warning from salinity alone, at 5 % false alarms: the alarm comes at least 2 years before the jump in at most 7 % of runs, whatever the sensor position; from heads alone, in 1 %.
- The KRITIK-GO optimum is 1 200 m from the coast. The current toe is near 950 m and the critical toe lies at 1 339–1 671 m (10–90 % of the prior); the status criterion picks 800 m.
- Median relative error of k at 0.85 Q_c with paired loggers: 0.42–0.44 at 1 000–1 400 m (oracle 0.37), 0.78 at 800 m and 1.60 at 1 900 m. With salinity alone the errors are 0.78–1.54 at 1 000–1 400 m and 22–203 elsewhere.
- Spearman correlation between the criterion and the realized accuracy over 16 positions: 0.96 for KRITIK-GO, 0.21 for the status criterion.
