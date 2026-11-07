"""CERTAIN-COAST (NATO SPS proposal): consolidated references. Collects every source cited in the CERTAIN-COAST documents:
the 30 papers of the State of the Art [1]-[30] (sota_data.py) and the local study [L1]; the classic method references of
the Methodology [C1]-[C10] (build_methodology.py); NATO and SPS documents [N]; policy, legal and ethics frameworks [F];
data standards and repositories [D]. Adds where each source is used, a map from each innovation (M1-M6, P1-P5) to the
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
    ('NATO SPS. Call for proposals 2027-1.', 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/SPS-Call4proposals-2027-1.pdf', 'Partnership; Letters; CVs; Timeline; Security Relevance'),
    ('NATO (2009). Ceremony marks the accession of Albania and Croatia to NATO.', 'https://www.nato.int/cps/en/natohq/news_52902.htm', 'Security Relevance'),
    ('NATO (2022). NATO 2022 Strategic Concept, adopted at the Madrid Summit, 29 June 2022.', 'https://www.act.nato.int/wp-content/uploads/2023/05/290622-strategic-concept.pdf', 'Security Relevance'),
    ('NATO (2021). NATO Climate Change and Security Action Plan.', 'https://www.nato.int/cps/en/natohq/official_texts_185174.htm', 'Security Relevance'),
    ('NATO Allied Command Transformation (2024). NATO Climate Change and Security Centre of Excellence.', 'https://www.act.nato.int/article/ccascoe-2024/', 'Security Relevance'),
    ('NATO (2021). Strengthened Resilience Commitment.', 'https://www.nato.int/cps/en/natohq/official_texts_185340.htm', 'Security Relevance'),
    ('NATO (2023). Vilnius Summit Communiqué, 11 July 2023 (Alliance Resilience Objectives).', None, 'Security Relevance'),
    ('NATO (2024). Summary of NATO\'s revised Artificial Intelligence (AI) Strategy, 10 July 2024.', 'https://www.nato.int/en/about-us/official-texts-and-resources/official-texts/2024/07/10/summary-of-natos-revised-artificial-intelligence-ai-strategy', 'Security Relevance'),
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
    ('Trans Adriatic Pipeline AG (2020). Trans Adriatic Pipeline completes offshore section (105 km across the Adriatic Sea).', 'https://www.tap-ag.com/news/news-stories/trans-adriatic-pipeline-completes-offshore-section', 'Security Relevance; Letters'),
    ('Métois, M., Benjelloun, M., Lasserre, C., Grandin, R., Barrier, L., Dushi, E., Koçi, R. (2020). Subsidence associated with oil extraction, measured from time series analysis of Sentinel-1 data: case study of the Patos-Marinza oil field, Albania. Solid Earth 11, 363–378.', 'https://doi.org/10.5194/se-11-363-2020', 'Security Relevance'),
    ('INSTAT, Institute of Statistics of Albania (2025). Maritime Transport Statistics, Q2 2025.', 'https://www.instat.gov.al/en/themes/industry-trade-and-services/transport-accidents-and-characteristics-of-road-vehicles/publikimet/2025/maritime-transport-statistics-q2-2025/', 'Security Relevance'),
]

SHORT_NAMES = {}


def innovations():
    """(code, name, refs cited in the innovation statement, papers whose 'beyond' names the code)."""
    out = []
    for _, blocks in D.SECTIONS:
        for kind, content in blocks:
            if kind != 'b' or not isinstance(content, str):
                continue
            m = re.match(r'\*\*([MP]\d+)\. (.+?)\*\*', content)
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
            refs.update(re.findall(r'\[(X\d+)\]', content))   # other references of the State of the Art
            out.append([code, name, refs])
    for _, items in D.GROUPS:
        for it in items:
            for code in set(re.findall(r'\b([MP][1-6])\b', it['beyond'])):
                for row in out:
                    if row[0] == code:
                        row[2].add(it['n'])
    return out


def _title(cite):
    m = re.match(r'^.*? \((\d{4})\)\. (.+?)\. ', cite)
    return (m.group(2).lower()[:45] if m else cite.lower()[:45])


def dup_numbers(papers):
    sota = {_title(it['cite']): n for n, it in papers.items()}
    return [sota[_title(r_)] for r_ in BM.FRONTIER if _title(r_) in sota]


def method_frontier(papers):
    """Frontier references of the Methodology that are not already among the 30 State of the Art papers."""
    sota = {_title(it['cite']) for it in papers.values()}
    return [r_ for r_ in BM.FRONTIER if _title(r_) not in sota]


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
    frontier = method_frontier(papers)
    ccode = {_title(r_): f'C{i}' for i, r_ in enumerate(BM.REFS + frontier, start=1)}
    # sources of the innovations that are neither State of the Art papers nor Methodology references keep their X code
    xonly = [(code, cite, url) for code, cite, url in D.OTHER if not ccode.get(_title(cite))]
    n_total = (len(papers) + len(D.LOCAL) + len(xonly) + len(BM.REFS) + len(frontier) + len(NATO) + len(FRAME)
               + len(DATA))
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, f'This list brings together the **{n_total} sources** cited in the CERTAIN-COAST documents, in six groups with their own '
            'codes: the 30 papers of the State of the Art [1]–[30], the local study [L1] and further sources of the '
            'innovations [X]; the method references of the '
            'Methodology [C], classic and from the 2018–2026 frontier; NATO and SPS documents [N]; policy, legal and ethics frameworks [F]; and data standards and '
            'repositories [D]. Each entry says where it is used. A map links each innovation of the project to the references '
            'it builds on, and a compact key list is given for form fields with a word limit.', size=11)
    p = para(doc, 8); run(p, 'Verification. ', bold=True, size=9.5, color='52606D')
    run(p, D.NOTE + ' NATO, legal and policy sources were checked on the official pages through web search; one call summary '
           'is a third-party page and is marked as such.', italic=True, size=9.5, color='52606D')

    heading(doc, '1. Innovations and the references they build on', 13.5, before=4)
    xmap = {code: ccode.get(_title(cite)) or code for code, cite, _ in D.OTHER}

    def builds_on(refs):
        nums = [f'[{r}]' for r in sorted(r for r in refs if isinstance(r, int))]
        lets = sorted({xmap[r] for r in refs if isinstance(r, str) and xmap.get(r)}, key=lambda c: (c[0], int(c[1:])))
        return ', '.join(nums + [f'[{c}]' for c in lets])
    rows = [[c, n, builds_on(refs) or 'No direct precedent found: new in CERTAIN-COAST'] for c, n, refs in inv]
    t = table(doc, ['', 'Innovation', 'Builds on'], rows, [1.2, 10.0, 5.8], size=9.5)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    p = para(doc, 6, before=3)
    run(p, 'M: mathematical innovations; P: physical innovations (State of the Art, Section 4). References are those cited in each '
           'statement and those whose "beyond" note names the innovation.', italic=True, size=9.5, color='52606D')

    heading(doc, '2. Scientific literature (State of the Art)', 13.5, before=8)
    for grp, items in D.GROUPS:
        p = para(doc, 3, before=4); run(p, grp, bold=True, size=11, color='2E6DB4'); p.paragraph_format.keep_with_next = True
        for it in items:
            codes = sorted(set(re.findall(r'\b([MP][1-6])\b', it['beyond'])))
            free = it.get('free')
            extra = f'{it["inst"]}' + (f'; free copy: {free.replace("https://", "")}' if free and free != it['doi'] else
                                       ('' if free else f'; {it.get("free_note", "paywalled")}'))
            used = 'State of the Art' + (f'; innovations {", ".join(codes)}' if codes else '')
            entry(doc, str(it['n']), it['cite'], it['doi'], extra, used)
    p = para(doc, 3, before=4); run(p, 'Local study', bold=True, size=11, color='2E6DB4'); p.paragraph_format.keep_with_next = True
    for code, cite, url in D.LOCAL:
        entry(doc, code, cite, url, None, 'State of the Art; Security Relevance (2019 liquefaction at Durrës)')
    if xonly:
        p = para(doc, 3, before=4); run(p, 'Further sources of the innovations', bold=True, size=11, color='2E6DB4')
        p.paragraph_format.keep_with_next = True
        used_by = {c: [code for code, _n, refs in inv if c in refs] for c, _, _ in xonly}
        for code, cite, url in xonly:
            entry(doc, code, cite, url, None, 'State of the Art; Innovation' + (f'; innovations {", ".join(used_by[code])}'
                                                                                 if used_by[code] else ''))

    heading(doc, '3. Method references (Methodology)', 13.5, before=8)
    p = para(doc, 3, before=2); run(p, 'Classic methods', bold=True, size=11, color='2E6DB4'); p.paragraph_format.keep_with_next = True
    for i, r_ in enumerate(BM.REFS, start=1):
        entry(doc, f'C{i}', r_, None, None, 'Methodology')
    p = para(doc, 3, before=4); run(p, 'Frontier methods, 2018–2026', bold=True, size=11, color='2E6DB4'); p.paragraph_format.keep_with_next = True
    for i, r_ in enumerate(frontier, start=len(BM.REFS) + 1):
        entry(doc, f'C{i}', r_, None, None, 'Methodology')
    p = para(doc, 4, before=2)
    run(p, 'Frontier papers that are also among the 30 papers of the State of the Art are listed there only: '
           + ', '.join(f'[{n}]' for n in sorted(set(dup_numbers(papers)))) + '.', italic=True, size=9.5, color='52606D')

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
    bi = next(r_ for r_ in BM.REFS if r_.startswith('Boulanger'))
    key_lines = [compact(papers[k]['cite']) for k in KEY] + [compact(bi), 'United Nations (2015). Sendai Framework for Disaster Risk Reduction 2015–2030.']
    words = sum(len(x.split()) for x in key_lines)
    p = para(doc, 4); rich(p, f'{len(key_lines)} references, **{words} words**; first author and "et al." for more than two authors, no DOIs.', size=10)
    for i, x in enumerate(key_lines, start=1):
        q = para(doc, 2); q.paragraph_format.left_indent = Cm(0.7); q.paragraph_format.first_line_indent = Cm(-0.7)
        run(q, f'{i}. ', bold=True, size=10); run(q, x, size=10)
    doc.save(out)
    print('saved', out, '| sources', n_total, '| innovations', len(inv), '| key list', len(key_lines), 'refs', words, 'words')
    for c, n, refs in inv:
        print(c, n[:50], sorted(refs, key=str))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_References.docx')
