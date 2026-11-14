"""CERTAIN-COAST (NATO SPS proposal): five figures of the project plan for the "Additional files" PDF, drawn in the
visual style of the HALOMAR figures (review61/str_fig.py, cdv_fig.py, cm_fig.py, del_fig.py, gantt_fig.py): the same
canvas measured in inches, DejaVu Sans, the same colours and rounded boxes, a bold title line at the top and a dark
navy "New: ..." banner at the bottom.

  plan_fig1_structure.png      project structure: management, work packages with leads, interfaces, deliverables
  plan_fig2_dissemination.png  communication, dissemination and exploitation, audience by audience
  plan_fig3_team.png           team and competences
  plan_fig4_deliverables.png   deliverables: timeline by work package and table
  plan_fig5_gantt.png          Gantt chart: tasks, milestones, evidence gates, deliverables, critical path

Nothing is typed in twice. Work packages, tasks, months, deliverables, milestones and gates come from
build_workplan.py; leads and the inputs and outputs of each work package from build_wps.py; deliverable types,
access levels and what each feeds from build_deliverables.py; milestone leads from build_milestones.py; task labels,
the critical path and the task that produces each deliverable from build_schedule.py; the governance calendar from
build_timeline.py; audiences, products, months, indicators and licences from build_dissemination.py; the number of
risks from build_risk.py; the participants and their shares of time from section 6 of build_application.py (read
from its source, where the table is local to main()); team facts from institutions_data.py. The sentences in boxes
and banners repeat the builders' own texts. Every figure is checked for overlapping text, text outside its box or
the canvas, and the Albanian working names of the experiments (codenames.py).

Each figure is drawn on a 16 x 12 inch canvas for a 16 cm wide A4 column and saved as PNG at 300 dpi.

usage: python plan_figs.py OUTDIR"""
import ast
import os
import re
import sys
from functools import lru_cache

sys.dont_write_bytecode = True                     # leave no .pyc files next to the builders
import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle, Circle  # noqa: E402
from matplotlib.textpath import TextPath  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_workplan as W  # noqa: E402        work packages, tasks, months, deliverables, milestones, gates
import build_wps as WPS  # noqa: E402           leads; inputs and outputs of each work package
import build_deliverables as BD  # noqa: E402   deliverables with type and access; what each feeds
import build_milestones as BM  # noqa: E402     lead of each milestone
import build_schedule as BS  # noqa: E402       task labels, critical path, deliverable -> task
import build_timeline as BT  # noqa: E402       governance calendar
import build_dissemination as BDI  # noqa: E402  audiences, products and months, indicators, licences
import build_risk as BR  # noqa: E402           risk register
import build_gender as BG  # noqa: E402         gender targets
import institutions_data as ID  # noqa: E402    team facts of the three institutions
import codenames  # noqa: E402                  Albanian working names that must not appear

# ------------------------------------------------------------------------------------------- style (as HALOMAR)
INK, MUTED, NAVY, RED, GREEN = '#1f2933', '#52606d', '#1f3864', '#b03a3a', '#1e8a5a'
BLUE, ORANGE, TEAL, PURPLE = '#2e6db4', '#c27c12', '#0e7490', '#6a4fb3'
GATE, GATE_TXT, LIGHT, EDGE = '#f2b134', '#b7791f', '#f6f7f9', '#9aa5b1'
TINT = {BLUE: '#e8f1fb', PURPLE: '#f1ecfa', RED: '#fdecec', GREEN: '#e6f5ee', ORANGE: '#fff4e0', TEAL: '#e3f4f7',
        MUTED: '#eceff3', NAVY: '#e9edf5'}
YEARS = ['#c9daf2', '#8fb3e3', '#5b8fd0']
FONT = 'DejaVu Sans'
WF, HF, DPI = 16.0, 12.0, 300                       # canvas in inches; PNG resolution
COL = W.COL                                         # colour of each work package, as in the Work Plan


def style():
    """The HALOMAR font; undoes the rcParams that build_schedule.py sets when it is imported."""
    matplotlib.rcdefaults()
    plt.rcParams.update({'font.family': FONT})


def canvas(h=HF):
    style()
    fig = plt.figure(figsize=(WF, h))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, WF); ax.set_ylim(0, h); ax.axis('off')
    ax._inside = []                                 # (text, box) pairs checked by qa()
    return fig, ax


# drawing helpers of review61/str_fig.py (rbox, arrow, chip)
def rbox(ax, x0, y0, w, h, fc, ec, lw=1.4, r=0.08, z=1, ls='-'):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle=f'round,pad=0.012,rounding_size={r}', fc=fc, ec=ec, lw=lw,
                                zorder=z, ls=ls))


def arrow(ax, p0, p1, color=MUTED, lw=2.0, style='-|>', ms=16):
    ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle=style, color=color, lw=lw, mutation_scale=ms), zorder=4)


def chip(ax, x, y, text, col, ha='right', size=10.2, tcol='white', box=None):
    t = ax.text(x, y, text, ha=ha, va='center', fontsize=size, color=tcol, fontweight='bold', zorder=5,
                bbox=dict(boxstyle='round,pad=0.28,rounding_size=0.15', fc=col, ec='none'))
    if box is not None:
        ax._inside.append((t, box))
    return t


@lru_cache(maxsize=None)
def tw(s, size, weight='normal', fstyle='normal'):
    """Width of a one-line string in inches (TextPath, with 2% to spare against the renderer)."""
    if not s.strip():
        return 0.0
    fp = FontProperties(family=FONT, weight=weight, style=fstyle)
    return TextPath((0, 0), s, size=size, prop=fp).get_extents().width / 72.0 * 1.02


def wrap(text, width, size, weight='normal', fstyle='normal'):
    """Greedy word wrap to a width in inches; explicit newlines are kept."""
    out = []
    for par in text.split('\n'):
        line = ''
        for word in par.split(' '):
            cand = f'{line} {word}' if line else word
            if not line or tw(cand, size, weight, fstyle) <= width:
                line = cand
            else:
                out.append(line); line = word
        out.append(line)
    return '\n'.join(out)


def lines_h(n, size, ls):
    """Height in inches of n lines (matplotlib 3.11: linespacing times the font size per line)."""
    return n * ls * size / 72.0


def put(ax, x, y, text, width, size, color=INK, weight='normal', fstyle='normal', ls=1.15, ha='left', va='top',
        box=None, z=3, minsize=None, maxh=None):
    """Wrapped text; shrinks the font (down to minsize) until it fits maxh. Returns (artist, height in inches)."""
    minsize = minsize or size
    while True:
        t = wrap(text, width, size, weight, fstyle)
        n = t.count('\n') + 1
        if maxh is None or lines_h(n, size, ls) <= maxh or size <= minsize:
            break
        size -= 0.2
    art = ax.text(x, y, t, fontsize=size, color=color, fontweight=weight, style=fstyle, ha=ha, va=va, linespacing=ls,
                  zorder=z)
    if box is not None:
        ax._inside.append((art, box))
    return art, lines_h(n, size, ls)


def title(ax, text, h=HF, size=17.0):
    while tw(text, size, 'bold') > WF - 0.5:
        size -= 0.25
    ax.text(WF / 2, h - 0.3, text, ha='center', va='center', fontsize=size, fontweight='bold', color=INK)


def banner(ax, text, y0=0.2, h=1.0, size=12.2):
    """The dark navy band at the bottom that states what is new, in the builders' words."""
    rbox(ax, 0.2, y0, WF - 0.4, h, NAVY, NAVY, lw=0, r=0.1, z=0)
    put(ax, WF / 2, y0 + h / 2, text, WF - 1.2, size, color='white', ls=1.35, ha='center', va='center',
        box=(0.2, y0, WF - 0.2, y0 + h), minsize=10.5, maxh=h - 0.12)


def months(ms):
    return ', '.join(f'M{m}' for m in ms)


def low1(s):
    """Lower-case the first letter of an ordinary word (keeps acronyms such as NATO), as build_milestones.low1."""
    return BM.low1(s)


def qa(fig, ax, name):
    """Problems a reader would see: overlapping text, text outside its box or the canvas, Albanian working names."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    d = fig.dpi
    hh = fig.get_size_inches()[1]
    texts = [t for t in ax.texts if t.get_visible() and t.get_text().strip()]
    ext = {}
    for t in texts:
        b = t.get_window_extent(r)
        ext[id(t)] = (b.x0 / d, b.y0 / d, b.x1 / d, b.y1 / d)
    out = []
    working = re.compile(r'\b(' + '|'.join(codenames.NAMES) + r')\b')
    for t in texts:
        x0, y0, x1, y1 = ext[id(t)]
        s = t.get_text()
        if x0 < 0.05 or y0 < 0.05 or x1 > WF - 0.05 or y1 > hh - 0.05:
            out.append(f'outside the canvas: {s[:60]!r}')
        if codenames.english(s) != s or working.search(s):
            out.append(f'working name: {s[:60]!r}')
    for i, a in enumerate(texts):
        ax0, ay0, ax1, ay1 = ext[id(a)]
        for b in texts[i + 1:]:
            bx0, by0, bx1, by1 = ext[id(b)]
            if min(ax1, bx1) - max(ax0, bx0) > 0.01 and min(ay1, by1) - max(ay0, by0) > 0.01:
                out.append(f'overlap: {a.get_text()[:40]!r} / {b.get_text()[:40]!r}')
    for t, (bx0, by0, bx1, by1) in ax._inside:
        x0, y0, x1, y1 = ext[id(t)]
        if x0 < bx0 - 0.02 or x1 > bx1 + 0.02 or y0 < by0 - 0.02 or y1 > by1 + 0.02:
            out.append(f'outside its box: {t.get_text()[:60]!r}')
    for p in out:
        print(f'  [{name}] {p}')
    return out


def save(fig, ax, path):
    problems = qa(fig, ax, os.path.basename(path))
    fig.savefig(path, dpi=DPI, pil_kwargs={'optimize': True})
    plt.close(fig)
    return problems


# ---------------------------------------------------------------------------------------- data from the builders
WPD = {wp: dict(title=t, obj=o, span=s, goal=g, tasks=ts, dels=ds) for wp, t, o, s, g, ts, ds in W.WPS}
ORDER = [w[0] for w in W.WPS]
MS = {c: dict(month=m, name=n, ev=v) for c, m, n, v in W.MILESTONES}
GATES = W.GATES
GATE_LIST = sorted(GATES, key=lambda c: MS[c]['month'])
TASK = {c: dict(wp=wp, text=t, a=a, b=b) for wp in ORDER for c, t, (a, b) in WPD[wp]['tasks']}
SHORT = BS.TLAB                                     # short task labels of the Project Schedule
PRODUCT = {p[0]: p for p in BDI.PRODUCTS}           # dissemination products: name -> (name, content, audience, month, task)
KPI = {k[0]: k[1] for k in BDI.KPIS}                # dissemination indicators: name -> target
GOV = {g[0]: g[1] for g in BT.GOVERN}               # governance calendar of the Timeline


def pm(name):
    """Month(s) of a dissemination product, as written in build_dissemination.PRODUCTS."""
    return PRODUCT[name][3]


def at_least(name):
    """'At least 6' -> '≥ 6' for an indicator of build_dissemination.KPIS."""
    return KPI[name].replace('At least ', '≥ ')


def and_list(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


def lead(wp):
    """Lead of a work package (build_wps.LEAD): the first option, without the placeholder brackets. The optional
    additional NATO co-director named for WP1 is not part of the application (section 5: Co-Directors not required)."""
    return re.sub(r'[\[\]]', '', WPS.LEAD[wp].split(' or ')[0])


def team_of(wp):
    """The institution behind a lead team."""
    return 'Qatar University' if lead(wp).startswith('PPD') else 'UPT'


def dels_of(wp):
    """Deliverables of a work package in order: [(code, name, [months])]."""
    out = {}
    for c, n, m in WPD[wp]['dels']:
        out.setdefault(c, [n, []])[1].append(m)
    return [(c, n, ms) for c, (n, ms) in out.items()]


def del_chip(wp):
    return ' · '.join(f'{c} {months(ms)}' for c, n, ms in dels_of(wp))


def milestones_of(wp):
    """Milestones led (alone or jointly) by a work package (build_milestones.CARD)."""
    return [c for c, *_ in W.MILESTONES if wp in [x.strip() for x in BM.CARD[c][0].split(',')]]


def ms_label(c):
    return f'{c}{" gate" if c in GATES else ""}, M{MS[c]["month"]}'


def deliverables():
    """One entry per deliverable code (build_deliverables.items()), with all its months, ordered by code."""
    merged = {}
    for d in BD.items():
        merged.setdefault(d['code'], dict(d, months=[]))['months'].append(d['month'])
    return sorted(merged.values(), key=lambda d: tuple(int(x) for x in d['code'][1:].split('.')))


def participants():
    """Section 6 of build_application.py (Project Participants), read from its source: the table is local to main()."""
    src = open(os.path.join(HERE, 'build_application.py'), encoding='utf-8').read()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == 'main':
            for sub in ast.walk(node):
                if isinstance(sub, ast.Assign) and any(getattr(t, 'id', None) == 'part' for t in sub.targets):
                    keys = ('first', 'family', 'aff', 'pos', 'nat', 'tasks', 'time')
                    return [dict(zip(keys, row)) for row in ast.literal_eval(sub.value)]
    raise RuntimeError('participants table not found in build_application.py')


def form_text(name):
    """A module-level answer of build_application.py (HOW, AFTER, DATA, COMMS ...), read from its source."""
    src = open(os.path.join(HERE, 'build_application.py'), encoding='utf-8').read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError(f'{name} not found in build_application.py')


PEOPLE = participants()
P = {p['family']: p for p in PEOPLE}
NAMED = [p for p in PEOPLE if '[' not in p['time']]
RECRUIT = [p for p in PEOPLE if '[' in p['time']]   # 'To be recruited (2 people)': share of time still a placeholder


def pct(p):
    return int(p['time'].rstrip('%'))


def first_clause(s):
    return s.split(',')[0].strip()


NPD_NAME = first_clause(ID.UPT['glance'][0][1])                        # 'Assoc. Prof. Dr. Dulian Zeqiraj'
PPD_NAME = first_clause(dict(ID.PPD['glance'])['Project Director'])    # 'Prof. Jassim Al-Khayat'
HOW = form_text('HOW')
AFTER = form_text('AFTER')
DATA = form_text('DATA')
COMMS = form_text('COMMS')
REPO = re.search(r'https://(github\.com/[\w.-]+/[\w.-]+)', DATA).group(1)
NTESTS = re.search(r'(\d+) tests', DATA).group(1)
UPKEEP = re.search(r'about (€[\d,]+) per year', AFTER).group(1)
assert 'the Albanian team leads WP1–WP5 and WP7; Qatar University leads WP6' in HOW


# ======================================================================================= 1. project structure
def wp_tasks(ax, x, y, wp, width, size=10.2, ls=1.12, box=None, gap=0.045):
    """Task lines 'T2.1 label' of a work package; returns the y below the last line."""
    for code, text, (a, b) in WPD[wp]['tasks']:
        cw = tw(code, size, 'bold') + 0.09
        t = ax.text(x, y, code, fontsize=size, fontweight='bold', color=COL[wp], va='top', zorder=3)
        if box:
            ax._inside.append((t, box))
        _, h = put(ax, x + cw, y, SHORT[code], width - cw, size, ls=ls, box=box)
        y -= h + gap
    return y


def ms_mark(ax, x, y, c, size=10.0, box=None):
    """A milestone as a diamond and 'MS3 gate, M18' (gates in orange), centred on y."""
    g = c in GATES
    ax.plot([x + 0.07], [y], marker='D', ms=8.5, color=GATE if g else NAVY, mec=INK if g else 'white', mew=0.9, zorder=5)
    t = ax.text(x + 0.2, y, ms_label(c), fontsize=size, fontweight='bold', color=GATE_TXT if g else NAVY, va='center',
                zorder=5)
    if box:
        ax._inside.append((t, box))


def foot(ax, x0, x1, y0, wp, box, pitch=0.31):
    """Bottom rows of a work-package box: milestones on the left, one deliverable chip per code on the right.
    Returns the top of these rows."""
    ms, ds = milestones_of(wp), dels_of(wp)
    n = max(len(ms), len(ds))
    for k in range(n):
        y = y0 + 0.21 + (n - 1 - k) * pitch
        if k < len(ms):
            ms_mark(ax, x0 + 0.1, y, ms[k], box=box)
        if k < len(ds):
            c, _, mm = ds[k]
            chip(ax, x1 - 0.14, y, f'{c} {months(mm)}', COL[wp], box=box)
    return y0 + 0.21 + (n - 1) * pitch + 0.17


def band(ax, wp, y0, y1, ncol, extra=None):
    """A wide work-package box (WP4, WP6, WP7): title, lead, milestones and deliverables on one line, tasks below."""
    c = COL[wp]
    box = (0.2, y0, WF - 0.2, y1)
    rbox(ax, 0.2, y0, WF - 0.4, y1 - y0, TINT[c], c, lw=1.8, z=1)
    head = f'{wp}  {WPD[wp]["title"]}'
    ax.text(0.35, y1 - 0.09, head, fontsize=12.3, fontweight='bold', color=c, va='top', zorder=3)
    a, b = WPD[wp]['span']
    obj = 'all objectives' if WPD[wp]['obj'] == 'all' else f'objective {WPD[wp]["obj"]}'
    t = ax.text(0.35 + tw(head, 12.3, 'bold') + 0.3, y1 - 0.105, f'lead: {lead(wp)}, {team_of(wp)} · Months {a}–{b} · {obj}',
                fontsize=10.4, fontstyle='italic', color=c, va='top', zorder=3)
    ax._inside.append((t, box))
    chip(ax, WF - 0.36, y1 - 0.24, del_chip(wp), c, box=box)
    xm = WF - 0.36 - tw(del_chip(wp), 10.2, 'bold') - 0.5          # milestones, right to left of the chip
    for mc in reversed(milestones_of(wp)):
        xm -= tw(ms_label(mc), 10.0, 'bold') + 0.2
        ms_mark(ax, xm, y1 - 0.24, mc, box=box)
        xm -= 0.3
    cw = (WF - 0.7) / ncol
    for k, (code, text, _) in enumerate(WPD[wp]['tasks']):
        xx = 0.35 + k * cw
        t = ax.text(xx, y1 - 0.5, code, fontsize=10.4, fontweight='bold', color=c, va='top', zorder=3)
        ax._inside.append((t, box))
        put(ax, xx + tw(code, 10.4, 'bold') + 0.09, y1 - 0.5, SHORT[code], cw - 0.6, 10.4, box=box)
    if extra:
        k = len(WPD[wp]['tasks'])
        put(ax, 0.35 + k * cw, y1 - 0.5, extra, cw - 0.15, 10.0, color=MUTED, fstyle='italic', box=box)


def fig1_structure(path):
    fig, ax = canvas()
    title(ax, 'Project structure: seven work packages, what flows between them, and gates that decide each next step')

    # ---------- management band: who decides ----------
    yb0, yb1 = 9.58, 11.43
    rbox(ax, 0.2, yb0, WF - 0.4, yb1 - yb0, LIGHT, EDGE, lw=1.1, z=0)
    ax.text(0.35, yb1 - 0.08, 'Management', fontsize=12, fontweight='bold', color=MUTED, va='top')
    by0, by1 = yb0 + 0.1, yb1 - 0.37
    npd, ppd = P['Zeqiraj'], P['Al-Khayat']
    mgmt = [(3.55, 'Project Directors',
             [f'NATO country: {NPD_NAME}, {npd["aff"].split(", ")[-1]}; coordinator; {npd["time"]} of time',
              f'Partner country: {PPD_NAME}, {ppd["aff"]}; leads WP6; {ppd["time"]} of time']),
            (2.95, 'Steering committee',
             ['the Project Directors and the end-user\'s contact person and team; meets in '
              f'{GOV["Steering committee"].replace(", and", " and")}; decides every milestone']),
            (3.05, 'End-user: IGJEO',
             ['Institute of Geosciences, Polytechnic University of Tirana: agrees the warning thresholds (T3.1), reviews '
              'the live bulletins (T5.2), shares its station data; its staff use the bulletins in Months 34–36 (MS7)'])]
    x = 0.32
    for w, head, paras in mgmt:
        box = (x, by0, x + w, by1)
        rbox(ax, x, by0, w, by1 - by0, 'white', MUTED, lw=1.2, z=2)
        t = ax.text(x + 0.1, by1 - 0.08, head, fontsize=10.8, fontweight='bold', color=INK, va='top', zorder=3)
        ax._inside.append((t, box))
        y = by1 - 0.34
        for ptxt in paras:
            _, h = put(ax, x + 0.1, y, ptxt, w - 0.2, 10.0, ls=1.12, box=box)
            y -= h + 0.06
        x += w + 0.08
    xr = x + 0.12
    ax.text(xr + 0.02, yb1 - 0.08, 'Created for this project', fontsize=12, fontweight='bold', color=RED, va='top')
    extra = [('Evidence gates', and_list(f'{c} (M{MS[c]["month"]})' for c in GATE_LIST) +
              ': go, go with conditions or no-go, with the fallback fixed in advance'),
             ('Release gate', 'every output classified before release; asset-level results only to the end-user and '
                              'the competent national authorities'),
             ('Risk triggers', f'{len(BR.all_risks())} risks, each with an owner and a numeric trigger; reviewed every '
                               'month, escalated within two weeks')]
    ew = (WF - 0.32 - xr - 2 * 0.08) / 3
    for k, (head, body) in enumerate(extra):
        x0 = xr + k * (ew + 0.08)
        box = (x0, by0, x0 + ew, by1)
        rbox(ax, x0, by0, ew, by1 - by0, '#fdecec', RED, lw=1.3, z=2)
        t = ax.text(x0 + 0.09, by1 - 0.08, head, fontsize=10.8, fontweight='bold', color=RED, va='top', zorder=3)
        ax._inside.append((t, box))
        put(ax, x0 + 0.09, by1 - 0.34, body, ew - 0.18, 10.0, ls=1.12, box=box, minsize=9.4, maxh=by1 - by0 - 0.42)

    # ---------- WP4 on top: the network serves every warning ----------
    y40, y41 = 8.5, 9.46
    band(ax, 'WP4', y40, y41, 4)

    # ---------- middle row: the chain WP1 -> WP2 -> WP3 -> WP5 ----------
    ym0, ym1 = 4.78, 7.92
    gap = 1.06
    bw = (WF - 0.4 - 3 * gap) / 4
    mids = ['WP1', 'WP2', 'WP3', 'WP5']
    xs = {wp: 0.2 + k * (bw + gap) for k, wp in enumerate(mids)}
    for wp in mids:
        c, x0 = COL[wp], xs[wp]
        box = (x0, ym0, x0 + bw, ym1)
        rbox(ax, x0, ym0, bw, ym1 - ym0, TINT[c], c, lw=1.8, z=1)
        _, h = put(ax, x0 + 0.12, ym1 - 0.1, f'{wp}  {WPD[wp]["title"]}', bw - 0.24, 11.6, color=c, weight='bold',
                   ls=1.08, box=box)
        a, b = WPD[wp]['span']
        y = ym1 - 0.15 - h
        _, h2 = put(ax, x0 + 0.12, y, f'lead: {lead(wp)}, {team_of(wp)} · Months {a}–{b} · {WPD[wp]["obj"]}',
                    bw - 0.24, 10.0, color=c, fstyle='italic', box=box)
        ytop = foot(ax, x0, x0 + bw, ym0, wp, box)
        ylow = wp_tasks(ax, x0 + 0.12, y - h2 - 0.09, wp, bw - 0.24, box=box)
        if ylow < ytop:
            print(f'  [structure] {wp}: tasks run into the milestone and deliverable rows')
    # the chain, and the outcomes of live operation back to the alarms (build_wps.fig_links and IO)
    yf, yk = ym1 - 1.05, ym0 + 1.15
    for a_, b_, lab in (('WP1', 'WP2', 'R(t), land\nmotion,\nhead limit'), ('WP2', 'WP3', 'surrogate\nand its\nerror bound'),
                        ('WP3', 'WP5', 'certified\nalarms and\nproofs')):
        xa, xb = xs[a_] + bw, xs[b_]
        arrow(ax, (xa + 0.03, yf), (xb - 0.03, yf), color=COL[a_])
        ax.text((xa + xb) / 2, yf + 0.12, lab, ha='center', va='bottom', fontsize=9.8, color=COL[a_], fontweight='bold',
                linespacing=1.05)
    xa, xb = xs['WP3'] + bw, xs['WP5']
    arrow(ax, (xb - 0.03, yk), (xa + 0.03, yk), color=COL['WP5'])
    ax.text((xa + xb) / 2, yk - 0.12, 'outcomes:\nmargin\nupdate', ha='center', va='top', fontsize=9.8, color=COL['WP5'],
            fontweight='bold', linespacing=1.05)
    # WP4 <-> the middle row
    c4 = COL['WP4']
    for wp, dx, lab, way in (('WP1', 0.55, 'GNSS, corner reflectors', 'down'),
                             ('WP2', 0.55, 'heads, chloride,\nseismic velocity', 'down'),
                             ('WP2', 2.62, 'sensitivities\nfor the design', 'up'),
                             ('WP3', 0.55, 'value of each sensor', 'up'),
                             ('WP5', 0.55, 'data streams', 'down')):
        xx = xs[wp] + dx
        if way == 'down':
            arrow(ax, (xx, y40 - 0.02), (xx, ym1 + 0.03), color=c4)
        else:
            arrow(ax, (xx, ym1 + 0.03), (xx, y40 - 0.02), color=COL[wp])
        ax.text(xx + 0.12, (y40 + ym1) / 2, lab, ha='left', va='center', fontsize=10.0, color=c4 if way == 'down' else COL[wp],
                fontweight='bold', linespacing=1.05)

    # ---------- WP6 and WP7, wide ----------
    y60, y61 = 3.28, 4.22
    band(ax, 'WP6', y60, y61, 4)
    for wp, dx, lab in (('WP1', 1.4, 'results'), ('WP2', 1.4, 'results'), ('WP3', 0.55, 'verification statistics'),
                        ('WP5', 0.55, 'bulletin log and outcomes')):
        xx = xs[wp] + dx
        arrow(ax, (xx, ym0 - 0.03), (xx, y61 + 0.02), color=COL[wp])
        ax.text(xx + 0.12, (ym0 + y61) / 2, lab, ha='left', va='center', fontsize=10.0, color=COL[wp], fontweight='bold')
    y70, y71 = 2.48, 3.18
    fo = P['Ndreca']
    band(ax, 'WP7', y70, y71, 4, extra=f'grant finance: {fo["pos"].lower()}, {first_clause(fo["aff"])} of UPT, '
                                        f'{fo["time"]} of time')

    # ---------- phases and rhythm ----------
    yq0, yq1 = 1.34, 2.38
    rbox(ax, 0.2, yq0, 7.75, yq1 - yq0, '#fff6e5', GATE_TXT, lw=1.5)
    box = (0.2, yq0, 7.95, yq1)
    t = ax.text(0.35, yq1 - 0.09, 'Three phases, separated by evidence gates', fontsize=11.6, fontweight='bold',
                color=GATE_TXT, va='top')
    ax._inside.append((t, box))
    put(ax, 0.35, yq1 - 0.42, 'Observe and measure (Months 1–12); model and certify (Months 4–30); operate, verify and '
        'hand over (Months 22–36). Gates ' + and_list(f'{c} (Month {MS[c]["month"]})' for c in GATE_LIST) +
        ' decide whether each next step starts; each gate has a named fallback.', 7.45, 10.4, box=box)
    rbox(ax, 8.05, yq0, WF - 0.2 - 8.05, yq1 - yq0, '#e8f1fb', BLUE, lw=1.5)
    box = (8.05, yq0, WF - 0.2, yq1)
    t = ax.text(8.2, yq1 - 0.09, 'Rhythm and reporting', fontsize=11.6, fontweight='bold', color=BLUE, va='top')
    ax._inside.append((t, box))
    put(ax, 8.2, yq1 - 0.42, f'steering committee: {GOV["Steering committee"].replace(", and", " and")}; '
        'work-package leaders with the coordinator: monthly; risk review: '
        f'{GOV["Risk review"].split(";")[0].lower()}; reports to NATO SPS: {GOV["Reports to NATO SPS"].split(": ", 1)[1]}',
        WF - 0.2 - 8.05 - 0.3, 10.4, box=box)

    banner(ax, 'New in the structure: phases start on evidence, not on dates: calibration (MS3), the go/no-go for live '
               'operation (MS4) and the confirmation of the miss rates (MS5) are gates with rules fixed in advance; live '
               'operation feeds outcomes back to the alarms, and the alarms tell the network which sensors are worth most.',
           y0=0.2, h=1.02)
    return save(fig, ax, path)


# ======================================================================= 2. communication, dissemination, exploitation
def audience(prefix):
    rows = [a for a in BDI.AUDIENCES if a[0].startswith(prefix)]
    assert len(rows) == 1, prefix
    return rows[0]


def fig2_dissemination(path):
    fig, ax = canvas()
    title(ax, 'Communication, dissemination and exploitation: what each audience receives, through which channel, and when')
    # the two tiers (build_dissemination.LEAD)
    rbox(ax, 0.2, 10.97, WF - 0.4, 0.46, NAVY, NAVY, lw=0)
    sub = ('Two tiers: methods, software, verification statistics and policy conclusions are open; asset-level results '
           'go only to those who must act on them')
    size = 11.6
    while tw(sub, size, 'bold') > WF - 0.8:
        size -= 0.2
    ax.text(WF / 2, 11.2, sub, ha='center', va='center', fontsize=size, color='white', fontweight='bold')

    # three years as chevrons, events above (build_dissemination.PRODUCTS)
    years = [('Year 1', f'kick-off workshop and press release (M{pm("Kick-off stakeholder workshop")}); website '
                        f'(M{pm("Website and visual identity").split(",")[0]}); press release: network installed (M12)'),
             ('Year 2', f'training school (M{pm("Training school")}); mid-term workshop (M{pm("Mid-term workshop")}); '
                        f'back-testing protocol with a DOI (M{pm("Back-testing protocol (DOI)")}); live bulletins from M23'),
             ('Year 3', f'verification ledger each quarter (M24–36); open software and data, D6.1 '
                        f'(M{pm("Open software and data (D6.1)")}); transfer workshop (M{pm("Transfer workshop")}); policy '
                        f'brief, D6.2, and final workshop (M{pm("Policy brief and procedures (D6.2)")})')]
    yb0, yb1 = 9.86, 10.18
    seg = (WF - 0.4) / 3
    for k, ((yl, ev), fc) in enumerate(zip(years, YEARS)):
        x0, x1 = 0.2 + k * seg, 0.2 + (k + 1) * seg
        n = 0.0 if k == 0 else 0.14
        tip = 0.14 if k < 2 else 0.0
        ym = (yb0 + yb1) / 2
        ax.add_patch(Polygon([(x0, yb0), (x1 - tip, yb0), (x1, ym), (x1 - tip, yb1), (x0, yb1), (x0 + n, ym)],
                             closed=True, fc=fc, ec='white', lw=1.5, zorder=2))
        ax.text((x0 + x1) / 2, ym, yl, ha='center', va='center', fontsize=10.8, fontweight='bold',
                color=INK if k < 2 else 'white', zorder=3)
        put(ax, x0 + 0.12, 10.27, ev, seg - 0.3, 10.3, va='bottom', ls=1.12, box=(x0, 10.2, x1, 10.92))

    cols = [(0.2, 2.62), (2.72, 6.62), (6.72, 9.62), (9.72, 11.5), (11.6, 15.8)]
    head = ['Audience', 'What they receive', 'Channel', 'When', 'Attainable because']
    yh0, yh1 = 9.28, 9.7
    for (x0, x1), t in zip(cols, head):
        rbox(ax, x0, yh0, x1 - x0, yh1 - yh0, '#eceff3', EDGE, lw=1.0)
        ax.text((x0 + x1) / 2, (yh0 + yh1) / 2, t, ha='center', va='center', fontsize=11.5, fontweight='bold', color=INK)

    igj, per, civ, sps = audience('Institute of Geosciences'), audience('Authorities that issue'), \
        audience('Civil protection'), audience('NATO SPS')
    sci, oth, ecr, pub = audience('Scientific community'), audience('Operators and agencies of other coasts'), \
        audience('Students and early-career'), audience('Public and media')
    conf = PRODUCT['Conference presentations'][1].replace('For example ', '').replace(
        'SIAM Conference on Uncertainty Quantification', 'SIAM UQ').replace(' General Assembly', '').replace(' Fall Meeting', '')
    rows = [
        ('End-user', 'IGJEO, Institute of\nGeosciences, UPT', GREEN,
         low1(igj[2]), low1(igj[3]),
         f'bulletins M{pm("Live bulletins")}\ntraining M{pm("Training of the end-user" + chr(39) + "s staff and users")}\n'
         f'hand-over M{MS["MS7"]["month"]}',
         'sits on the steering committee and agrees the thresholds (T3.1); gives staff time and station data in kind, '
         'with no procurement, ownership or maintenance obligations'),
        ('Operators', 'wellfields, port and energy\nlanding; water-use permits', ORANGE,
         f'water supply and permit authorities: {low1(per[2])}; port and landfall: warnings of ground motion, '
         'liquefaction and storm surges',
         f'{low1(per[3])}; kick-off and mid-term workshops',
         f'workshops M{pm("Kick-off stakeholder workshop")}, M{pm("Mid-term workshop")}\n'
         f'rule by M{TASK["T5.3"]["b"]}\nbrief M{pm("Policy brief and procedures (D6.2)")}',
         'port and landfall warnings run on satellite radar, GNSS and public data, so no data or access from their '
         'owners is needed; the pumping rule is checked against the three hazards together (T5.3)'),
        ('Policy makers', 'national authorities, civil\nprotection, NATO SPS', BLUE,
         f'{low1(civ[2])} (D6.2); {low1(sps[2]).replace("; transfer workshop", "")}',
         f'{low1(civ[3])}; {low1(sps[3]).replace("reports; ", "")}',
         f'post-event reports\non trigger (T5.4)\nSPS reports M{pm("Reports to NATO SPS").replace(", ", ", M")}',
         'reached through IGJEO, which monitors earthquakes, weather and waters in Albania; each report to SPS falls '
         'on a decision: MS1, MS3, MS4 and MS5, MS7'),
        ('Scientific\ncommunity', 'and early-career\nresearchers', TEAL,
         f'{low1(sci[2])}; {low1(ecr[2])}',
         f'{low1(sci[3])}: {conf}; {low1(ecr[3])}',
         f'papers M{pm("Open-access papers (at least six)")}\nschool M{pm("Training school")}\n'
         f'protocol M{pm("Back-testing protocol (DOI)")}\nsoftware M{pm("Open software and data (D6.1)")}',
         f'the code is public from the start (MATLAB and free GNU Octave, Apache 2.0, {NTESTS} tests); open-access fees '
         'are budgeted (€6,000); two-month exchanges between the two countries'),
        ('Other coasts', 'operators and agencies;\nAllies and partners', PURPLE,
         low1(oth[2]), low1(oth[3]),
         f'workshop M{pm("Transfer workshop")}\nsoftware M{pm("Open software and data (D6.1)")}',
         'the method is tested on the east coast of Qatar within the project; D6.1 is accepted only when someone outside '
         'the team reproduces the synthetic coast'),
        ('Public\nand media', 'in Durrës and Albania', RED,
         low1(pub[2]), low1(pub[3]),
         f'press M{pm("Press releases").replace(", ", ", M")}\nwebsite from M{pm("Website and visual identity").split(",")[0]}'
         '\nledger each quarter',
         'press releases at natural moments: the start of live warnings, the training school, the hand-over; website, '
         'translation and printing (€1,500) and public events (€500) are budgeted'),
    ]
    rh, gy, top = 1.02, 0.07, 9.2
    for r, (name, sub_, col, rec, chan, when, why) in enumerate(rows):
        y0 = top - (r + 1) * rh - r * gy
        ym = y0 + rh / 2
        x0, x1 = cols[0]
        rbox(ax, x0, y0, x1 - x0, rh, col, col, lw=0)
        box = (x0, y0, x1, y0 + rh)
        nl = name.count('\n') + 1
        sl = sub_.count('\n') + 1
        hn, hs = lines_h(nl, 11.4, 1.05), lines_h(sl, 9.4, 1.08)
        yt = ym + (hn + hs + 0.05) / 2
        t = ax.text((x0 + x1) / 2, yt, name, ha='center', va='top', fontsize=11.4, fontweight='bold', color='white',
                    linespacing=1.05)
        ax._inside.append((t, box))
        t = ax.text((x0 + x1) / 2, yt - hn - 0.05, sub_, ha='center', va='top', fontsize=9.4, color='white',
                    linespacing=1.08)
        ax._inside.append((t, box))
        for k, txt, fc, tc, ha in ((1, rec, TINT[col], INK, 'left'), (2, chan, 'white', INK, 'left'),
                                   (3, when, TINT[col], col, 'center'), (4, why, TINT[col], INK, 'left')):
            cx0, cx1 = cols[k]
            rbox(ax, cx0, y0, cx1 - cx0, rh, fc, col, lw=1.0)
            box = (cx0, y0, cx1, y0 + rh)
            xt = cx0 + 0.1 if ha == 'left' else (cx0 + cx1) / 2
            put(ax, xt, ym, txt, cx1 - cx0 - 0.2, 10.2, color=tc, weight='bold' if k == 3 else 'normal', ls=1.12,
                ha=ha, va='center', box=box, minsize=9.4, maxh=rh - 0.1)

    # exploitation and indicators
    yv0, yv1 = 1.4, 2.66
    rbox(ax, 0.2, yv0, 9.42, yv1 - yv0, LIGHT, MUTED, lw=1.4)
    box = (0.2, yv0, 9.62, yv1)
    t = ax.text(0.35, yv1 - 0.1, 'Exploitation: used by the end-user, kept running in Albania, offered to other coasts',
                fontsize=11.8, fontweight='bold', color=INK, va='top')
    ax._inside.append((t, box))
    lic = BDI.RULES[1].split('**', 2)[-1].strip()
    put(ax, 0.35, yv1 - 0.45, 'IGJEO intends to use the bulletins and the open methods in its monitoring. The network stays '
        'in Albania with the Polytechnic University of Tirana, which keeps the bulletins running; an agreement (Month 33) '
        f'sets out how the sensors are kept, at about {UPKEEP} a year. Next: the other wellfields and coastal assets of '
        f'Albania, and coasts of Allies and partners. {lic}', 9.1, 10.3, box=box, minsize=9.6, maxh=yv1 - yv0 - 0.5)
    rbox(ax, 9.72, yv0, WF - 0.2 - 9.72, yv1 - yv0, '#e6f5ee', GREEN, lw=1.6)
    box = (9.72, yv0, WF - 0.2, yv1)
    t = ax.text(9.87, yv1 - 0.1, 'How we know it worked (Month 36)', fontsize=11.8, fontweight='bold', color=GREEN, va='top')
    ax._inside.append((t, box))
    put(ax, 9.87, yv1 - 0.45,
        f'{at_least("Open-access peer-reviewed papers")} open-access papers; {at_least("Conference presentations")} '
        f'conference presentations; {at_least("Professionals trained (at least four from IGJEO)")} professionals trained, '
        f'≥ 4 from IGJEO; {at_least("Early-career researchers trained")} early-career researchers; '
        f'{at_least("Groups testing the software on another coast")} groups test the software on another coast; '
        f'{at_least("Operating procedures adopted")} procedure adopted', WF - 0.2 - 9.72 - 0.3, 10.3, box=box,
        minsize=9.6, maxh=yv1 - yv0 - 0.5)

    banner(ax, 'New: open verification of a restricted service: each quarter the events, misses and false alarms of every '
               'alarm type are published with the 95% upper bound on its miss rate, without a single vulnerable location; '
               f'the back-testing protocol gets a DOI in Month {pm("Back-testing protocol (DOI)")}, before any result '
               f'exists; the code is public from the start: {REPO}.', y0=0.2, h=1.08)
    return save(fig, ax, path)


# ============================================================================================ 3. team and competences
GROUPS = [
    ('Model and certified warnings', BLUE, [
        ('Coupled model of the coast and its certified fast copy', 'WP2',
         'Zeqiraj builds it; Brakaj: certified error bounds; Beqiraj: aquifer properties (T2.3); Zeqo: well data (T2.1)'),
        ('Certified alarms and their margins', 'WP3', 'Zeqiraj: the alarm algorithm; Brakaj: the alarm margins'),
        ('Coastal motion and relative sea level', 'WP1', 'Zeqiraj'),
        ('Open-source code in MATLAB and GNU Octave', 'D6.1', 'Zeqiraj writes it; public from the start')]),
    ('Network, field data and live operation', ORANGE, [
        ('Monitoring network designed for the warnings', 'WP4', 'Zeqiraj'),
        ('Drilling and installing piezometers; pumping tests', 'T4.2, T5.3',
         'Seitaj; Zeqo: borehole design, quality control of drilling, casing and sealing'),
        ('Hydrogeology, groundwater chemistry and tracers', 'T4.1, T5.3',
         'Beqiraj; Jahja: sampling, chloride, major ions, tracers; Pregja: laboratory'),
        ('Earthquakes, weather and waters; live bulletins', 'T3.1, T5.2',
         'IGJEO (end-user): thresholds, station data, review of the bulletins; Zeqiraj: live operation')]),
    ('Transfer, training and management', GREEN, [
        ('Training, transfer and dissemination; a second coast', 'WP6',
         'Al-Khayat: transfer study on the east coast of Qatar, regional workshop, user-side review; two early-career '
         'researchers to be recruited'),
        ('Water quality and groundwater protection at the transfer site', 'T6.4', 'AlMomani'),
        ('Sampling, data curation and publications', 'WP6', 'Yigiterhan; Welter Giraldes'),
        ('Coordination and grant finance', 'WP7', 'Zeqiraj: coordination; Ndreca: financial management')]),
]


def check_groups():
    """Every named participant appears on a competence card, and every name on a card is a participant."""
    names = {p['family'] for p in NAMED}
    on_cards = set()
    for _, _, items in GROUPS:
        for _, _, who in items:
            on_cards |= {n for n in names if n in who}
    assert names == on_cards, names ^ on_cards


def fig3_team(path):
    check_groups()
    fig, ax = canvas()
    title(ax, 'Team and competences: what the project needs, who brings it, and the team today')

    # ---------- competences ----------
    px0, px1, py0, py1 = 0.2, 10.4, 5.62, 11.4
    rbox(ax, px0, py0, px1 - px0, py1 - py0, LIGHT, EDGE, lw=1.3, z=0)
    ax.text(px0 + 0.18, py1 - 0.13, 'The competences the project needs, and who brings them', fontsize=13,
            fontweight='bold', color=INK, va='top')
    cw, gx, ch, gy = (px1 - px0 - 0.3 - 2 * 0.1) / 3, 0.1, 1.06, 0.08
    for g, (gt, col, items) in enumerate(GROUPS):
        x0 = px0 + 0.15 + g * (cw + gx)
        rbox(ax, x0, 10.47, cw, 0.36, col, col, lw=0, r=0.07, z=2)
        ax.text(x0 + cw / 2, 10.65, gt, ha='center', va='center', fontsize=11, color='white', fontweight='bold', zorder=3)
        for k, (name, tag, who) in enumerate(items):
            y1 = 10.37 - k * (ch + gy)
            y0 = y1 - ch
            box = (x0, y0, x0 + cw, y1)
            rbox(ax, x0, y0, cw, ch, TINT[col], col, lw=1.3, r=0.07, z=2)
            _, h = put(ax, x0 + 0.1, y1 - 0.07, name, cw - 0.2, 10.6, weight='bold', ls=1.08, box=box)
            tagw = tw(tag, 10, 'bold')
            t = ax.text(x0 + cw - 0.1, y0 + 0.1, tag, ha='right', va='bottom', fontsize=10, color=col, fontweight='bold',
                        zorder=3)
            ax._inside.append((t, box))
            put(ax, x0 + 0.1, y1 - 0.12 - h, who, cw - 0.2, 9.8, color=MUTED, ls=1.1, box=box, minsize=9.2,
                maxh=ch - 0.2 - h - 0.12 if tagw > 0 else None)

    # ---------- the team today ----------
    xr, wr = 10.55, WF - 0.2 - 10.55
    rbox(ax, xr, py0, wr, py1 - py0, 'white', NAVY, lw=1.6, z=0)
    ax.text(xr + 0.18, py1 - 0.13, 'The team today', fontsize=13, fontweight='bold', color=NAVY, va='top')
    unis = []
    for p in NAMED:
        u = p['aff'].split(', ')[-1]
        if u not in unis:
            unis.append(u)
    ax.text(xr + 1.05, 10.42, str(len(NAMED)), ha='center', va='center', fontsize=30, fontweight='bold', color=NAVY)
    ax.text(xr + 1.05, 9.93, 'named participants', ha='center', va='center', fontsize=10.6, color=INK)
    ax.text(xr + 3.6, 10.42, str(len(unis)), ha='center', va='center', fontsize=30, fontweight='bold', color=NAVY)
    ax.text(xr + 3.6, 9.93, 'universities, Albania\nand Qatar', ha='center', va='center', fontsize=10.6, color=INK,
            linespacing=1.05)
    bx, bwid = xr + 1.72, wr - 1.72 - 0.62
    y = 9.5
    for u, label in ((unis[0], 'Albania: Polytechnic University of Tirana'), (unis[1], 'Qatar: Environmental Science Center, '
                                                                                       'Qatar University')):
        team = sorted([p for p in NAMED if p['aff'].endswith(u)], key=lambda p: -pct(p))
        tot = sum(pct(p) for p in team)
        t = ax.text(xr + 0.2, y, f'{label}', fontsize=10.4, fontweight='bold', color=INK, va='center')
        ax._inside.append((t, (xr, py0, xr + wr, py1)))
        y -= 0.27
        for p in team:
            role = ' (NPD)' if p is P['Zeqiraj'] else ' (PPD)' if p is P['Al-Khayat'] else ''
            ax.text(xr + 0.2, y, p['family'] + role, fontsize=10.2, color=INK, va='center')
            ax.add_patch(Rectangle((bx, y - 0.07), bwid, 0.14, fc='#e4e7eb', ec='none', zorder=1))
            ax.add_patch(Rectangle((bx, y - 0.07), bwid * pct(p) / 100, 0.14, fc=BLUE, ec='none', zorder=2))
            ax.text(bx + bwid * pct(p) / 100 + 0.06, y, p['time'], fontsize=10, color=INK, va='center', fontweight='bold',
                    zorder=3)
            y -= 0.235
        t = ax.text(xr + 0.2, y + 0.02, f'together {tot}% of one person\'s time' +
                    (f'; {RECRUIT[0]["family"].strip("()")} to be recruited ({RECRUIT[0]["pos"].lower()})'
                     if u in RECRUIT[0]['aff'] else ''), fontsize=9.6, color=MUTED, va='center', style='italic')
        ax._inside.append((t, (xr, py0, xr + wr, py1)))
        y -= 0.36
    put(ax, xr + 0.2, y + 0.08, 'and the end-user, IGJEO: a contact person and a small team, with staff time and data in '
        'kind; no SPS funds', wr - 0.4, 10.0, color=GREEN, weight='bold', box=(xr, py0, xr + wr, py1))

    # ---------- capacity the project builds ----------
    qx0, qx1, qy0, qy1 = 0.2, 10.4, 1.32, 5.47
    rbox(ax, qx0, qy0, qx1 - qx0, qy1 - qy0, '#f2f8fb', TEAL, lw=1.3, z=0)
    ax.text(qx0 + 0.18, qy1 - 0.13, 'Capacity the project builds, each with a target', fontsize=13, fontweight='bold',
            color=TEAL, va='top')
    ecr_women = [t[1] for t in BG.TARGETS if t[0].startswith('Early-career')][0]
    trained = at_least('Professionals trained (at least four from IGJEO)')
    cards = [('Trained professionals',
              f'the end-user\'s staff and the intended users learn to use the bulletins and what a certified miss rate '
              f'means (T6.2, Months {TASK["T6.2"]["a"]}–{TASK["T6.2"]["b"]})',
              'procedures and software documented for use without the project team',
              f'{trained}, of them ≥ 4 from IGJEO'),
             ('Early-career researchers',
              f'trained by doing: exchanges, the training school (Month {pm("Training school")}) and supervised work in '
              'WP1–WP5 (T6.1)',
              'two-month exchanges between the two countries; stipends',
              f'{at_least("Early-career researchers trained")}; {low1(ecr_women.split(" (")[0])}'),
             ('A second coast',
              'a transfer study on the east coast of Qatar with the project\'s tools and the Albanian team; a regional '
              'workshop',
              f'transfer workshop for other coasts in Month {pm("Transfer workshop")}',
              f'D6.1 reproduced outside the team, M{pm("Open software and data (D6.1)")}')]
    for g, (head, now, act, tgt) in enumerate(cards):
        x0 = qx0 + 0.15 + g * (cw + gx)
        y0, hc = 2.38, 2.48
        box = (x0, y0, x0 + cw, y0 + hc)
        rbox(ax, x0, y0, cw, hc, 'white', TEAL, lw=1.3, r=0.07, z=2)
        t = ax.text(x0 + 0.1, y0 + hc - 0.08, head, ha='left', va='top', fontsize=11.2, color=TEAL, fontweight='bold',
                    zorder=3)
        ax._inside.append((t, box))
        _, h = put(ax, x0 + 0.1, y0 + hc - 0.44, now, cw - 0.2, 10.2, ls=1.13, box=box)
        put(ax, x0 + 0.1, y0 + hc - 0.56 - h, act, cw - 0.2, 10.2, color=GREEN, fstyle='italic', ls=1.13, box=box)
        rbox(ax, x0 + 0.08, y0 + 0.08, cw - 0.16, 0.5, GREEN, GREEN, lw=0, r=0.06, z=3)
        put(ax, x0 + cw / 2, y0 + 0.33, tgt, cw - 0.3, 10.4, color='white', weight='bold', ha='center', va='center',
            ls=1.08, z=4, box=box, minsize=9.4, maxh=0.46)
    # the starting point
    rbox(ax, qx0 + 0.15, 1.44, qx1 - qx0 - 0.3, 0.82, 'white', EDGE, lw=1.0, r=0.06, z=2)
    box = (qx0 + 0.15, 1.44, qx1 - 0.15, 2.26)
    t = ax.text(qx0 + 0.27, 2.17, 'Starting point (2026):', fontsize=10.4, fontweight='bold', color=INK, va='top', zorder=3)
    ax._inside.append((t, box))
    put(ax, qx0 + 0.27 + tw('Starting point (2026):', 10.4, 'bold') + 0.1, 2.17,
        'eleven reviews with tested methods and a calibrated chloride model of the aquifer that supplies Durrës; the '
        f'open code with {NTESTS} tests; papers of the team in Journal of Hydrology, Journal of Contaminant Hydrology '
        'and Journal of Hazardous Materials Advances; on the Qatar side, projects on shoreline change and on wind and '
        'waves (2025–2027)', qx1 - qx0 - 0.5 - tw('Starting point (2026):', 10.4, 'bold') - 0.1, 10.0, box=box,
        minsize=9.4, maxh=0.7)

    # ---------- how the team works ----------
    rbox(ax, xr, qy0, wr, qy1 - qy0, '#e6f5ee', GREEN, lw=1.6, z=0)
    ax.text(xr + 0.18, qy1 - 0.13, 'How the team works', fontsize=13, fontweight='bold', color=GREEN, va='top')
    collab = HOW.split('Collaboration. ')[1]
    bullets = ['the NPD builds the coupled model and the alarm algorithm and releases them as open-source MATLAB and '
               'Octave code; the Albanian team leads WP1–WP5 and WP7',
               'Qatar University leads WP6, a transfer study on the east coast of Qatar and a user-side review of the '
               'bulletins',
               'early-career researchers of both countries work across work packages, with two-month exchanges',
               'the end-user agrees the thresholds and reviews the bulletins; a steering committee with it meets every '
               'six months, and each gate has a named fallback']
    assert all(b.split(';')[0].split(',')[0][4:30].lower() in collab.lower() for b in bullets), 'bullets left the form text'
    y = qy1 - 0.58
    box = (xr, qy0, xr + wr, qy1)
    for b in bullets:
        ax.text(xr + 0.2, y, '•', fontsize=12, color=GREEN, va='top', fontweight='bold')
        _, h = put(ax, xr + 0.42, y, b, wr - 0.6, 10.6, ls=1.15, box=box)
        y -= h + 0.16

    banner(ax, 'New in how the team is built: the model and the alarm algorithm stay with the team that builds them and '
               'are open source from the start; the partner-country team leads training and transfer and tests the method '
               'on a second coast within the project; the end-user agrees the thresholds before the alarms are designed.',
           y0=0.2, h=0.98)
    return save(fig, ax, path)


# ======================================================================================= 4. deliverables
TYPES = {'Report': ('v', RED), 'Data, report': ('s', ORANGE), 'Model': ('^', TEAL), 'Software': ('D', PURPLE),
         'Demonstrator': ('p', GREEN), 'Software, data': ('h', NAVY)}
ACCESS = {'Public': 'public', 'Restricted': 'restricted', 'Public + restricted annex': 'public + annex'}


def fig4_deliverables(path):
    its = deliverables()
    n_items = len(BD.items())
    fig, ax = canvas()
    title(ax, f'Deliverables: when each of the {n_items} falls, who produces it, and what it serves')

    # ---------- timeline ----------
    X0, X1 = 3.45, 15.55
    X = lambda m: X0 + (X1 - X0) * m / 36.0  # noqa: E731
    yh0, yh1 = 10.92, 11.26
    for k in range(3):
        ax.add_patch(Rectangle((X(12 * k), yh0), X(12 * k + 12) - X(12 * k), yh1 - yh0, fc=YEARS[k], ec='white', lw=1.5,
                               zorder=2))
        ax.text((X(12 * k) + X(12 * k + 12)) / 2, (yh0 + yh1) / 2, f'Year {k + 1}', ha='center', va='center', fontsize=11,
                fontweight='bold', color=INK if k < 2 else 'white', zorder=3)
    lh, top = 0.47, 10.86
    for r, wp in enumerate(ORDER):
        y0 = top - (r + 1) * lh
        c = COL[wp]
        ax.add_patch(Rectangle((X(0), y0 + 0.03), X(36) - X(0), lh - 0.06, fc=TINT[c], ec='none', zorder=0))
        rbox(ax, 0.2, y0 + 0.03, 3.1, lh - 0.06, c, c, lw=0)
        ax.text(0.32, y0 + lh / 2, wp, ha='left', va='center', fontsize=10.8, fontweight='bold', color='white')
        ax.text(0.95, y0 + lh / 2, BT.SHORTWP[wp], ha='left', va='center', fontsize=10.2, color='white')
    ybot = top - len(ORDER) * lh
    for c_, mm in ((c, MS[c]['month']) for c in MS):
        g = c_ in GATES
        ax.plot([X(mm), X(mm)], [ybot, top], color=GATE if g else '#9aa3ae', lw=1.6 if g else 1.0, ls='--', zorder=1)
    ax.plot([X(0), X(36)], [ybot, ybot], color=INK, lw=1.4, zorder=2)
    for m in range(0, 37, 6):
        ax.plot([X(m), X(m)], [ybot - 0.06, ybot], color=INK, lw=1.2, zorder=2)
        ax.text(X(m), ybot - 0.1, f'M{m}' if m % 12 else f'Month {m}', ha='center', va='top',
                fontsize=9.8 if m % 12 else 10.4, color=MUTED if m % 12 else INK, fontweight='normal' if m % 12 else 'bold')
    for c_ in MS:
        g, mm = c_ in GATES, MS[c_]['month']
        dx = -0.12 if c_ == 'MS6' else (0.12 if c_ == 'MS7' else 0)
        ax.text(X(mm) + dx, ybot - 0.38, c_ + ('\ngate' if g else ''), ha='center', va='top', fontsize=10,
                color=GATE_TXT if g else NAVY, fontweight='bold', linespacing=1.0)
    for d in its:
        mk, col = TYPES[d['type']]
        r = ORDER.index(d['wp'])
        yc = top - r * lh - lh / 2
        for m in d['months']:
            ax.plot([X(m)], [yc - 0.05], marker=mk, ms=11.5, color=col, mec='white', mew=1.2, zorder=4)
            ax.text(X(m), yc + 0.07, d['code'], ha='center', va='bottom', fontsize=10, fontweight='bold', color=INK, zorder=5)

    # ---------- table ----------
    cols = [(0.2, 0.95, 'D'), (1.0, 4.85, 'Deliverable'), (4.9, 7.75, 'Type · access'), (7.8, 9.95, 'Lead'),
            (10.0, 11.35, 'Month'), (11.4, 15.8, 'Serves: milestone · feeds')]
    th0, th1 = 6.48, 6.88
    for x0, x1, t in cols:
        rbox(ax, x0, th0, x1 - x0, th1 - th0, '#eceff3', EDGE, lw=1.0)
        ax.text((x0 + x1) / 2, (th0 + th1) / 2, t, ha='center', va='center', fontsize=11, fontweight='bold', color=INK)
    rh = 0.335
    for i, d in enumerate(its):
        y1 = th0 - 0.04 - i * rh
        y0 = y1 - rh + 0.03
        ym = (y0 + y1) / 2
        ax.add_patch(Rectangle((0.2, y0), WF - 0.4, y1 - y0, fc=LIGHT if i % 2 == 0 else 'white', ec='none', zorder=0))
        mk, col = TYPES[d['type']]
        cells = [(cols[0], d['code'], 'center', 'bold', INK), (cols[1], d['name'], 'left', 'normal', INK)]
        for (x0, x1, _), txt, ha, wt, tc in cells:
            put(ax, (x0 + x1) / 2 if ha == 'center' else x0 + 0.08, ym, txt, x1 - x0 - 0.1, 10.4, color=tc, weight=wt,
                ha=ha, va='center', box=(x0, y0, x1, y1), minsize=9.4, maxh=rh)
        x0 = cols[2][0]
        ax.plot([x0 + 0.17], [ym], marker=mk, ms=10, color=col, mec='white', mew=1.0)
        tt = d['type'].lower()
        ax.text(x0 + 0.36, ym, tt, ha='left', va='center', fontsize=10.4, color=col, fontweight='bold')
        ax.text(x0 + 0.36 + tw(tt, 10.4, 'bold') + 0.08, ym, '· ' + ACCESS[d['cls']], ha='left', va='center',
                fontsize=10.2, color=MUTED)
        put(ax, (cols[3][0] + cols[3][1]) / 2, ym, lead(d['wp']), cols[3][1] - cols[3][0] - 0.1, 10.4, ha='center',
            va='center', box=cols[3][:2] and (cols[3][0], y0, cols[3][1], y1), minsize=9.4, maxh=rh)
        put(ax, (cols[4][0] + cols[4][1]) / 2, ym, months(d['months']), cols[4][1] - cols[4][0] - 0.1, 10.4,
            weight='bold', ha='center', va='center', box=(cols[4][0], y0, cols[4][1], y1), minsize=9.0, maxh=rh)
        ms = BD.ms_of(d['code'])
        feeds = BD.DESC[d['code']][5]
        x0, x1 = cols[5][0] + 0.08, cols[5][1]
        if ms != '—':
            g = '(gate)' in ms
            lab = ms.replace(' (gate)', ' gate')
            ax.text(x0, ym, lab, ha='left', va='center', fontsize=10.4, fontweight='bold', color=GATE_TXT if g else NAVY)
            x0 += tw(lab, 10.4, 'bold') + 0.1
            ax.text(x0, ym, '·', ha='left', va='center', fontsize=10.4, color=MUTED)
            x0 += 0.16
        put(ax, x0, ym, feeds, x1 - x0 - 0.05, 10.2, ha='left', va='center', box=(cols[5][0], y0, x1, y1), minsize=9.0,
            maxh=rh)
    yn = th0 - 0.04 - len(its) * rh - 0.08
    put(ax, 0.25, yn, f'Lead: NPD team, {P["Zeqiraj"]["aff"].split(", ")[-1]} (Albania); PPD team, '
        f'{P["Al-Khayat"]["aff"]} (Qatar). Access: public; restricted; or public with a restricted annex for asset-level '
        f'results. Months count from the start; D7.2 is the progress report at each SPS reporting milestone.',
        WF - 0.5, 9.8, color=MUTED, fstyle='italic', box=(0.2, 1.3, WF - 0.2, yn + 0.02))

    banner(ax, 'New: every deliverable has a pass test stated in advance, and three of them decide the evidence gates (D2.1, '
               'D2.2 and D3.2 at Months 18, 22 and 27); the back-testing protocol of D3.2 is published with a DOI before '
               'the results; D6.1 is accepted only when someone outside the team installs the software and reproduces '
               'the synthetic coast.', y0=0.2, h=1.0)
    return save(fig, ax, path)


# ======================================================================================= 5. Gantt chart
def fig5_gantt(path):
    fig, ax = canvas()
    title(ax, f'Gantt chart: seven work packages, {len(TASK)} tasks, milestones MS1–MS7 with three evidence gates, '
              'and the deliverables')
    X0, X1 = 5.35, 15.72
    X = lambda m: X0 + (X1 - X0) * (m - 1) / 36.0  # noqa: E731   month m occupies [X(m), X(m + 1)]
    rows = []
    for wp in ORDER:
        rows.append(('wp', wp))
        rows += [('t', c) for c, *_ in WPD[wp]['tasks']]
    top, rh = 10.42, 0.232
    ybot = top - len(rows) * rh
    # year band
    for k in range(3):
        ax.add_patch(Rectangle((X(12 * k + 1), 10.98), X(12 * k + 13) - X(12 * k + 1), 0.36, fc=YEARS[k], ec='white',
                               lw=1.5))
        ax.text((X(12 * k + 1) + X(12 * k + 13)) / 2, 11.16, f'Year {k + 1}  ·  Months {12 * k + 1}–{12 * k + 12}',
                ha='center', va='center', fontsize=11, fontweight='bold', color=INK)
    # live operation (build_milestones.LIVE)
    la, lb = BM.LIVE
    ax.add_patch(Rectangle((X(la), ybot), X(lb + 1) - X(la), top - ybot, fc='#fcebd3', ec='none', zorder=0.2))
    # milestones on top, lines through the chart
    ymr = 10.68
    ax.text(X0 - 0.12, ymr, 'Milestones', ha='right', va='center', fontsize=11, fontweight='bold', color=GATE_TXT)
    for c in MS:
        g, m = c in GATES, MS[c]['month']
        xm = X(m + 1)
        ax.plot([xm, xm], [ybot, ymr - 0.12], color=GATE if g else '#9aa3ae', lw=1.6 if g else 1.0, ls='--', zorder=1)
        ax.plot([xm], [ymr], marker='D', ms=11, color=GATE if g else NAVY, mec=INK if g else 'white', mew=1.0, zorder=5)
        ax.text(xm - 0.15, ymr, c, ha='right', va='center', fontsize=10.4, fontweight='bold', color=GATE_TXT if g else NAVY)
    ypos = {}
    for i, (kind, code) in enumerate(rows):
        y1 = top - i * rh
        y0 = y1 - rh
        yc = (y0 + y1) / 2
        ypos[code] = yc
        if kind == 'wp':
            c = COL[code]
            a, b = WPD[code]['span']
            ax.add_patch(Rectangle((0.2, y0), X1 - 0.2, rh, fc='#eef1f5', ec='none', zorder=0.1))
            ax.add_patch(FancyBboxPatch((0.25, yc - 0.095), 0.58, 0.19, boxstyle='round,pad=0.01,rounding_size=0.05',
                                        fc=c, ec='none', zorder=2))
            ax.text(0.54, yc, code, ha='center', va='center', fontsize=9.8, color='white', fontweight='bold', zorder=3)
            ax.text(0.95, yc, BS.WPLAB[code], ha='left', va='center', fontsize=10.6, color=c, fontweight='bold')
            ax.text(X0 - 0.12, yc, f'{a}–{b}', ha='right', va='center', fontsize=10, color=c, fontweight='bold')
            ax.add_patch(Rectangle((X(a), yc - 0.035), X(b + 1) - X(a), 0.07, fc=c, ec='none', alpha=0.55, zorder=2))
        else:
            t = TASK[code]
            c = COL[t['wp']]
            crit = code in BS.CRIT
            ax.text(0.95, yc, code, ha='left', va='center', fontsize=10, color=c, fontweight='bold')
            ax.text(1.5, yc, SHORT[code], ha='left', va='center', fontsize=10, color=INK)
            ax.text(X0 - 0.12, yc, f'{t["a"]}–{t["b"]}', ha='right', va='center', fontsize=9.8, color=MUTED)
            ax.add_patch(FancyBboxPatch((X(t['a']) + 0.01, yc - 0.075), X(t['b'] + 1) - X(t['a']) - 0.02, 0.15,
                                        boxstyle='round,pad=0,rounding_size=0.04', fc=c, alpha=0.9,
                                        ec=RED if crit else 'none', lw=1.8 if crit else 0, zorder=3))
    # deliverables at the end of the task that produces them (build_schedule.DTASK)
    for d in deliverables():
        yc = ypos[BS.DTASK[d['code']]]
        for m in d['months']:
            xm = X(m + 1) - 0.05
            ax.plot([xm], [yc + 0.005], marker='v', ms=9, color=INK, mec='white', mew=0.9, zorder=6)
            right = m < 34
            ax.text(xm + (0.11 if right else -0.11), yc, d['code'], ha='left' if right else 'right', va='center',
                    fontsize=9.6, fontweight='bold', color=INK, zorder=7,
                    bbox=dict(boxstyle='round,pad=0.06', fc='white', ec='none', alpha=0.9))
    # month axis
    ax.plot([X(1), X(37)], [ybot, ybot], color=INK, lw=1.3)
    for m in (1, 6, 12, 18, 24, 30, 36):
        xm = (X(m) + X(m + 1)) / 2
        ax.plot([xm, xm], [ybot - 0.06, ybot], color=INK, lw=1.1)
        ax.text(xm, ybot - 0.09, str(m), ha='center', va='top', fontsize=10.4, color=INK)
    ax.text((X0 + X1) / 2, ybot - 0.36, 'Month of the project; a task "12–18" runs from the start of Month 12 to the end '
            'of Month 18', ha='center', va='top', fontsize=10.2, color=MUTED)
    ax.text(X0 - 0.12, ybot - 0.09, 'Months', ha='right', va='top', fontsize=10, color=MUTED, fontweight='bold')
    # legend, well above the banner
    yl = 1.38
    x = 0.3
    ax.plot([x + 0.09], [yl], marker='v', ms=10, color=INK)
    ax.text(x + 0.27, yl, 'deliverable (end of its month)', fontsize=10.4, va='center', color=INK)
    x += 0.27 + tw('deliverable (end of its month)', 10.4) + 0.42
    ax.plot([x + 0.09], [yl], marker='D', ms=10, color=NAVY, mec='white')
    ax.text(x + 0.27, yl, 'milestone', fontsize=10.4, va='center', color=INK)
    x += 0.27 + tw('milestone', 10.4) + 0.42
    ax.plot([x + 0.09], [yl], marker='D', ms=10, color=GATE, mec=INK, mew=1.0)
    lab = 'evidence gate (' + and_list(GATE_LIST) + ')'
    ax.text(x + 0.27, yl, lab, fontsize=10.4, va='center', color=INK)
    x += 0.27 + tw(lab, 10.4) + 0.42
    ax.add_patch(FancyBboxPatch((x, yl - 0.075), 0.45, 0.15, boxstyle='round,pad=0,rounding_size=0.04', fc=COL['WP4'],
                                ec=RED, lw=1.8))
    ax.text(x + 0.55, yl, 'task on the critical path', fontsize=10.4, va='center', color=INK)
    x += 0.55 + tw('task on the critical path', 10.4) + 0.42
    ax.add_patch(Rectangle((x, yl - 0.1), 0.45, 0.2, fc='#fcebd3', ec='none'))
    ax.text(x + 0.55, yl, f'live operation, Months {la}–{lb}', fontsize=10.4, va='center', color=INK)

    banner(ax, 'New: gates, not only dates: live operation starts only after the model passes its validation test (MS3) and '
               'the surrogate meets its error bound (MS4); back-testing runs alongside live operation, so twelve full '
               'months fit even after a two-month slip at MS4.', y0=0.2, h=0.88)
    return save(fig, ax, path)


# =========================================================================================================== main
FIGS = [('plan_fig1_structure.png', fig1_structure), ('plan_fig2_dissemination.png', fig2_dissemination),
        ('plan_fig3_team.png', fig3_team), ('plan_fig4_deliverables.png', fig4_deliverables),
        ('plan_fig5_gantt.png', fig5_gantt)]


def main(outdir, only=None):
    os.makedirs(outdir, exist_ok=True)
    out = []
    for name, fn in FIGS:
        if only and not any(o in name for o in only):
            continue
        path = os.path.join(outdir, name)
        problems = fn(path)
        print('saved', path, '|', 'no layout problems' if not problems else f'{len(problems)} layout problems')
        out.append(path)
    return out


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: python plan_figs.py OUTDIR')
    main(sys.argv[1], sys.argv[2:] or None)
