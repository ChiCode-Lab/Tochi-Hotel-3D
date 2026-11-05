#!/usr/bin/env python3
"""Export 3D geometry (plot coords, metres; z up from finished ground) for the Three.js model."""
import json, sys, os
os.chdir('/home/claude/hotel'); sys.path.insert(0, '/home/claude/hotel')
import plan as P

FFL = 0.45          # finished floor above ground (plinth)
CEIL = 3.0          # floor to ceiling / top of internal walls
PARA = 4.2          # top of parapet above FFL
OX, OY = P.FRONT, P.SIDE   # building local -> plot

# ---------- record openings ----------
OPN = []
def rec(kind, axis, a0, a1, c0, c1, z0, z1, double=False, slant=False):
    OPN.append(dict(kind=kind, axis=axis, a0=a0, a1=a1, c0=c0, c1=c1, z0=z0, z1=z1, double=double, slant=slant))

def win_z(w):
    return (1.8, 2.4) if w <= 0.65 else (0.9, 2.1)

P.window_h = lambda t, x0, x1, y0, y1, glass=True: rec('win', 'x', x0, x1, y0, y1, *win_z(x1 - x0))
P.window_v = lambda t, y0, y1, x0, x1: rec('win', 'y', y0, y1, x0, x1, *win_z(y1 - y0))
P.window_N = lambda t, x0, x1: rec('win', 'x', x0, x1, P.yN_in(x0), P.yN_out(x0), *win_z(x1 - x0), slant=True)
def dh(t, x0, x1, y0, y1, side, hinge="L", double=False, draw=True):
    rec('door', 'x', x0, x1, y0, y1, 0, 2.1 if (x1 - x0) > 0.75 or (y1 - y0) > 0.2 else 2.1, double)
def dv(t, y0, y1, x0, x1, side, hinge="B", double=False, draw=True):
    rec('door', 'y', y0, y1, x0, x1, 0, 2.1, double)
P.door_h, P.door_v = dh, dv
P.draw_openings(None)

# ---------- walls -> strips ----------
walls = []   # dict(axis, a0, a1, lo(a), hi(a), ext)
def strip_rect(x0, y0, x1, y1):
    if (x1 - x0) >= (y1 - y0):
        walls.append(dict(axis='x', a0=x0, a1=x1, lo=lambda a, v=y0: v, hi=lambda a, v=y1: v, t=y1 - y0))
    else:
        walls.append(dict(axis='y', a0=y0, a1=y1, lo=lambda a, v=x0: v, hi=lambda a, v=x1: v, t=x1 - x0))

for poly in P.wall_list():
    if len(poly) == 6:   # north external with slant
        strip_rect(0, P.yN_in0, P.XS, P.yN_out0)
        walls.append(dict(axis='x', a0=P.XS, a1=P.L, lo=P.yN_in, hi=P.yN_out, t=P.EXT))
        continue
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    strip_rect(min(xs), min(ys), max(xs), max(ys))
for wing, i, name, side in P.ROOMS:
    for poly in P.toilet_walls(wing, i, side):
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        strip_rect(min(xs), min(ys), max(xs), max(ys))

pieces = []   # [pts(4 x [x,y]), z0, z1, mat]
MAT = dict(body=0, parapet=1, coping=2, inner=3)
COURT_SPLIT = P.BLK_W[1]

def is_court_wall(w):
    return w['axis'] == 'x' and abs(w['t'] - P.EXT) < 1e-6 and (
        abs(w['lo'](0) - P.yS_court[0]) < 1e-6 or abs(w['lo'](0) - P.yN_court[0]) < 1e-6)

def quad(w, a0, a1, grow=0.0):
    if grow and w.get('t', 0) > 0.2:
        a0, a1 = a0 - grow, a1 + grow
    if w['axis'] == 'x':
        return [[a0, w['lo'](a0) - grow], [a1, w['lo'](a1) - grow], [a1, w['hi'](a1) + grow], [a0, w['hi'](a0) + grow]]
    return [[w['lo'](a0) - grow, a0], [w['hi'](a0) + grow, a0], [w['hi'](a1) + grow, a1], [w['lo'](a1) - grow, a1]]

for w in walls:
    ext = w['t'] > 0.2
    cuts = {w['a0'], w['a1']}
    if is_court_wall(w) and w['a0'] < COURT_SPLIT < w['a1']:
        cuts.add(COURT_SPLIT)
    mine = []
    for o in OPN:
        if o['axis'] != w['axis']:
            continue
        if o['a1'] <= w['a0'] + 1e-6 or o['a0'] >= w['a1'] - 1e-6:
            continue
        am = (o['a0'] + o['a1']) / 2
        cm = (o['c0'] + o['c1']) / 2
        if not (w['lo'](am) - 0.01 <= cm <= w['hi'](am) + 0.01):
            continue
        mine.append(o); cuts.add(max(o['a0'], w['a0'])); cuts.add(min(o['a1'], w['a1']))
    cuts = sorted(cuts)
    for k in range(len(cuts) - 1):
        a0, a1 = cuts[k], cuts[k + 1]
        if a1 - a0 < 1e-4:
            continue
        am = (a0 + a1) / 2
        top = CEIL
        holes = sorted([(o['z0'], o['z1']) for o in mine if o['a0'] - 1e-6 <= am <= o['a1'] + 1e-6])
        z = 0.0; spans = []
        for (h0, h1) in holes:
            if h0 > z: spans.append((z, h0))
            z = max(z, h1)
        if z < top: spans.append((z, top))
        q = quad(w, a0, a1)
        for (z0, z1) in spans:
            if top > CEIL + 0.01 and z1 > CEIL:
                if z0 < CEIL:
                    pieces.append([q, z0, CEIL, MAT['body']])
                pieces.append([q, max(z0, CEIL), z1, MAT['parapet']])
            else:
                pieces.append([q, z0, z1, MAT['body'] if ext else MAT['inner']])


def tp(pt):
    return [round(pt[0] + OX, 4), round(pt[1] + OY, 4)]

# ---------- cornice band (white "parapet" fascia) around external walls ----------
BAND = [(0.16, 3.00, 3.12), (0.10, 3.12, 3.78), (0.22, 3.78, 3.86), (0.38, 3.86, 3.95), (0.55, 3.95, 4.18)]
bands = []
for w in walls:
    if w['t'] < 0.2:
        continue
    a0, a1 = w['a0'], w['a1']
    if is_court_wall(w):
        a1 = min(a1, COURT_SPLIT)
    for g, z0, z1 in BAND:
        bands.append([[tp(p) for p in quad(w, a0, a1, g)], z0, z1])

# ---------- facade accent panels (brick cladding + sage window surrounds) ----------
panels = []
def slab_x(x0, x1, yface, outd, z0, z1, kind, th=0.025):
    pts = [(x0, yface(x0)), (x1, yface(x1)), (x1, yface(x1) + outd * th), (x0, yface(x0) + outd * th)]
    panels.append([[tp(p) for p in pts], z0, z1, kind])
def slab_y(y0, y1, xface, outd, z0, z1, kind, th=0.025):
    pts = [(xface, y0), (xface + outd * th, y0), (xface + outd * th, y1), (xface, y1)]
    panels.append([[tp(p) for p in pts], z0, z1, kind])
S_FACE = lambda x: 0.0
N_FACE = lambda x: P.yN_out(x)
for k in (2, 4, 6):
    c = P.b[k] + P.INT / 2
    slab_x(c - 0.8, c + 0.8, S_FACE, -1, -FFL + 0.05, CEIL, 'brick')
for k in (0, 2, 4, 6):
    c = P.b[k] + P.INT / 2
    slab_x(c - 0.8, c + 0.8, N_FACE, 1, -FFL + 0.05, CEIL, 'brick')
# front (west) faces
slab_y(P.yN_corr_wall[0] + 0.6, P.yN_in0 - 0.3, 0.0, -1, -FFL + 0.05, CEIL, 'brick')
slab_y(3.2, 5.4, 0.0, -1, -FFL + 0.05, CEIL, 'brick')
# sage surrounds around room windows on outer walls
for o in OPN:
    if o['kind'] != 'win' or (o['a1'] - o['a0']) < 1.4 or o['axis'] != 'x':
        continue
    cm = (o['c0'] + o['c1']) / 2
    if cm < 1.0:
        face, outd = S_FACE, -1
    elif cm > 16.0:
        face, outd = N_FACE, 1
    else:
        continue
    x0, x1, m = o['a0'], o['a1'], 0.32
    slab_x(x0 - m, x0, face, outd, 0.55, 2.5, 'sage')
    slab_x(x1, x1 + m, face, outd, 0.55, 2.5, 'sage')
    slab_x(x0, x1, face, outd, 0.55, o['z0'], 'sage')
    slab_x(x0, x1, face, outd, o['z1'], 2.5, 'sage')

# ---------- outside direction for openings (for bars / sills) ----------
def outside(o):
    if o['axis'] == 'x':
        cm = (o['c0'] + o['c1']) / 2
        if P.yS_court[0] - 0.01 <= cm <= P.yS_court[1] + 0.01: return 1
        if P.yN_court[0] - 0.01 <= cm <= P.yN_court[1] + 0.01: return -1
        return -1 if cm < 8.7 else 1
    cm = (o['c0'] + o['c1']) / 2
    return 1 if cm > 41 else -1

def tp(pt):
    return [round(pt[0] + OX, 4), round(pt[1] + OY, 4)]

out_pieces = [[[tp(p) for p in q], round(z0, 4), round(z1, 4), m] for q, z0, z1, m in pieces]
out_open = []
for o in OPN:
    thick = o['c1'] - o['c0']
    ext = thick > 0.2
    if o['slant']:
        am = (o['a0'] + o['a1']) / 2
        c0, c1 = P.yN_in(am), P.yN_out(am)
    else:
        c0, c1 = o['c0'], o['c1']
    if o['axis'] == 'x':
        a0, a1, c0, c1 = o['a0'] + OX, o['a1'] + OX, c0 + OY, c1 + OY
    else:
        a0, a1, c0, c1 = o['a0'] + OY, o['a1'] + OY, c0 + OX, c1 + OX
    out_open.append(dict(k=o['kind'], ax=o['axis'], a0=round(a0, 4), a1=round(a1, 4), c0=round(c0, 4), c1=round(c1, 4),
                         z0=o['z0'], z1=o['z1'], d=o['double'], ext=ext, out=outside(o),
                         sl=(-P.K if o['slant'] else 0)))

# ---------- furniture ----------
fur = []   # [type, pts or circle, z0, z1]
def add_box(kind, pts, z0, z1):
    fur.append([kind, [tp(p) for p in pts], z0, z1])
def add_cyl(kind, x, y, r, z0, z1):
    fur.append([kind, [round(x + OX, 3), round(y + OY, 3), r], z0, z1])

for wing, i, name, side in P.ROOMS:
    m = P.mapper(wing, i, side)
    mf = m
    if wing == 'N' and i == 6:
        e, sg = P.b[i], -1
        mf = lambda p, q: (e + sg * p, P.yN_in0 - q)
    R = lambda f, p0, q0, p1, q1: [f(p0, q0), f(p1, q0), f(p1, q1), f(p0, q1)]
    add_box('bed', R(mf, 3.0, 1.2, 4.95, 2.8), 0, 0.5)
    add_box('pillow', R(mf, 4.5, 1.3, 4.9, 2.7), 0.5, 0.62)
    add_box('headboard', R(mf, 4.92, 1.1, 5.0, 2.9), 0, 1.1)
    add_box('wood', R(mf, 4.55, 0.7, 5.0, 1.15), 0, 0.5)
    add_box('wood', R(mf, 4.55, 2.85, 5.0, 3.3), 0, 0.5)
    add_box('wood', R(mf, 2.3, 3.4, 3.5, 4.0), 0, 2.1)
    if not (wing == 'N' and i == 6):
        add_box('wood', R(mf, 2.05, 0, 3.05, 0.5), 0.72, 0.76)
    add_box('tray', R(m, 0, 0, 0.9, 0.9), 0, 0.08)
    add_box('white', R(m, 1.05, 0, 1.6, 0.42), 0.8, 0.9)
    wx, wy = m(0.35, 1.5)
    add_box('white', R(m, 0, 1.28, 0.2, 1.72), 0, 0.8)
    add_cyl('white', wx, wy, 0.2, 0, 0.42)

# lounge
x0, x1, y0, y1 = P.a[0], P.b[1], P.yS_in, P.yS_court[0]
add_box('bar', [(x1 - 1.9, y0 + 0.6), (x1 - 1.35, y0 + 0.6), (x1 - 1.35, y1 - 0.9), (x1 - 1.9, y1 - 0.9)], 0, 1.1)
add_box('wood', [(x1 - 0.5, y0 + 0.3), (x1, y0 + 0.3), (x1, y1 - 0.4), (x1 - 0.5, y1 - 0.4)], 0, 2.0)
for k in range(4):
    add_cyl('stool', x1 - 2.3, y0 + 0.95 + k * 0.62, 0.17, 0, 0.75)
import math
for (tx, ty) in [(1.6, 1.3), (1.6, 3.0), (1.6, 4.7), (3.9, 1.3), (3.9, 3.0), (6.0, 1.6), (6.0, 3.6)]:
    add_cyl('wood', tx, ty, 0.4, 0, 0.75)
    for ang in range(45, 360, 90):
        add_cyl('chair', tx + 0.68 * math.cos(math.radians(ang)), ty + 0.68 * math.sin(math.radians(ang)), 0.18, 0, 0.45)
# kitchen
k0, k1, yb = P.a[7], P.b[7], P.yN_corr_wall[1]
add_box('counter', [(k0, P.yN_in(k0)), (k1, P.yN_in(k1)), (k1, P.yN_in(k1) - 0.6), (k0, P.yN_in(k0) - 0.6)], 0, 0.9)
add_box('counter', [(k0, P.yN_in(k0) - 0.6), (k0 + 0.6, P.yN_in(k0) - 0.6), (k0 + 0.6, yb + 1.6), (k0, yb + 1.6)], 0, 0.9)
add_box('counter', [(k0 + 1.6, yb + 0.9), (k0 + 3.6, yb + 0.9), (k0 + 3.6, yb + 1.6), (k0 + 1.6, yb + 1.6)], 0, 0.9)
add_box('white', [(k1 - 0.75, yb + 0.05), (k1, yb + 0.05), (k1, yb + 0.8), (k1 - 0.75, yb + 0.8)], 0, 1.8)
# reception
add_box('bar', [(38.35, 6.25), (38.95, 6.25), (38.95, 8.7), (38.35, 8.7)], 0, 1.1)
for yy in (6.55, 7.25):
    add_cyl('chair', 37.85, yy, 0.22, 0, 0.45)
for k in range(3):
    r0 = P.BLK_IN[0]
    add_box('shelf', [(r0 + 0.1 + k * 1.15, P.STORE_Y[1] - 0.5), (r0 + 1.15 + k * 1.15, P.STORE_Y[1] - 0.5),
                      (r0 + 1.15 + k * 1.15, P.STORE_Y[1]), (r0 + 0.1 + k * 1.15, P.STORE_Y[1])], 0, 2.0)

# ---------- floors / roofs (building local -> plot) ----------
def T(pts): return [tp(p) for p in pts]
L = P.L
floor = dict(
    south=T([(0, 0), (L, 0), (L, P.yS_court[1]), (0, P.yS_court[1])]),
    north=T([(0, P.yN_court[0]), (L, P.yN_court[0]), (L, P.yN_out(L)), (P.XS, P.yN_out0), (0, P.yN_out0)]),
    east=T([(P.BLK_W[0], P.yS_court[1]), (L, P.yS_court[1]), (L, P.yN_court[0]), (P.BLK_W[0], P.yN_court[0])]),
)
roof = dict(
    s=dict(x0=P.EXT + OX, x1=L - P.EXT + OX, y0=P.EXT + OY, y1=P.yS_court[1] - 0.0 + OY),
    n=dict(x0=P.EXT + OX, x1=L - P.EXT + OX, y0=P.yN_court[0] + OY, xs=P.XS + OX, ye0=P.yN_in0 + OY,
           ye1=P.yN_in(L - P.EXT) + OY),
    e=dict(x0=P.BLK_W[0] + OX, x1=L - P.EXT + OX, y0=P.yS_court[1] + OY, y1=P.yN_court[0] + OY),
)
site = dict(PL=P.PLOT_L, PW=P.SIDE + P.D + P.SIDE, NARROW=P.NARROW, XSF=P.FRONT + P.XS, FFL=FFL, CEIL=CEIL, PARA=PARA,
            BX0=OX, BY0=OY, BL=P.L, BD=P.D, court=dict(x0=OX, x1=P.BLK_W[0] + OX, y0=P.yS_court[1] + OY, y1=P.yN_court[0] + OY),
            gate=[7.8, 12.3], ped=[12.45, 13.45],
            bays=[[1.8, 4.2], [4.2, 6.6], [6.6, 9.0], [11.0, 13.4], [13.4, 15.8], [15.8, 18.2]],
            gh=[0.2, 17.9, 4.2, 20.2], conv=[0.2, 0.2, 2.9, 2.1])
data = dict(bands=bands, panels=panels, pieces=out_pieces, openings=out_open, furniture=fur, floor=floor, roof=roof, site=site)
json.dump(data, open('/home/claude/hotel/model.json', 'w'), separators=(',', ':'))
print(len(out_pieces), 'pieces', len(out_open), 'openings', len(fur), 'furniture', os.path.getsize('/home/claude/hotel/model.json'), 'bytes')
