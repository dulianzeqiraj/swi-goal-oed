"""Capture what each diagram passes to build_page (header, innovation, cards) and write it as JSON for the Word builder."""
import importlib, json, os, sys, tempfile
ML4 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ML4)
out = []
for name, html in (('d1_robust_design', 'd1_robust_design'), ('d2_causal', 'd2_causal_generative'),
                   ('d3_deep_rl', 'd3_deep_rl_theory'), ('d4_value_info', 'd4_value_of_information')):
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
