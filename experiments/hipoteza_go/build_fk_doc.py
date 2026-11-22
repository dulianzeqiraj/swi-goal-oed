"""Builds the internal note "Where does the chloride of Fushe-Kuqe come from?" (Word, OMML equations).
usage: python build_fk_doc.py OUT.docx      (needs res_fk/ensemble_fk.npz and res_fk/fk_results_second.json)
The note contains data of the Albanian Geological Survey and of A. Beqiraj: it is for the author and the data owners."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fk_figs as FF  # noqa: E402
from fk_text import blocks, REFS  # noqa: E402
from build_hip_doc import render  # noqa: E402

VERIFY = ('Verification note. Every reference with a DOI was checked on Crossref; Tartari (2001) is cited as reported '
          'in CB16 and was not seen. Every number is computed by the code in experiments/hipoteza_go (fk_core.py, '
          'fk_infer.py, fk_run.py) from the workbook of the chloride manuscript; the results are not in the public '
          'repository because the data owners\' permission covers the chloride manuscript only. Generative AI tools '
          'assisted with the code and the drafting of this note; the author checks the statements, numbers and '
          'references and is responsible for them.')


def main(out):
    R, E = FF.load('second')
    work = tempfile.mkdtemp()
    F = {'section': FF.fig_section(work, R, E)}
    FF.fig_calib(work, R, E); F['calib'] = True
    FF.fig_libs(work, R); F['libs'] = True
    FF.fig_couple(work); F['couple'] = True
    figs = {k: os.path.join(work, f'fk_{k}.png') for k in ('section', 'calib', 'libs', 'couple')}
    BL, s = blocks(R, E, F)
    render(BL, REFS, figs, out, VERIFY, work)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'FK_HIPOTEZA-GO.docx')
