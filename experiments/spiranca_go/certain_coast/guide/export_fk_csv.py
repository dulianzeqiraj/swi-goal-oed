"""Export the two sheets the demo needs (wells with K, boundary polygon) to CSV. usage: python -I export_fk.py XLSX OUTDIR"""
import csv, sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
rows = list(wb['2_All_Wells'].iter_rows(values_only=True))[1:]
with open(sys.argv[2] + '/wells.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Well_ID', 'X_GaussKruger', 'Y_GaussKruger', 'K_m_per_day'])
    n = 0
    for r in rows:
        if r[0] is None:
            continue
        k = r[3] if isinstance(r[3], (int, float)) else ''
        w.writerow([str(r[0]).strip(), r[1], r[2], k]); n += 1
rows = list(wb['3_Boundary_Coords'].iter_rows(values_only=True))[1:]
with open(sys.argv[2] + '/boundary.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['X_GaussKruger', 'Y_GaussKruger'])
    m = 0
    for r in rows:
        if isinstance(r[1], (int, float)) and isinstance(r[2], (int, float)):
            w.writerow([r[1], r[2]]); m += 1
print('wells', n, 'boundary vertices', m)
