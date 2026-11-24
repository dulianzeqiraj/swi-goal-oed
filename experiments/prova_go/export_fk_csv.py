"""Export the two sheets of Fushe_Kuqe_All_Data.xlsx that fushe_kuqe_field_design.m reads
('3_Boundary_Coords' and '2_All_Wells', all columns, header row kept) to CSV files in data/.

Only needed for GNU Octave 8.4, which has no readmatrix/readtable for .xlsx (no io package):
a file-format conversion, nothing is changed. MATLAB reads the .xlsx directly.
Run once:  python3 export_fk_csv.py   (needs openpyxl)
"""
import csv, os, sys
import openpyxl

here = os.path.dirname(os.path.abspath(__file__))
xlsx = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', '..', 'data', 'Fushe_Kuqe_All_Data.xlsx')
wb = openpyxl.load_workbook(xlsx, data_only=True, read_only=True)
for sheet, name in [('3_Boundary_Coords', 'fk_boundary.csv'), ('2_All_Wells', 'fk_wells.csv')]:
    rows = list(wb[sheet].iter_rows(values_only=True))
    ncol = max(len(r) for r in rows)
    out = os.path.join(here, 'data', name)
    with open(out, 'w', newline='') as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for r in rows:
            r = list(r) + [None] * (ncol - len(r))
            w.writerow(['' if v is None else (repr(v) if isinstance(v, float) else v) for v in r])
    print('%s: %d rows x %d columns -> %s' % (sheet, len(rows), ncol, out))
