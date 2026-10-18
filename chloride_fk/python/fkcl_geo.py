"""Derived geographic inputs for the Fushe-Kuqe chloride study (run once; outputs are committed as CSV).

* shoreline per model row: for every 0.25 km row of the aquifer grid, the easternmost sea point west of the
  aquifer, from the GLOBE 1-km land mask (global-land-mask package). Gauss-Krueger zone 4 (Pulkovo 1942,
  EPSG:28404) <-> WGS84 with pyproj. Rows whose western aquifer edge lies within GAP_MAX of the sea are the
  rows in contact with the Adriatic.
* shoreline polyline (for maps) and reference place labels.

Local coordinates are km east/north of the south-west corner of the aquifer polygon (x0, y0), the same
origin as src/fushe_kuqe_field_design.m.
"""
import os
import numpy as np
import pandas as pd
from pyproj import Transformer
from global_land_mask import globe

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, '..', 'derived')
GAP_MAX = 5.0          # km; a western edge farther than this from the sea is an inland (hill) margin
DX = 0.25              # km, model grid

# reference places (WGS84 lat, lon), used only as map labels
PLACES = {'Lezhë': (41.7836, 19.6436), 'Laç': (41.6353, 19.7131), 'Milot': (41.6833, 19.7167),
          'Mamurras': (41.5775, 19.6922), 'Fushë-Krujë': (41.4783, 19.7178), 'Tirana': (41.3275, 19.8189),
          'Patok lagoon': (41.637, 19.580), 'Durrës': (41.3231, 19.4414)}


def xlsx_path():
    for f in (os.path.join(ROOT, 'data', 'Fushe_Kuqe_All_Data.xlsx'), os.path.join(ROOT, 'Fushe_Kuqe_All_Data.xlsx')):
        if os.path.exists(f):
            return f
    raise FileNotFoundError('Fushe_Kuqe_All_Data.xlsx')


def main():
    os.makedirs(OUT, exist_ok=True)
    B = pd.read_excel(xlsx_path(), sheet_name='3_Boundary_Coords').iloc[:, 1:3].to_numpy(float)
    B = B[np.all(np.isfinite(B), 1)]
    x0, y0 = B[:, 0].min(), B[:, 1].min()
    to_ll = Transformer.from_crs('EPSG:28404', 'EPSG:4326', always_xy=True)
    to_gk = Transformer.from_crs('EPSG:4326', 'EPSG:28404', always_xy=True)

    # fine land mask over the region (local km)
    xs = np.arange(-20.0, 24.0 + 1e-9, 0.1)
    ys = np.arange(-4.0, 60.0 + 1e-9, 0.1)
    GX, GY = np.meshgrid(xs, ys)
    lon, lat = to_ll.transform((x0 + 1000 * GX).ravel(), (y0 + 1000 * GY).ravel())
    land = globe.is_land(np.asarray(lat), np.asarray(lon)).reshape(GX.shape)

    # shoreline per model row: easternmost sea cell west of x = 22 km in that row
    rows_y = np.arange(0.0, B[:, 1].max() / 1000 - y0 / 1000 + DX + 1e-9, DX)
    rows_y = np.round(np.arange(0, (B[:, 1].max() - y0) / 1000 + DX + 1e-9, DX), 6)
    shore = np.full(len(rows_y), np.nan)
    for j, yr in enumerate(rows_y):
        jj = int(round((yr - ys[0]) / 0.1))
        sea = np.flatnonzero(~land[jj])
        if len(sea):
            shore[j] = xs[sea.max()]
    pd.DataFrame({'y_km': rows_y, 'shore_x_km': shore}).to_csv(os.path.join(OUT, 'shoreline_rows.csv'),
                                                                 index=False, float_format='%.3f')

    # shoreline polyline from the mask (marching squares via matplotlib)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    cs = plt.contour(GX, GY, land.astype(float), levels=[0.5])
    segs = []
    for k, path in enumerate(cs.allsegs[0]):
        if len(path) < 20:
            continue
        segs.append(np.column_stack([np.full(len(path), k), path]))
    plt.close('all')
    seg = np.vstack(segs)
    pd.DataFrame(seg, columns=['segment', 'x_km', 'y_km']).to_csv(os.path.join(OUT, 'shoreline_polyline.csv'),
                                                                  index=False, float_format='%.3f')

    # place labels
    rec = []
    for name, (la, lo) in PLACES.items():
        X, Y = to_gk.transform(lo, la)
        rec.append((name, X / 1000 - x0 / 1000, Y / 1000 - y0 / 1000))
    pd.DataFrame(rec, columns=['name', 'x_km', 'y_km']).to_csv(os.path.join(OUT, 'places.csv'), index=False,
                                                              float_format='%.3f')
    pd.DataFrame({'x0_m': [x0], 'y0_m': [y0]}).to_csv(os.path.join(OUT, 'origin.csv'), index=False, float_format='%.3f')
    print(f'origin x0={x0:.2f} y0={y0:.2f}; rows {len(rows_y)}; polyline points {len(seg)}')


if __name__ == '__main__':
    main()
