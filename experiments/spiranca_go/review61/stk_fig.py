"""Involvement of stakeholders: seven groups, each with its role, why it is needed, its challenge and the tailored
response, and where it is engaged; the Stakeholder Advisory Panel; the public; what is new.
Content from the HALOMAR annex, sections 2.B, 2.C, 3.A and 3.B. Writes res/figK1_stakeholders.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED, NAVY, GREEN = '#1f2933', '#52606d', '#1f3864', '#1e8a5a'
plt.rcParams.update({'font.family': 'DejaVu Sans'})


def rbox(ax, x0, y0, w, h, fc, ec, lw=1.3, r=0.08, z=1):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle=f'round,pad=0.012,rounding_size={r}', fc=fc, ec=ec, lw=lw, zorder=z))


COLS = [(0.2, 2.2), (2.3, 5.15), (5.25, 8.0), (8.1, 12.6), (12.7, 14.4)]
HEAD = ['Stakeholder', 'Role in the Action', 'Why they are needed', 'Challenge  →  tailored engagement', 'Engaged in']

ROWS = [
    ('National\ngeological\nsurveys', '#c27c12', '#fff4e0',
     'WG members; source of the long\nrecords every method is\nbenchmarked against',
     'a survey holds the record: no\nresearch group has decades of\nhead, chloride and ion series',
     'staff time unpaid; some records cannot be published raw',
     'derived series and metadata only; one meeting a year;\nin return, a documented basis for their classification',
     'WG5 inventory\nD4, D5\nbenchmark'),
    ('Water agencies,\nriver basin\nauthorities', GREEN, '#e6f5ee',
     'co-authors of the status\nprotocol; the independent teams\nin the falsification test',
     'they make the classification: a\nprotocol they co-author needs\nno further decision',
     'act for administrative reasons, within the reporting cycle',
     'protocol work timed to the transposition timetable;\npolicy brief written in the form a basin plan absorbs',
     'WG1\nD7 protocol\nD10 brief'),
    ('Water utilities,\nwell-field\noperators', '#2e6db4', '#e8f1fb',
     'pumping records, constraints and\naccess; partners on learning\npumping rules from records',
     'only the operator knows how\npumping was decided; what is\nnot logged misleads models',
     'abstraction data are commercially, politically sensitive',
     'aggregated series if needed, the design cost stated;\nsharing terms agreed per contributor (Data Steward)',
     'WG4\nD6 guidance'),
    ('Recharge\nscheme\noperators', '#6a4fb3', '#f1ecfa',
     'hosts for missions and one\nTraining School; operational\nconstraints models lack',
     'recharge without an operating\nscheme is a proposal about\nmodels',
     'operating coastal schemes are few: the group cannot grow',
     'a light hosting role, with the analysis brought to them;\nrecruited at the 2028 recharge symposium',
     'WG3, D3\nSTSMs\nTraining School 2'),
    ('Consultancies,\nlabs, instrument\nmakers', '#52606d', '#eceff3',
     'Advisory Panel; WGs on siting\nand recharge; labs measure\nexchange capacity of sediments',
     'consultancies design most\nnetworks: the route by which a\nprotocol becomes routine',
     'they need a return within their own commercial horizon',
     'open, citable workflows they can use at once;\nearly access to the benchmark set',
     'WG2, WG3\nAdvisory Panel'),
    ('Research\ncommunity', '#0e7490', '#e3f4f7',
     'WG membership, benchmark teams\nand peer scrutiny, including\nmathematicians',
     'independent use of rival methods\nmakes the benchmark a test,\nnot a demonstration',
     'modelling, chemistry, geophysics, maths: separate venues',
     'joint mixed-authorship papers, in the venues of all;\nSWIM 2029 in Bari, ISMAR, Eurokarst, IAH Congress',
     'all WGs\nD5, D12'),
    ('Early-career\nresearchers', '#b03a3a', '#fdecec',
     'Training Schools, missions and\nleadership roles; often the ones\nwho run the benchmark',
     'they carry methods home and\nstay long after the Action ends',
     'the least-monitored countries have the fewest funded posts',
     'priority for mobility and Virtual Mobility Grants;\nall training material open: no need to travel',
     'Training Schools\nSTSMs; ≥ 1/3\nof WG leads'),
]


def main():
    W, H = 14.6, 11.0
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 10.74, 'Involvement of stakeholders: who, why, and a plan tailored to each', ha='center', va='center',
            fontsize=16, fontweight='bold', color=INK)

    # top band: participants not audience + Advisory Panel
    rbox(ax, 0.2, 9.58, 4.6, 0.82, NAVY, NAVY, lw=0)
    ax.text(2.5, 9.99, 'Participants, not an audience:\nthe central deliverables cannot\nbe produced without them',
            ha='center', va='center', fontsize=11.2, color='white', fontweight='bold', linespacing=1.12)
    rbox(ax, 4.95, 9.58, 9.45, 0.82, '#e6f5ee', GREEN, lw=1.6)
    ax.text(5.1, 10.3, 'Stakeholder Advisory Panel', fontsize=11.8, fontweight='bold', color=GREEN, va='top')
    ax.text(5.1, 10.03, 'drawn from all seven groups, utilities and private sector included; chaired by a member from a\n'
            'water authority or utility; reviews every deliverable in draft; meets the Management Committee yearly',
            fontsize=10.5, color=INK, va='top', linespacing=1.15)

    # header
    yh0, yh1 = 8.98, 9.44
    for (x0, x1), t in zip(COLS, HEAD):
        rbox(ax, x0, yh0, x1 - x0, yh1 - yh0, '#eceff3', '#9aa5b1', lw=1.0)
        ax.text((x0 + x1) / 2, (yh0 + yh1) / 2, t, ha='center', va='center', fontsize=11.5, fontweight='bold', color=INK)

    rh, gy, top = 1.0, 0.07, 8.9
    for r, (name, col, fill, role, why, chal, resp, where) in enumerate(ROWS):
        y0 = top - (r + 1) * rh - r * gy
        ym = y0 + rh / 2
        x0, x1 = COLS[0]
        rbox(ax, x0, y0, x1 - x0, rh, col, col, lw=0)
        ax.text((x0 + x1) / 2, ym, name, ha='center', va='center', fontsize=11, fontweight='bold', color='white', linespacing=1.08)
        for k, txt in ((1, role), (2, why)):
            cx0, cx1 = COLS[k]
            rbox(ax, cx0, y0, cx1 - cx0, rh, fill, col, lw=1.0)
            ax.text(cx0 + 0.1, ym, txt, ha='left', va='center', fontsize=10.4, color=INK, linespacing=1.12, zorder=3)
        cx0, cx1 = COLS[3]
        rbox(ax, cx0, y0, cx1 - cx0, rh, 'white', col, lw=1.0)
        ax.text(cx0 + 0.1, y0 + rh - 0.1, chal, ha='left', va='top', fontsize=10.4, color=MUTED, style='italic', zorder=3)
        ax.text(cx0 + 0.1, y0 + 0.36, '→', ha='left', va='center', fontsize=13, color=GREEN, fontweight='bold', zorder=3)
        ax.text(cx0 + 0.42, y0 + 0.36, resp, ha='left', va='center', fontsize=10.4, color=GREEN, linespacing=1.12, zorder=3)
        cx0, cx1 = COLS[4]
        rbox(ax, cx0, y0, cx1 - cx0, rh, fill, col, lw=1.0)
        ax.text((cx0 + cx1) / 2, ym, where, ha='center', va='center', fontsize=10.4, color=col, fontweight='bold', linespacing=1.12, zorder=3)

    # bottom: public + what is new
    yb0, yb1 = 0.2, 1.32
    rbox(ax, 0.2, yb0, 5.6, yb1 - yb0, '#fff4e0', '#c27c12', lw=1.4)
    ax.text(0.35, yb1 - 0.1, 'Public and water users', fontsize=11.6, fontweight='bold', color='#c27c12', va='top')
    ax.text(0.35, yb1 - 0.42, 'plain-language summaries of every deliverable, in\nnational languages; why a well is placed where it is;\nan annual open web seminar with the Advisory Panel',
            fontsize=10.4, color=INK, va='top', linespacing=1.12)
    rbox(ax, 5.95, yb0, W - 0.2 - 5.95, yb1 - yb0, NAVY, NAVY, lw=0)
    ax.text(6.1, yb1 - 0.1, 'New: engagement is built into the deliverables', fontsize=11.6, fontweight='bold', color='white', va='top')
    ax.text(6.1, yb1 - 0.42, 'two authorities are the falsification test; utilities\' records are the test of how many years\n'
            'a pumping rule needs; the theorem on misleading records makes what operators log a scientific\n'
            'question; record holders keep ownership and only derived series are published',
            fontsize=10.4, color='white', va='top', linespacing=1.12)
    fig.savefig(os.path.join(OUT, 'figK1_stakeholders.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
