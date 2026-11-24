"""Shared helpers for Word sections: page-number fields and two-column sections."""
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def field_run(p, instr, size):
    """A PAGE or NUMPAGES field in the footer."""
    r = p.add_run(); r.font.size = Pt(size)
    for kind, text in (('begin', None), (None, instr), ('separate', None), (None, '1'), ('end', None)):
        if kind:
            e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), kind); r._r.append(e)
        elif text == instr:
            e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = f' {instr} '; r._r.append(e)
        else:
            e = OxmlElement('w:t'); e.text = text; r._r.append(e)


def two_columns(section):
    cols = section._sectPr.find(qn('w:cols'))
    if cols is None:
        cols = OxmlElement('w:cols'); section._sectPr.append(cols)
    cols.set(qn('w:num'), '2'); cols.set(qn('w:space'), str(int(0.6 * 567)))

