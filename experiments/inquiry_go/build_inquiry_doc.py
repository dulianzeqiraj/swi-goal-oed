"""Builds the proposal "INQUIRY-GO: the decisive question" (Word, OMML equations).
usage: python build_inquiry_doc.py OUT.docx [IONS.json]
res/inquiry_poc.json (python inquiry_poc.py) adds Section 3. IONS.json (python -I fk_ions.py WORKBOOK OUT) adds the
section on the chemistry of Fushe-Kuqe; that section holds field data and is not for the public repository."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'hipoteza_go'))
import inquiry_text as T  # noqa: E402
import inquiry_figs as HF  # noqa: E402
import build_hip_doc as B  # noqa: E402

VERIFY = ('Verification note. Every reference with a DOI was checked on Crossref on 24 November 2026. S25 and HMR '
          'were identified from the first page of the files in the author\'s folder. Of the twenty papers of that '
          'folder, the first pages of KN25, G26, S25, HMR, ZT21 and B22 and the author\'s reference list were read for '
          'this note; the others were not opened, and what is said of C26, H24 and A21 rests on their abstracts and '
          'on earlier notes. T23 is a set of lecture notes (Sections 1 to 4 were read), not a peer-reviewed source; J25 was read from the '
          'file provided by the author (abstract, introduction and the statements of the results). The '
          'searches of Section 1 and of the companion ideas were web searches made on 24 November 2026: SF14, PW89, PT23, '
          'PT16, K15, KV89, NG16, C15, Fa18, RG87, At25, Mi26, Ba17, Ma14, Ju21, St25, Li17 and Av04 are known from their '
          'abstracts, records or search summaries, and F26 from a search summary only. Every number '
          'of the synthetic test is computed by experiments/inquiry_go/inquiry_poc.py on the library of HYPOTHESIS-GO; '
          'the numbers of the chemistry section by fk_ions.py from the workbook of the chloride manuscript, which is '
          'not in the public repository. Generative AI tools assisted with the reading, the code and the drafting of '
          'this note; the author checks the statements, numbers and references and is responsible for them.')


def main(out, ions=None):
    rp = os.path.join(HERE, 'res', 'inquiry_poc.json')
    R = json.load(open(rp)) if os.path.exists(rp) else None
    ION = json.load(open(ions)) if ions else None
    work = tempfile.mkdtemp()
    figs = {'poc': HF.fig_poc(work, R)} if R else {}
    BL, _ = T.blocks(R, ION)
    B.REFS = T.REFS
    B.render(BL, T.REFS, figs, out, VERIFY, work)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'INQUIRY-GO.docx', sys.argv[2] if len(sys.argv) > 2 else None)
