"""CERTAIN-COAST (NATO SPS proposal): consolidated references. Collects every source cited in the CERTAIN-COAST documents:
the 30 papers of the State of the Art [1]-[30] (sota_data.py) and the local study [L1]; the classic method references of
the Methodology [C1]-[C10] (build_methodology.py); NATO and SPS documents [N]; policy, legal and ethics frameworks [F];
data standards and repositories [D]. Adds where each source is used, a map from each innovation (M1-M5, P1-P5) to the
references it builds on (parsed from the State of the Art), and a compact key list with its word count for
space-limited form fields. Nothing is added that was not cited and checked in the earlier documents.

usage: python build_references.py OUT.docx"""
import os
import re
import sys

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, link  # noqa: E402
import sota_data as D  # noqa: E402
import build_methodology as BM  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

NATO = [
    ('NATO (2024). Science for Peace and Security Programme: overview and Key Priorities.', 'https://www.nato.int/cps/en/natohq/85291.htm', 'Security Relevance'),
    ('NATO. Resilience, civil preparedness and Article 3 (baseline requirements for national resilience).', 'https://www.nato.int/cps/en/natohq/topics_132722.htm', 'Security Relevance; Sustainability'),
    ('NATO Allied Maritime Command (2024). NATO officially launches new Maritime Centre for Security of Critical Undersea Infrastructure.', 'https://mc.nato.int/media-centre/news/2024/nato-officially-launches-new-nmcscui', 'Security Relevance'),
    ('NATO SPS (2023). Multi-Year Project Handbook.', 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/2023/SPS_MYP_Handbook.pdf', 'Budget; Partnership'),
    ('NATO SPS (2020). Multi-Year Project Handbook.', 'https://nato.int/content/dam/nato/webready/documents/sps/grants/2020/2020-sps-myp-handbook.pdf', 'Budget'),
    ('NATO SPS (2017). Multi-Year Project Handbook.', 'https://nato.int/content/dam/nato/webready/documents/sps/grants/2017/1705_SPS_MYP_Handbook.pdf', 'Budget'),
    ('NATO SPS. Call for proposals 2027-1.', 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/SPS-Call4proposals-2027-1.pdf', 'Partnership; Letters; CVs; Timeline'),
    ('NATO SPS (2023). Sample application form, Multi-Year Project.', 'https://nato.int/content/dam/nato/webready/documents/sps/grants/2023/sps-myp-sample-application-form.pdf', 'Abstract; Sustainability'),
    ('NATO SPS (2023). Sample application form, Multi-Year Project, Phase 1.', 'https://nato.int/content/dam/nato/webready/documents/sps/grants/2023/Sample-Application-Form-for-MYP-Phase-1.pdf', 'Abstract; Partnership'),
    ('NATO SPS. Grant mechanisms.', 'https://www.nato.int/en/about-us/organization/nato-structure/science-for-peace-and-security-hub/grant-mechanisms', 'Budget'),
    ('NATO SPS (2012, older rules). Funding of Multi-Year Projects.', 'https://www.nato.int/cps/en/natohq/88198.htm', 'Budget'),
    ('NATO SPS (2023). Project kick-off presentation (stipend rates).', 'https://www.ftmc.lt/uploads/images/pages/projektai/SPS%20Presentation%20-%20KoM%20-%20Richard%20Brewin.pdf', 'Budget'),
    ('NATO (2024). Allies endorse a new NATO policy on Women, Peace and Security at the Summit in Washington.', 'https://www.nato.int/en/news-and-events/articles/news/2024/07/10/allies-endorse-a-new-nato-policy-on-women-peace-and-security-at-the-summit-in-washington', 'Gender Balance'),
    ('NATO (2021). NATO supports women and girls in science.', 'https://www.nato.int/en/news-and-events/articles/news/2021/02/11/nato-supports-women-and-girls-in-science', 'Gender Balance'),
    ('NATO (2021). Summary of the NATO Artificial Intelligence Strategy (Principles of Responsible Use).', 'https://www.nato.int/en/about-us/official-texts-and-resources/official-texts/2021/10/22/summary-of-the-nato-artificial-intelligence-strategy', 'Ethics'),
]
FRAME = [
    ('United Nations (2015). Sendai Framework for Disaster Risk Reduction 2015–2030. UNDRR.', 'https://www.undrr.org/publication/sendai-framework-disaster-risk-reduction-2015-2030', 'Sustainability; Gender Balance'),
    ('United Nations. Sustainable Development Goals.', 'https://sdgs.un.org/goals', 'Sustainability'),
    ('United Nations. Early Warnings for All initiative.', 'https://www.un.org/en/climatechange/early-warnings-for-all', 'Sustainability'),
    ('Republic of Albania (2024). Law No. 124/2024 "On Personal Data Protection". Information and Data Protection Commissioner.', 'https://idp.al/wp-content/uploads/2025/03/Law-no.124-2024.pdf', 'Ethics; Data Management Plan'),
    ('European Union (2024). Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (AI Act).', 'https://eur-lex.europa.eu/eli/reg/2024/1689/oj', 'Ethics'),
    ('ALLEA (2023). The European Code of Conduct for Research Integrity, revised edition.', 'https://allea.org/code-of-conduct/', 'Ethics'),
]
DATA = [
    ('Zenodo, open research repository (CERN).', 'https://zenodo.org', 'Data Management Plan'),
    ('DataCite metadata schema.', 'https://datacite.org', 'Data Management Plan'),
    ('International Federation of Digital Seismograph Networks (FDSN): miniSEED and StationXML standards.', 'https://www.fdsn.org', 'Data Management Plan'),
    ('CF (Climate and Forecast) metadata conventions for NetCDF.', 'https://cfconventions.org', 'Data Management Plan'),
    ('EPSG:25834, ETRS89 / UTM zone 34N.', 'https://epsg.io/25834', 'Data Management Plan'),
]

SHORT_NAMES = {}


def innovations():
    """(code, name, refs cited in the innovation statement, papers whose 'beyond' names the code)."""
    out = []
    for _, blocks in D.SECTIONS:
        for kind, content in blocks:
            if kind != 'b' or not isinstance(content, str):
                continue
            m = re.match(r'\*\*([MP]\d)\. (.+?)\*\*', content)
            if not m:
                continue
            code, name = m.group(1), m.group(2).rstrip('.').rstrip(',')
            refs = set()
            for grp in re.findall(r'\[([0-9,\s–-]+)\]', content):
                for part in grp.split(','):
                    part = part.strip()
                    if re.match(r'^\d+[–-]\d+$', part):
                        a, b = re.split(r'[–-]', part); refs.update(range(int(a), int(b) + 1))
                    elif part.isdigit():
                        refs.add(int(part))
            out.append([code, name, refs])
    for _, items in D.GROUPS:
        for it in items:
            for code in set(re.findall(r'\b([MP][1-5])\b', it['beyond'])):
                for row in out:
                    if row[0] == code:
                        row[2].add(it['n'])
    return out


def compact(cite):
    """First author et al. (year). Title. Venue — no DOI, for space-limited fields."""
    m = re.match(r'^(.*?) \((\d{4})\)\. (.*)$', cite)
    if not m:
        return cite
    authors, year, rest = m.groups()
    first = authors.split(',')[0].strip()
    n_auth = authors.count('.,') + authors.count(' and ') + 1
    a = authors if n_auth <= 2 and 'et al' not in authors else f'{first} et al.'
    rest = re.sub(r',\s*e?\d{4,}[\w.]*$', '', rest).rstrip()
    if not rest.endswith('.'):
        rest += '.'
    return f'{a} ({year}). {rest}'


KEY = [1, 2, 4, 6, 8, 10, 16, 17, 19, 20, 23, 25, 29, 30]


def entry(doc, code, text, url=None, extra=None, used=None, size=10):
    p = para(doc, 1); p.paragraph_format.left_indent = Cm(1.0); p.paragraph_format.first_line_indent = Cm(-1.0)
    run(p, f'[{code}]  ', bold=True, size=size, color='1F3864'); run(p, text + ' ', size=size)
    if url:
        link(p, url, url.replace('https://', ''), size - 0.5)
    q = para(doc, 5); q.paragraph_format.left_indent = Cm(1.0)
    if extra:
        run(q, extra + '   ', italic=True, size=size - 1, color='52606D')
    if used:
        run(q, 'Used in: ' + used, italic=True, size=size - 1, color='1E8A5A')


def main(out):
    inv = innovations()
    papers = {it['n']: it for _, items in D.GROUPS for it in items}
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — References', bold=True, size=18, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    n_total = len(papers) + len(D.LOCAL) + len(BM.REFS) + len(NATO) + len(FRAME) + len(DATA)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, f'This list brings together the **{n_total} sources** cited in the CERTAIN-COAST documents, in six groups with their own '
            'codes: the 30 papers of the State of the Art [1]–[30] and the local study [L1]; the classic method references of '
            'the Methodology [C]; NATO and SPS documents [N]; policy, legal and ethics frameworks [F]; and data standards and '
            'repositories [D]. Each entry says where it is used. A map links each innovation of the project to the references '
            'it builds on, and a compact key list is given for form fields with a word limit.', size=11)
    p = para(doc, 8); run(p, 'Verification. ', bold=True, size=9.5, color='52606D')
    run(p, D.NOTE + ' NATO, legal and policy sources were checked on the official pages through web search; one call summary '
           'is a third-party page and is marked as such.', italic=True, size=9.5, color='52606D')

    heading(doc, '1. Innovations and the references they build on', 13.5, before=4)
    rows = [[c, n, ', '.join(f'[{r}]' for r in sorted(refs)) or 'No direct precedent found: new in CERTAIN-COAST'] for c, n, refs in inv]
    t = table(doc, ['', 'Innovation', 'Builds on'], rows, [1.2, 10.0, 5.8], size=9.5)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    p = para(doc, 6, before=3)
    run(p, 'M: mathematical innovations; P: physical innovations (State of the Art, Section 4). References are those cited in each '
           'statement and those whose "beyond" note names the innovation.', italic=True, size=9.5, color='52606D')

    heading(doc, '2. Scientific literature (State of the Art)', 13.5, before=8)
    for grp, items in D.GROUPS:
        p = para(doc, 3, before=4); run(p, grp, bold=True, size=11, color='2E6DB4'); p.paragraph_format.keep_with_next = True
        for it in items:
            codes = sorted(set(re.findall(r'\b([MP][1-5])\b', it['beyond'])))
            free = it.get('free')
            extra = f'{it["inst"]}' + (f'; free copy: {free.replace("https://", "")}' if free and free != it['doi'] else
                                       ('' if free else f'; {it.get("free_note", "paywalled")}'))
            used = 'State of the Art' + (f'; innovations {", ".join(codes)}' if codes else '')
            entry(doc, str(it['n']), it['cite'], it['doi'], extra, used)
    p = para(doc, 3, before=4); run(p, 'Local study', bold=True, size=11, color='2E6DB4'); p.paragraph_format.keep_with_next = True
    for code, cite, url in D.LOCAL:
        entry(doc, code, cite, url, None, 'State of the Art; Security Relevance (2019 liquefaction at Durrës)')

    heading(doc, '3. Classic method references (Methodology)', 13.5, before=8)
    for i, r_ in enumerate(BM.REFS, start=1):
        entry(doc, f'C{i}', r_, None, None, 'Methodology')

    heading(doc, '4. NATO and SPS documents', 13.5, before=8)
    for i, (t_, u, used) in enumerate(NATO, start=1):
        entry(doc, f'N{i}', t_, u, None, used)
    entry(doc, f'N{len(NATO) + 1}', 'Opportunities for Youth (2026). Summary of the NATO SPS 2027 call for proposals (third-party page).',
          'https://opportunitiesforyouth.org/2026/09/14/nato-science-for-peace-and-security-programme-2027-call-for-proposals-funding-for-multi-year-projects-and-scientific-events/',
          'Third-party summary: confirm dates on nato.int', 'Partnership; Timeline')

    heading(doc, '5. Policy, legal and ethics frameworks', 13.5, before=8)
    for i, (t_, u, used) in enumerate(FRAME, start=1):
        entry(doc, f'F{i}', t_, u, None, used)

    heading(doc, '6. Data standards and repositories', 13.5, before=8)
    for i, (t_, u, used) in enumerate(DATA, start=1):
        entry(doc, f'D{i}', t_, u, None, used)
    entry(doc, f'D{len(DATA) + 1}', 'Copernicus Sentinel-1 radar mission, European Union and European Space Agency (free and open data; '
          'products carry the attribution "contains modified Copernicus Sentinel data").', None, None, 'Methodology; Data Management Plan')

    heading(doc, '7. Compact key list for a form field with a word limit', 13.5, before=8)
    key_lines = [compact(papers[k]['cite']) for k in KEY] + [compact(BM.REFS[2]), 'United Nations (2015). Sendai Framework for Disaster Risk Reduction 2015–2030.']
    words = sum(len(x.split()) for x in key_lines)
    p = para(doc, 4); rich(p, f'{len(key_lines)} references, **{words} words**; first author and "et al." for more than two authors, no DOIs.', size=10)
    for i, x in enumerate(key_lines, start=1):
        q = para(doc, 2); q.paragraph_format.left_indent = Cm(0.7); q.paragraph_format.first_line_indent = Cm(-0.7)
        run(q, f'{i}. ', bold=True, size=10); run(q, x, size=10)
    doc.save(out)
    print('saved', out, '| sources', n_total, '| innovations', len(inv), '| key list', len(key_lines), 'refs', words, 'words')
    for c, n, refs in inv:
        print(c, n[:50], sorted(refs))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_References.docx')
