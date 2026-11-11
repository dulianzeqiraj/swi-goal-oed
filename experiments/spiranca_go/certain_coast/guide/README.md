# CERTAIN-COAST illustrated guide

*Seawater intrusion, sensors, earthquakes and liquefaction: an illustrated guide to the CERTAIN-COAST methods, with
their equations* (English, Word with native equations, 30 pages, 27 figures).

| File | What it does |
|---|---|
| `guide_compute.m` | every computed result, with the open-source MATLAB package `certaincoast` (runs in MATLAB or GNU Octave) and the Fushë-Kuqe wells and boundary exported to CSV; writes `res/*.mat` |
| `fk_field_model.m` | the Fushë-Kuqe field model of Zeqiraj (2026), J. Hydrol. 680, 136559, written with the public package |
| `export_fk_csv.py` | the two sheets of `data/Fushe_Kuqe_All_Data.xlsx` the field model needs, as CSV |
| `guide_figs.py` | the 27 figures (`fig/`), from `res/` and `../../../tronditja_go/res` |
| `build_guide.py` | the Word document with OMML equations (pandoc through `../../../ml_paradigms/word/omml.py`) |

Rebuild (the certain-coast package is the public repository https://github.com/dulianzeqiraj/certain-coast):

    python -I export_fk_csv.py ../../../../data/Fushe_Kuqe_All_Data.xlsx /tmp/fkcsv
    octave --eval "guide_compute('/path/to/certain-coast', '/tmp/fkcsv', 'res')"     # about 1 minute
    python guide_figs.py
    python build_guide.py ../../../../docs/certain_coast/CERTAIN-COAST_Illustrated_Guide.docx

The Fushë-Kuqe data belong to the Albanian Geological Survey and to Prof. A. Beqiraj and are used with their
permission (see `data/README.txt`); they do not go into the public certain-coast repository.
