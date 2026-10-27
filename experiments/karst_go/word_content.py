"""Content of the karst diagram for its Word version (large type, OMML equations), in the format read by
../ml_paradigms/word/paradigms_word.js: header, innovation (written out in full, with equations) and the eight panels.
Writes word_karst/content.json and crops the section of karst_diagram.png to word_karst/hero.png, plus two
enlarged halves (hero_left.png, hero_right.png)."""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from karst_diagram import PANELS, HERO_Y0, HERO_Y1, W  # noqa: E402

COLOR = dict(sea='blue', drn='purple', top='green', riv='teal', clo='orange', well='amber', ic='pink', base='brown')

INNOV = dict(
    kicker='INNOVATION', name='The conduit network is assimilated',
    sub='Not only the parameters of a fixed network: an ensemble of possible conduit networks is weighted by the data, '
        'and every law in it is monotone in the head, so each update stays stable.',
    items=[
        dict(t='Assimilate the network itself',
             eqs=[r'p(\mathcal{N}\mid\mathcal{D})\propto p(\mathcal{D}\mid\mathcal{N})\,p(\mathcal{N}),\qquad '
                  r'\mathcal{N}=\big(V,\,E,\,\{D_e,\epsilon_e\}\big)'],
             x='Stochastic networks are generated from geology, fractures and base level and weighted by tracer tests, the '
               'spring hydrograph and its EC. Conduits not yet mapped stay in the ensemble until the data rule them out.',
             kv='', kc=''),
        dict(t='Monotone laws keep every update stable',
             eqs=[r'f(d)=\frac{C\,d}{\sqrt{|d|+\varepsilon}}',
                  r'\|\Delta h_n\|_S\le\|\Delta h_0\|_S+\sum_k\Delta t\,\|S^{-1}\Delta b_k\|_S,\qquad \|v\|_S^2=\sum_i S_i v_i^2'],
             x='Every pipe law, exchange and switching outlet is monotone in the head, so two runs never drift further apart '
               'than their forcings push them. Check on 30 random dual-continuum networks (25 conduit nodes, 25 matrix '
               'cells, implicit Euler with Newton): the largest ratio of the head difference to the bound is 0.3273.',
             kv='0.33', kc='OF THE BOUND (MUST BE ≤ 1)'),
        dict(t='The EC of a coastal spring observes the conduit head',
             eqs=[r'c_{\mathrm{spring}}=\frac{Q_{\mathrm{sea}}}{Q_{\mathrm{sea}}+Q_{\mathrm{fresh}}},\qquad '
                  r'Q_{\mathrm{sea}}=C_i\big(h_f^{\mathrm{sea}}(z_i)-h_c(z_i)\big)_+'],
             x='A brackish spring measures how far the conduit head at the sea inlet has fallen below the equivalent fresh '
               'head of the sea; a fresh spring says only that $h_c(z_i)\\ge h_f^{\\mathrm{sea}}(z_i)$, a censored '
               'observation.',
             kv='censored', kc='WHEN THE SPRING IS FRESH'),
    ],
    foot='The same assimilation as for a porous aquifer, with the network as one more unknown: the pipe laws, the exchange '
         'and the springs keep the update stable.')


def main():
    out = os.path.join(HERE, 'word_karst')
    os.makedirs(out, exist_ok=True)
    cards = [dict(t=title, color=COLOR[key], ideaPill='POROUS', idea=porous, eqs=list(tex), pill='IN THE MODEL', land=impact)
             for (n, key, title, porous, tex, impact) in PANELS]
    D = dict(name='karst_diagram', kicker='KARST AQUIFERS  ·  WHAT CHANGES IN THE MODEL',
             title='From a porous aquifer to a karst aquifer: how a coastal karst massif is modelled',
             tags=[['POROUS', 'one continuum · Darcy flow · diffuse recharge · a sea face'],
                   ['KARST', 'matrix + conduits · pipe flow · point recharge · springs and sea inlets']],
             hero_y1=HERO_Y1, innov=INNOV, cards=cards,
             zoom=[dict(png='hero_left.png', caption='The section enlarged (1 of 2): the sea, the springs and the seawater inlet'),
                   dict(png='hero_right.png', caption='The section enlarged (2 of 2): the massif, the epikarst, the polje and the conduits')])
    json.dump([D], open(os.path.join(out, 'content.json'), 'w'), ensure_ascii=False, indent=1)
    im = Image.open(os.path.join(HERE, 'karst_diagram.png'))
    s = im.size[0] / W
    im.crop((0, int(HERO_Y0 * s), im.size[0], int(HERO_Y1 * s))).save(os.path.join(out, 'hero.png'))
    for name, x0, x1 in (('hero_left.png', 0, 1250), ('hero_right.png', 1150, W)):      # two halves that overlap by 100 px
        im.crop((int(x0 * s), int(HERO_Y0 * s), int(x1 * s), int(HERO_Y1 * s))).save(os.path.join(out, name))
    print('wrote word_karst/content.json and word_karst/hero.png', len(cards), 'panels')


if __name__ == '__main__':
    main()
