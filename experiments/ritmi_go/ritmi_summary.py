"""Compact summary of RITMI-GO for review 43 (everything but the per-truth runs): ritmi_summary.json."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
R = json.load(open('ritmi_results.json'))
V = R['V']
out = dict(S=R['S'], HD=R['HD'], G={k: v for k, v in R['G'].items() if k not in ('greedy_rows', 'routine_rows')},
           T={k: v for k, v in R['T'].items() if k != 'profiles'},
           T_setup={k: R['T']['profiles'][k] for k in ('periods_days', 'wells', 'theta', 'errors')},
           V=dict(summary=V['summary'], n_truths=V['n_truths'], ne=V['ne'], na=V['na']))
json.dump(out, open('ritmi_summary.json', 'w'), indent=1)
print('wrote ritmi_summary.json')
