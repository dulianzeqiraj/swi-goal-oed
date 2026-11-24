"""Parse Table 2 of USGS SIR 2004-5067 (sources of ground water per well) from pdftotext -layout text."""
import re, sys, csv
lines = open(sys.argv[1], encoding='utf-8').read().split('\n')
code = r'(?:[BSNI](?:-[BSNI])*|—|\*)'
pat = re.compile(r'^(\S.*?)\s+(Upper|Lower|Pico)\s+(Low|Medium|High)\s+(' + code + r')\s+(' + code + r')\s+(' + code + r')\s+(' + code + r')\s+(Old|Recent|—)\s*(.*)$')
rows = []; cur = None
for l in lines:
    m = pat.match(l.strip())
    if m:
        cur = dict(name=m.group(1).strip(), aquifer=m.group(2), cl_range=m.group(3), clbr=m.group(4), cli=m.group(5),
                   clb=m.group(6), iso=m.group(7), age=m.group(8), comment=m.group(9).strip())
        rows.append(cur)
    elif cur is not None and l.startswith(' ' * 60) and l.strip() and not l.strip().startswith(('Table', 'Ground-Water', '[', ']')):
        cur['comment'] = (cur['comment'] + ' ' + l.strip()).strip()
    elif l.strip().startswith(('Table 2', 'Common name')) or not l.strip():
        cur = None if not l.strip() else cur
with open(sys.argv[2], 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows))
