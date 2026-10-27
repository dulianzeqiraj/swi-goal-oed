"""Capture what each diagram passes to build_page (header, innovation, cards) and write it as JSON for the Word builder."""
import importlib, json, os, sys, tempfile
ML4 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ML4)
out = []
# diagram number k of the Word builder = position in this list (1-4: the paradigms, 5: introduction, 6: stakeholders)
DIAGRAMS = (('d1_robust_design', 'd1_robust_design'), ('d2_causal', 'd2_causal_generative'),
            ('d3_deep_rl', 'd3_deep_rl_theory'), ('d4_value_info', 'd4_value_of_information'),
            ('d0_problem', 'd0_problem_statement'), ('d5_stakeholders', 'd5_stakeholder_decisions'))
for name, html in DIAGRAMS:
    if not os.path.exists(os.path.join(ML4, name + '.py')):
        print('skipped (no builder):', name)
        continue
    m = importlib.import_module(name)
    cap = {}
    def fake(tex, **kw):
        cap.update(kw)
        return ''
    m.build_page = fake
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        m.build()
        os.chdir(cwd)
    out.append(dict(name=html, kicker=cap['kicker'], title=cap['title'], tags=cap['tags'], hero_y1=cap['hero_y1'],
                    innov_box=cap['innov_box'], innov=cap['innov'], cards=cap['cards']))
json.dump(out, open(os.path.join(ML4, 'word', 'content.json'), 'w'), ensure_ascii=False, indent=1)
print('exported', [(o['name'], o['hero_y1'], len(o['cards'])) for o in out])
