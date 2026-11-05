#!/usr/bin/env python3
"""Ground floor plan + site plan for proposed Tochi Hotel. Units: metres (world), mm (paper)."""
import math

# ---------------- GEOMETRY (building local, origin = SW outer corner) ----------------
EXT, INT, TP = 0.225, 0.15, 0.10
BAY, NB = 5.0, 8
L = EXT + NB * BAY + (NB - 1) * INT + EXT          # 41.5
a = [EXT + i * (BAY + INT) for i in range(NB)]       # bay clear start (index 0..7)
b = [x + BAY for x in a]                              # bay clear end
cen = [x + BAY / 2 for x in a]

# Y levels
yS_in = EXT                     # south rooms inner face (outer wall inner)
yS_corr_wall = (4.225, 4.375)
yS_court = (5.575, 5.8)
yN_court = (11.3, 11.525)
yN_corr_wall = (13.025, 13.175)
yN_in0, yN_out0 = 17.175, 17.4
D = 17.4

# slanted north wall (fence narrows toward rear)
XS = b[5] + INT / 2              # kink at Rm8/Rm7 partition centre (31.05)
FRONT, REAR, SIDE = 10.0, 10.0, 1.5
PLOT_L = FRONT + L + REAR        # 61.5
NARROW = 2.0
K = NARROW / (FRONT + L + REAR - (FRONT + XS))

def yN_out(x): return yN_out0 - K * max(0.0, x - XS)
def yN_in(x): return yN_out(x) - EXT

# reception block
BLK_W = (36.2, 36.425)
BLK_IN = (36.425, 39.925)
BLK_E = (39.925, 40.075)
REAR_CORR = (40.075, L - EXT)
REC_Y = (yS_court[1], 9.15)
REC_PART = (9.15, 9.3)
STORE_Y = (9.3, yN_court[0])

# ---------------- SVG helpers ----------------
out = []
def E(s): out.append(s)
def f(v): return f"{v:.3f}"

class T:
    def __init__(s, ox, oy, sc, dx=0.0, dy=0.0):
        s.ox, s.oy, s.sc, s.dx, s.dy = ox, oy, sc, dx, dy
    def __call__(s, x, y):
        return (s.ox + (x + s.dx) * s.sc, s.oy - (y + s.dy) * s.sc)

def poly(t, pts, fill="none", stroke="#000", sw=0.18, extra=""):
    p = " ".join(f"{f(X)},{f(Y)}" for X, Y in (t(*q) for q in pts))
    E(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

def rect(t, x0, y0, x1, y1, **k):
    poly(t, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **k)

def line(t, x0, y0, x1, y1, sw=0.18, stroke="#000", extra=""):
    X0, Y0 = t(x0, y0); X1, Y1 = t(x1, y1)
    E(f'<line x1="{f(X0)}" y1="{f(Y0)}" x2="{f(X1)}" y2="{f(Y1)}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

def text(X, Y, s, size=2.5, anchor="middle", weight="normal", fill="#000", rot=0, style=""):
    s = s.replace("&amp;", "&").replace("&", "&amp;")
    tr = f' transform="rotate({rot} {f(X)} {f(Y)})"' if rot else ""
    E(f'<text x="{f(X)}" y="{f(Y)}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}" style="{style}"{tr}>{s}</text>')

def wtext(t, x, y, s, **k):
    X, Y = t(x, y); text(X, Y, s, **k)

def circle(t, x, y, r, fill="none", sw=0.13, stroke="#000"):
    X, Y = t(x, y)
    E(f'<circle cx="{f(X)}" cy="{f(Y)}" r="{f(r * t.sc)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def ellipse(t, x, y, rx, ry, sw=0.13):
    X, Y = t(x, y)
    E(f'<ellipse cx="{f(X)}" cy="{f(Y)}" rx="{f(rx * t.sc)}" ry="{f(ry * t.sc)}" fill="#fff" stroke="#000" stroke-width="{sw}"/>')

WALL = "#262626"

# ---------------- BUILDING DRAWING ----------------
def wall_list():
    W = []
    R = lambda x0, y0, x1, y1: W.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    # south external
    R(0, 0, L, EXT)
    # west external (two segments; courtyard open between)
    R(0, 0, EXT, yS_court[1]); R(0, yN_court[0], EXT, yN_out0)
    # east external
    W.append([(L - EXT, 0), (L, 0), (L, yN_out(L)), (L - EXT, yN_out(L - EXT))])
    # north external with slant
    W.append([(0, yN_in0), (XS, yN_in0), (L, yN_in(L)), (L, yN_out(L)), (XS, yN_out0), (0, yN_out0)])
    # corridor/room walls
    R(b[1] + INT, yS_corr_wall[0], L - EXT, yS_corr_wall[1])
    # wall closing south corridor from lounge (lounge has no corridor)
    R(b[1], yS_corr_wall[0], b[1] + INT, yS_court[0])
    R(EXT, yN_corr_wall[0], L - EXT, yN_corr_wall[1])
    # courtyard walls
    R(0, yS_court[0], REAR_CORR[0], yS_court[1])
    R(0, yN_court[0], REAR_CORR[0], yN_court[1])
    # reception block
    R(BLK_W[0], yS_court[1], BLK_W[1], yN_court[0])
    R(BLK_E[0], yS_court[1], BLK_E[1], yN_court[0])
    R(BLK_IN[0], REC_PART[0], BLK_IN[1], REC_PART[1])
    # south wing partitions (no partition between bay1 & bay2 = lounge)
    for i in range(1, NB - 1):
        R(b[i], EXT, b[i] + INT, yS_corr_wall[0])
    # north wing partitions
    for i in range(NB - 1):
        x0, x1 = b[i], b[i] + INT
        W.append([(x0, yN_corr_wall[1]), (x1, yN_corr_wall[1]), (x1, yN_in(x1)), (x0, yN_in(x0))])
    return W

# room definitions: (wing, bay index, name, toilet side)
S_ROOMS = [("S", 2, "ROOM 1", "E"), ("S", 3, "ROOM 2", "W"), ("S", 4, "ROOM 3", "E"),
           ("S", 5, "ROOM 4", "W"), ("S", 6, "ROOM 5", "E"), ("S", 7, "ROOM 6", "W")]
N_ROOMS = [("N", 0, "ROOM 13", "E"), ("N", 1, "ROOM 12", "W"), ("N", 2, "ROOM 11", "E"),
           ("N", 3, "ROOM 10", "W"), ("N", 4, "ROOM 9", "E"), ("N", 5, "ROOM 8", "W"),
           ("N", 6, "ROOM 7", "E")]
ROOMS = S_ROOMS + N_ROOMS
TW, TD = 1.8, 2.1   # en-suite clear size

def mapper(wing, i, side):
    """(p,q) -> world. p from toilet-side partition along bay, q from outer wall inward."""
    edge, sg = (b[i], -1) if side == "E" else (a[i], 1)
    def m(p, q):
        x = edge + sg * p
        if wing == "S":
            return (x, yS_in + q)
        return (x, yN_in(x) - q)
    return m

def toilet_walls(wing, i, side):
    m = mapper(wing, i, side)
    W = []
    # side wall (p = TW .. TW+TP), from outer to q = TD + TP
    if wing == "S":
        q_bot = TD
    else:
        # keep a uniform corridor-side line; deepest point sets it
        q_bot = TD
    if wing == "N" and i == 6:  # Room 7 slanted: set bottom line by outer face at free side
        pass
    pts_side = [m(TW, 0), m(TW + TP, 0), m(TW + TP, q_bot + TP), m(TW, q_bot + TP)]
    W.append(pts_side)
    # front wall q = TD .. TD+TP from p=0 to TW+TP
    # for N wing, define front wall at a constant y (horizontal)
    if wing == "S":
        y0 = yS_in + TD; W.append([(m(0, 0)[0], y0), (m(TW + TP, 0)[0], y0), (m(TW + TP, 0)[0], y0 + TP), (m(0, 0)[0], y0 + TP)])
    else:
        xA, xB = m(0, 0)[0], m(TW + TP, 0)[0]
        ytop = min(yN_in(xA), yN_in(xB))
        y0 = ytop - TD
        y0 = min(y0, yN_in0 - TD)
        W.append([(xA, y0), (xB, y0), (xB, y0 - TP), (xA, y0 - TP)])
        # fix side wall to reach front wall
        W[0] = [(m(TW, 0)[0], yN_in(m(TW, 0)[0])), (m(TW + TP, 0)[0], yN_in(m(TW + TP, 0)[0])),
                (m(TW + TP, 0)[0], y0 - TP), (m(TW, 0)[0], y0 - TP)]
    return W

def toilet_front_y(wing, i, side):
    if wing == "S":
        return yS_in + TD
    m = mapper(wing, i, side)
    xA, xB = m(0, 0)[0], m(TW + TP, 0)[0]
    y0 = min(yN_in(xA), yN_in(xB)) - TD
    return min(y0, yN_in0 - TD)

def draw_walls(t):
    for w in wall_list():
        poly(t, w, fill=WALL, stroke=WALL, sw=0.05)
    for wing, i, name, side in ROOMS:
        for w in toilet_walls(wing, i, side):
            poly(t, w, fill=WALL, stroke=WALL, sw=0.05)

# ---- openings ----
def cut(t, pts):
    poly(t, pts, fill="#fff", stroke="none", sw=0)

def window_h(t, x0, x1, y0, y1, glass=True):
    cut(t, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    sw = 0.15 if t.sc > 6 else 0.1
    line(t, x0, y0, x1, y0, sw); line(t, x0, y1, x1, y1, sw)
    line(t, x0, y0, x0, y1, sw); line(t, x1, y0, x1, y1, sw)
    ym = (y0 + y1) / 2
    line(t, x0, ym, x1, ym, sw)

def window_v(t, y0, y1, x0, x1):
    cut(t, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    sw = 0.15 if t.sc > 6 else 0.1
    line(t, x0, y0, x1, y0, sw); line(t, x0, y1, x1, y1, sw)
    line(t, x0, y0, x0, y1, sw); line(t, x1, y0, x1, y1, sw)
    xm = (x0 + x1) / 2
    line(t, xm, y0, xm, y1, sw)

def window_N(t, x0, x1):
    pts = [(x0, yN_in(x0)), (x1, yN_in(x1)), (x1, yN_out(x1)), (x0, yN_out(x0))]
    cut(t, pts)
    sw = 0.15 if t.sc > 6 else 0.1
    for (p, q) in [(pts[0], pts[1]), (pts[3], pts[2]), (pts[0], pts[3]), (pts[1], pts[2])]:
        line(t, *p, *q, sw)
    line(t, x0, (pts[0][1] + pts[3][1]) / 2, x1, (pts[1][1] + pts[2][1]) / 2, sw)

def arc_door(t, hinge, jamb, sdir, w, draw=True):
    """hinge, jamb: world points on swing-side wall face; sdir: unit vector of swing side."""
    if not draw:
        return
    tip = (hinge[0] + sdir[0] * w, hinge[1] + sdir[1] * w)
    line(t, *hinge, *tip, sw=0.25 if t.sc > 6 else 0.12)
    H = t(*hinge); P = t(*tip); J = t(*jamb)
    vx, vy = P[0] - H[0], P[1] - H[1]; jx, jy = J[0] - H[0], J[1] - H[1]
    sweep = 1 if (vx * jy - vy * jx) > 0 else 0
    r = w * t.sc
    E(f'<path d="M {f(P[0])} {f(P[1])} A {f(r)} {f(r)} 0 0 {sweep} {f(J[0])} {f(J[1])}" fill="none" stroke="#000" stroke-width="{0.12 if t.sc > 6 else 0.08}" stroke-dasharray="{"0.8,0.5" if t.sc > 6 else "none"}"/>')

def door_h(t, x0, x1, y0, y1, side, hinge="L", double=False, draw=True):
    """opening in horizontal wall (y0..y1). side=+1 swings toward +y (from face y1), -1 toward -y (face y0)."""
    cut(t, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    sw = 0.15 if t.sc > 6 else 0.08
    line(t, x0, y0, x0, y1, sw); line(t, x1, y0, x1, y1, sw)
    yf = y1 if side > 0 else y0
    if double:
        h = (x1 - x0) / 2
        arc_door(t, (x0, yf), (x0 + h, yf), (0, side), h, draw)
        arc_door(t, (x1, yf), (x1 - h, yf), (0, side), h, draw)
    else:
        w = x1 - x0
        if hinge == "L":
            arc_door(t, (x0, yf), (x1, yf), (0, side), w, draw)
        else:
            arc_door(t, (x1, yf), (x0, yf), (0, side), w, draw)

def door_v(t, y0, y1, x0, x1, side, hinge="B", double=False, draw=True):
    cut(t, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    sw = 0.15 if t.sc > 6 else 0.08
    line(t, x0, y0, x1, y0, sw); line(t, x0, y1, x1, y1, sw)
    xf = x1 if side > 0 else x0
    if double:
        h = (y1 - y0) / 2
        arc_door(t, (xf, y0), (xf, y0 + h), (side, 0), h, draw)
        arc_door(t, (xf, y1), (xf, y1 - h), (side, 0), h, draw)
    else:
        w = y1 - y0
        if hinge == "B":
            arc_door(t, (xf, y0), (xf, y1), (side, 0), w, draw)
        else:
            arc_door(t, (xf, y1), (xf, y0), (side, 0), w, draw)

def draw_openings(t, doors=True):
    c0, c1 = yS_court; n0, n1 = yN_court
    # --- Courtyard walls: corridor windows W2 + doors D1
    for i in [0, 2, 3, 4, 5]:
        window_h(t, cen[i] - 0.6, cen[i] + 0.6, c0, c1)
    for i in [0, 1, 2, 3, 4, 5]:
        window_h(t, cen[i] - 0.6, cen[i] + 0.6, n0, n1)
    door_h(t, cen[1] - 0.6, cen[1] + 0.6, c0, c1, +1, double=True, draw=doors)      # S corr <-> courtyard (near lounge)
    door_h(t, cen[6] - 0.6, cen[6] + 0.6, c0, c1, +1, double=True, draw=doors)      # S corr <-> courtyard (near reception)
    door_h(t, cen[6] - 0.6, cen[6] + 0.6, n0, n1, -1, double=True, draw=doors)      # N corr <-> courtyard
    # --- West (front) wall
    door_v(t, 1.6, 2.8, 0, EXT, +1, double=True, draw=doors)                         # lounge front door (in)
    # --- Lounge windows (south wall)
    for x0 in [1.4, 4.55, 7.7]:
        window_h(t, x0, x0 + 1.5, 0, EXT)
    # lounge door from corridor
    # --- Guest rooms
    for wing, i, name, side in ROOMS:
        m = mapper(wing, i, side)
        sg = -1 if side == "E" else 1
        def xr(p): return m(p, 0)[0]
        # room window W1 (outer wall), toilet window W3
        for (p0, p1) in [(2.6, 4.1), (1.05, 1.65)]:
            xa, xb = sorted([xr(p0), xr(p1)])
            if wing == "S":
                window_h(t, xa, xb, 0, EXT)
            else:
                window_N(t, xa, xb)
        # room entrance D3 on corridor wall, hinge near partition
        xa, xb = sorted([xr(0.3), xr(1.2)])
        hinge = "L" if side == "W" else "R"
        if wing == "S":
            door_h(t, xa, xb, *yS_corr_wall, -1, hinge=hinge, draw=doors)
        else:
            door_h(t, xa, xb, *yN_corr_wall, +1, hinge=hinge, draw=doors)
        # toilet door D4 (swing into toilet), hinge at free side (p=1.7)
        xa, xb = sorted([xr(1.0), xr(1.7)])
        hinge_t = "R" if side == "W" else "L"
        yf = toilet_front_y(wing, i, side)
        if wing == "S":
            door_h(t, xa, xb, yf, yf + TP, -1, hinge=hinge_t, draw=doors)
        else:
            door_h(t, xa, xb, yf - TP, yf, +1, hinge=hinge_t, draw=doors)
    # --- Kitchen (N bay 8)
    door_h(t, a[7] + 0.4, a[7] + 1.3, *yN_corr_wall, +1, hinge="L", draw=doors)
    window_N(t, a[7] + 0.75, a[7] + 1.95)
    window_N(t, a[7] + 3.0, a[7] + 4.2)
    door_v(t, 13.45, 14.35, L - EXT, L, +1, hinge="B", draw=doors)                    # kitchen back door (out)
    # --- East wall: corridor-end windows + rear exit
    window_v(t, 4.475, 5.475, L - EXT, L)
    window_v(t, 11.675, 12.875, L - EXT, L)
    door_v(t, 7.0, 8.0, L - EXT, L, +1, hinge="B", draw=doors)                        # rear exit (out)
    window_v(t, 9.3, 10.5, L - EXT, L)
    window_v(t, 2.4, 3.6, L - EXT, L)                                                  # Room 6 side window
    # --- Reception block
    door_v(t, 6.6, 7.8, *BLK_W, +1, double=True, draw=doors)                          # reception entrance (in)
    window_v(t, 8.0, 8.9, *BLK_W)                                                      # reception window
    window_v(t, 10.0, 10.6, *BLK_W)                                                    # store high window
    door_h(t, 38.95, 39.85, *REC_PART, +1, hinge="R", draw=doors)                     # store door from reception

def wc(t, x, y, facing):
    """WC: x,y = centre of cistern back on wall; facing unit vector."""
    fx, fy = facing; px, py = -fy, fx
    c = [(x + px * 0.25, y + py * 0.25), (x - px * 0.25, y - py * 0.25),
         (x - px * 0.25 + fx * 0.2, y - py * 0.25 + fy * 0.2), (x + px * 0.25 + fx * 0.2, y + py * 0.25 + fy * 0.2)]
    poly(t, c, fill="#fff", sw=0.13)
    cx, cy = x + fx * 0.45, y + fy * 0.45
    X, Y = t(cx, cy)
    rx = 0.25 * t.sc if abs(fx) > 0 else 0.19 * t.sc
    ry = 0.19 * t.sc if abs(fx) > 0 else 0.25 * t.sc
    E(f'<ellipse cx="{f(X)}" cy="{f(Y)}" rx="{f(rx)}" ry="{f(ry)}" fill="#fff" stroke="#000" stroke-width="0.13"/>')

def draw_fixtures(t):
    fs = "#555"
    for wing, i, name, side in ROOMS:
        m = mapper(wing, i, side)
        sg = -1 if side == "E" else 1
        qd = 1 if wing == "S" else -1
        # shower tray 900x900 at outer/partition corner
        poly(t, [m(0, 0), m(0.9, 0), m(0.9, 0.9), m(0, 0.9)], fill="#fff", sw=0.13)
        line(t, *m(0, 0), *m(0.9, 0.9), sw=0.08, stroke=fs); line(t, *m(0.9, 0), *m(0, 0.9), sw=0.08, stroke=fs)
        circle(t, *m(0.45, 0.45), 0.05, sw=0.1)
        # WC on partition wall facing +p
        wx, wy = m(0, 1.5)
        wc(t, wx, wy, (sg, 0))
        # basin on outer wall
        poly(t, [m(1.05, 0), m(1.6, 0), m(1.6, 0.42), m(1.05, 0.42)], fill="#fff", sw=0.13)
        bx, by = m(1.325, 0.22); ellipse(t, bx, by, 0.2, 0.13, sw=0.1)
        if wing == "N" and i == 6:
            _m = m
            edge_, sg_ = (b[i], -1)
            m = lambda p, q: (edge_ + sg_ * p, yN_in0 - q)
        # double bed 1600 x 2000, headboard on far partition
        poly(t, [m(3.0, 1.2), m(5.0, 1.2), m(5.0, 2.8), m(3.0, 2.8)], stroke=fs, sw=0.13)
        poly(t, [m(4.5, 1.35), m(4.9, 1.35), m(4.9, 1.95), m(4.5, 1.95)], stroke=fs, sw=0.1)
        poly(t, [m(4.5, 2.05), m(4.9, 2.05), m(4.9, 2.65), m(4.5, 2.65)], stroke=fs, sw=0.1)
        line(t, *m(3.0, 1.2), *m(3.6, 2.8), sw=0.08, stroke=fs)
        # bedside tables
        poly(t, [m(4.55, 0.7), m(5.0, 0.7), m(5.0, 1.15), m(4.55, 1.15)], stroke=fs, sw=0.1)
        poly(t, [m(4.55, 2.85), m(5.0, 2.85), m(5.0, 3.3), m(4.55, 3.3)], stroke=fs, sw=0.1)
        # wardrobe on corridor wall
        poly(t, [m(2.3, 3.4), m(3.5, 3.4), m(3.5, 4.0), m(2.3, 4.0)], stroke=fs, sw=0.12)
        line(t, *m(2.3, 3.4), *m(3.5, 4.0), sw=0.07, stroke=fs); line(t, *m(3.5, 3.4), *m(2.3, 4.0), sw=0.07, stroke=fs)
        # desk + chair on outer wall
        if not (wing == "N" and i == 6):
            poly(t, [m(2.05, 0), m(3.05, 0), m(3.05, 0.5), m(2.05, 0.5)], stroke=fs, sw=0.1)
            cx, cy = m(2.55, 0.75); circle(t, cx, cy, 0.18, sw=0.08, stroke=fs)
        # labels
        lx, ly = m(3.0, 3.35 if True else 0)
        X, Y = t(*m(2.6, 1.85 if wing == "S" else 1.85))
        cxw = (a[i] + b[i]) / 2
        yc = (yS_in + yS_corr_wall[0]) / 2 if wing == "S" else (yN_corr_wall[1] + yN_in(cxw)) / 2
        # place text on the free (non-bed) zone near toilet front
        tx, ty = m(1.0, 2.75) if not (wing == "N" and i == 6) else m(2.45, 3.0)
        X, Y = t(tx, ty)
        text(X, Y - 0.6, name, size=2.4, weight="bold")
        if i == 6 and wing == "N":
            ar = room_area(wing, i)
            text(X, Y + 2.4, f"{ar:.1f} m²", size=1.7)
        else:
            text(X, Y + 2.4, "20.0 m²", size=1.7)
        ex, ey = t(*m(0.9, 1.25))
        text(ex, ey + 0.6, "EN-SUITE", size=1.3, fill="#333")

def room_area(wing, i):
    if wing == "S":
        return BAY * (yS_corr_wall[0] - yS_in)
    xm = (a[i] + b[i]) / 2
    return BAY * (yN_in(xm) - yN_corr_wall[1])

def draw_lounge_kitchen_reception(t):
    fs = "#555"
    # ---- Lounge / bar (S bays 1-2)
    x0, x1 = a[0], b[1]; y0, y1 = yS_in, yS_court[0]
    # back bar on east wall
    poly(t, [(x1 - 0.5, y0 + 0.3), (x1, y0 + 0.3), (x1, y1 - 0.4), (x1 - 0.5, y1 - 0.4)], stroke=fs, sw=0.12)
    # counter
    poly(t, [(x1 - 1.9, y0 + 0.6), (x1 - 1.35, y0 + 0.6), (x1 - 1.35, y1 - 0.9), (x1 - 1.9, y1 - 0.9)], fill="#eee", stroke="#000", sw=0.15)
    for k in range(4):
        circle(t, x1 - 2.3, y0 + 0.95 + k * 0.62, 0.17, sw=0.1, stroke=fs)
    # tables
    for (tx, ty) in [(1.6, 1.3), (1.6, 3.0), (1.6, 4.7), (3.9, 1.3), (3.9, 3.0), (6.0, 1.6), (6.0, 3.6)]:
        circle(t, tx, ty, 0.4, sw=0.12, stroke=fs)
        for ang in range(0, 360, 90):
            r = 0.68
            circle(t, tx + r * math.cos(math.radians(ang + 45)), ty + r * math.sin(math.radians(ang + 45)), 0.16, sw=0.08, stroke=fs)
    X, Y = t(3.9 + 0.0, 4.75)
    text(X, Y, "LOUNGE / BAR", size=2.6, weight="bold")
    text(X, Y + 2.3, f"{(x1 - x0) * (y1 - y0):.1f} m²", size=1.7)
    wtext(t, x1 - 0.9, y0 + 0.15, "BAR", size=1.5, fill="#333")

    # ---- Kitchen (N bay 8)
    k0, k1 = a[7], b[7]
    yb = yN_corr_wall[1]
    # worktop along slanted north wall
    poly(t, [(k0, yN_in(k0)), (k1, yN_in(k1)), (k1, yN_in(k1) - 0.6), (k0, yN_in(k0) - 0.6)], stroke=fs, sw=0.12)
    # worktop along west partition
    poly(t, [(k0, yN_in(k0) - 0.6), (k0 + 0.6, yN_in(k0 + 0.6) - 0.6), (k0 + 0.6, yb + 1.6), (k0, yb + 1.6)], stroke=fs, sw=0.12)
    # sink under first window
    sx = k0 + 1.35
    poly(t, [(sx - 0.45, yN_in(sx) - 0.08), (sx + 0.45, yN_in(sx) - 0.08), (sx + 0.45, yN_in(sx) - 0.52), (sx - 0.45, yN_in(sx) - 0.52)], stroke="#000", sw=0.12)
    ellipse(t, sx - 0.2, yN_in(sx) - 0.3, 0.16, 0.13, sw=0.08); ellipse(t, sx + 0.2, yN_in(sx) - 0.3, 0.16, 0.13, sw=0.08)
    # cooker
    cx = k0 + 2.6
    poly(t, [(cx - 0.3, yN_in(cx) - 0.02), (cx + 0.3, yN_in(cx) - 0.02), (cx + 0.3, yN_in(cx) - 0.6), (cx - 0.3, yN_in(cx) - 0.6)], stroke="#000", sw=0.12)
    for dx in (-0.14, 0.14):
        for dy in (-0.17, -0.43):
            circle(t, cx + dx, yN_in(cx) + dy, 0.08, sw=0.07)
    # prep table
    poly(t, [(k0 + 1.6, yb + 0.9), (k0 + 3.6, yb + 0.9), (k0 + 3.6, yb + 1.6), (k0 + 1.6, yb + 1.6)], stroke=fs, sw=0.12)
    # fridge
    poly(t, [(k1 - 0.75, yb + 0.05), (k1, yb + 0.05), (k1, yb + 0.8), (k1 - 0.75, yb + 0.8)], stroke=fs, sw=0.12)
    wtext(t, k1 - 0.37, yb + 0.35, "FR", size=1.3, fill="#333")
    ka = BAY * (yN_in((k0 + k1) / 2) - yb)
    X, Y = t((k0 + k1) / 2 + 0.6, yb + 1.25)
    text(X, Y - 2.2, "KITCHEN", size=2.4, weight="bold")
    text(X + 6, Y + 1.0, f"{ka:.1f} m²", size=1.7)

    # ---- Reception + store
    r0, r1 = BLK_IN
    poly(t, [(38.35, 6.25), (38.95, 6.25), (38.95, 8.7), (38.35, 8.7)], fill="#eee", stroke="#000", sw=0.15)
    circle(t, 39.4, 7.4, 0.2, sw=0.1, stroke=fs)
    for yy in (6.55, 7.25):
        circle(t, 37.85, yy, 0.22, sw=0.1, stroke=fs)
    X, Y = t((r0 + 38.3) / 2 + 0.05, 8.55)
    text(X, Y - 1.0, "RECEPTION", size=2.1, weight="bold", rot=0)
    text(X, Y + 1.4, f"{(r1 - r0) * (REC_Y[1] - REC_Y[0]):.1f} m²", size=1.6)
    for k in range(3):
        poly(t, [(r0 + 0.1 + k * 1.15, STORE_Y[1] - 0.5), (r0 + 1.15 + k * 1.15, STORE_Y[1] - 0.5), (r0 + 1.15 + k * 1.15, STORE_Y[1]), (r0 + 0.1 + k * 1.15, STORE_Y[1])], stroke=fs, sw=0.1)
    X, Y = t((r0 + r1) / 2, 10.1)
    text(X, Y, "STORE", size=2.1, weight="bold")
    text(X, Y + 2.2, f"{(r1 - r0) * (STORE_Y[1] - STORE_Y[0]):.1f} m²", size=1.6)

    # ---- Corridors & courtyard labels
    wtext(t, 22.0, (yS_corr_wall[1] + yS_court[0]) / 2 - 0.12, "CORRIDOR (1200 WIDE)", size=1.9, fill="#222")
    wtext(t, 22.0, (yN_court[1] + yN_corr_wall[0]) / 2 - 0.15, "CORRIDOR (1500 WIDE)", size=1.9, fill="#222")
    X, Y = t((REAR_CORR[0] + REAR_CORR[1]) / 2, 8.4)
    text(X + 0.7, Y, "CORRIDOR (1200)", size=1.6, rot=-90, fill="#222")
    # courtyard
    X, Y = t(18.0, 8.55)
    text(X, Y - 1.5, "OPEN COURTYARD", size=3.2, weight="bold", fill="#3a6b35")
    text(X, Y + 2.8, "LANDSCAPED  ·  5500 WIDE  ·  PAVED WALKWAY TO RECEPTION", size=1.8, fill="#3a6b35")
    # paved walkway (dashed)
    line(t, 0.0, 7.75, BLK_W[0], 7.75, sw=0.1, stroke="#3a6b35", extra='stroke-dasharray="1.2,0.8"')
    line(t, 0.0, 9.35, BLK_W[0], 9.35, sw=0.1, stroke="#3a6b35", extra='stroke-dasharray="1.2,0.8"')
    # feature planting circles
    for x in (4.0, 12.0, 26.0, 32.0):
        circle(t, x, 10.4, 0.45, sw=0.1, stroke="#3a6b35")
        circle(t, x, 6.65, 0.35, sw=0.1, stroke="#3a6b35")
    # entrance arrows
    for (x, y, rot, lab) in [(-3.4, 8.55, 0, "MAIN ENTRY")]:
        X, Y = t(x, y)
        E(f'<path d="M {f(X - 6)} {f(Y)} L {f(X + 6)} {f(Y)} M {f(X + 3.5)} {f(Y - 2)} L {f(X + 6)} {f(Y)} L {f(X + 3.5)} {f(Y + 2)}" stroke="#000" stroke-width="0.35" fill="none"/>')
        text(X, Y - 3, lab, size=2.0, weight="bold")

def fanlight_marks(t):
    pass

# ---------------- DIMENSIONS ----------------
def dim_h(t, xs, y_ref, off, labels=None, size=1.7, ext_from=None, show_small=True):
    """chain dimension along x at world y = y_ref, offset 'off' mm on paper (neg=up)."""
    Xs = [t(x, y_ref)[0] for x in xs]
    Yref = t(0, y_ref)[1]
    Yd = Yref + off
    E(f'<line x1="{f(Xs[0] - 2)}" y1="{f(Yd)}" x2="{f(Xs[-1] + 2)}" y2="{f(Yd)}" stroke="#000" stroke-width="0.13"/>')
    sgn = 1 if off > 0 else -1
    for X in Xs:
        y0 = (t(0, ext_from)[1] if ext_from is not None else Yref) + sgn * 1.5
        E(f'<line x1="{f(X)}" y1="{f(y0)}" x2="{f(X)}" y2="{f(Yd + sgn * 1.5)}" stroke="#000" stroke-width="0.1"/>')
        E(f'<line x1="{f(X - 0.9)}" y1="{f(Yd + 0.9)}" x2="{f(X + 0.9)}" y2="{f(Yd - 0.9)}" stroke="#000" stroke-width="0.3"/>')
    for k in range(len(xs) - 1):
        v = round((xs[k + 1] - xs[k]) * 1000)
        lab = labels[k] if labels else str(v)
        mid = (Xs[k] + Xs[k + 1]) / 2
        if Xs[k + 1] - Xs[k] < 4:
            if show_small:
                text(mid, Yd - 0.8 + (0 if k % 2 == 0 else 0), lab, size=1.05)
        else:
            text(mid, Yd - 0.8, lab, size=size)

def dim_v(t, ys, x_ref, off, labels=None, size=1.7, show_small=True):
    Ys = [t(x_ref, y)[1] for y in ys]
    Xref = t(x_ref, 0)[0]
    Xd = Xref + off
    E(f'<line x1="{f(Xd)}" y1="{f(Ys[0] + 2)}" x2="{f(Xd)}" y2="{f(Ys[-1] - 2)}" stroke="#000" stroke-width="0.13"/>')
    sgn = 1 if off > 0 else -1
    for Y in Ys:
        E(f'<line x1="{f(Xref + sgn * 1.5)}" y1="{f(Y)}" x2="{f(Xd + sgn * 1.5)}" y2="{f(Y)}" stroke="#000" stroke-width="0.1"/>')
        E(f'<line x1="{f(Xd - 0.9)}" y1="{f(Y + 0.9)}" x2="{f(Xd + 0.9)}" y2="{f(Y - 0.9)}" stroke="#000" stroke-width="0.3"/>')
    for k in range(len(ys) - 1):
        v = round((ys[k + 1] - ys[k]) * 1000)
        lab = labels[k] if labels else str(v)
        mid = (Ys[k] + Ys[k + 1]) / 2
        if abs(Ys[k + 1] - Ys[k]) < 4:
            if show_small:
                text(Xd - 0.8, mid, lab, size=1.05, rot=-90)
        else:
            text(Xd - 0.8, mid, lab, size=size, rot=-90)

# ---------------- SHEET ----------------
W_, H_ = 841, 594
E(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_}mm" height="{H_}mm" viewBox="0 0 {W_} {H_}" font-family="DejaVu Sans, Arial, sans-serif">')
E(f'<rect x="0" y="0" width="{W_}" height="{H_}" fill="#fff"/>')
E(f'<rect x="10" y="10" width="{W_ - 20}" height="{H_ - 20}" fill="none" stroke="#000" stroke-width="0.7"/>')
E(f'<rect x="12" y="12" width="{W_ - 24}" height="{H_ - 24}" fill="none" stroke="#000" stroke-width="0.25"/>')

# ---------- FLOOR PLAN 1:100 ----------
TF = T(68, 250, 10)
draw_walls(TF)
draw_openings(TF, doors=True)
draw_fixtures(TF)
draw_lounge_kitchen_reception(TF)

# dimension chains
xsN = [0]
for i in range(NB):
    xsN += [a[i], b[i]]
xsN += [L]
dim_h(TF, xsN, yN_out0, -12)
dim_h(TF, [0, L], yN_out0, -20)
xsS = [0, a[0], b[1]] + sum([[a[i], b[i]] for i in range(2, NB)], []) + [L]
dim_h(TF, xsS, 0, 12)
dim_h(TF, [0, BLK_W[0], BLK_W[1], BLK_IN[1], BLK_E[1], REAR_CORR[1], L], 0, 20,
      labels=["36200 (COURTYARD)", "225", "3500", "150", "1200", "225"])
dim_h(TF, [0, L], 0, 28)
ys = [0, EXT, yS_corr_wall[0], yS_corr_wall[1], yS_court[0], yS_court[1], yN_court[0], yN_court[1],
      yN_corr_wall[0], yN_corr_wall[1], yN_in0, yN_out0]
dim_v(TF, [0, EXT, yS_court[0], yS_court[1], yN_court[0], yN_court[1], yN_corr_wall[0], yN_corr_wall[1], yN_in0, yN_out0], 0, -12)
dim_v(TF, [0, yN_out0], 0, -20)
dim_v(TF, [0, EXT, yS_corr_wall[0], yS_corr_wall[1], yS_court[0], yS_court[1], REC_PART[0], REC_PART[1],
           yN_court[0], yN_court[1], yN_corr_wall[0], yN_corr_wall[1], yN_in(L), yN_out(L)], L, 12)
# typical en-suite dims (Room 1)
m1 = mapper("S", 2, "E")

# fence-side note
X, Y = TF(0, yN_out0)
text(X - 18, Y - 26, "", size=1)

# plan title
X, Y = TF(0, 0)
text(TF(L / 2, 0)[0], Y + 40, "GROUND FLOOR PLAN", size=5.5, weight="bold")
text(TF(L / 2, 0)[0], Y + 46, "SCALE 1:100 @ A1   ·   ALL DIMENSIONS IN MILLIMETRES", size=2.4)
E(f'<line x1="{f(TF(L/2,0)[0]-38)}" y1="{f(Y+41.8)}" x2="{f(TF(L/2,0)[0]+38)}" y2="{f(Y+41.8)}" stroke="#000" stroke-width="0.4"/>')

# north arrow (floor plan)
def north_arrow(X, Y, r=7):
    E(f'<circle cx="{f(X)}" cy="{f(Y)}" r="{r}" fill="none" stroke="#000" stroke-width="0.3"/>')
    E(f'<path d="M {f(X)} {f(Y - r - 1)} L {f(X + r * 0.45)} {f(Y + r * 0.6)} L {f(X)} {f(Y + r * 0.25)} Z" fill="#000"/>')
    E(f'<path d="M {f(X)} {f(Y - r - 1)} L {f(X - r * 0.45)} {f(Y + r * 0.6)} L {f(X)} {f(Y + r * 0.25)} Z" fill="#fff" stroke="#000" stroke-width="0.25"/>')
    text(X, Y - r - 2.5, "N", size=4, weight="bold")
north_arrow(600, 36)
text(600, 52, "(ASSUMED)", size=1.8)

# scale bar
def scale_bar(X, Y, sc, n=5, step=1, label="METRES"):
    for k in range(n):
        E(f'<rect x="{f(X + k * step * sc)}" y="{f(Y)}" width="{f(step * sc)}" height="1.6" fill="{"#000" if k % 2 == 0 else "#fff"}" stroke="#000" stroke-width="0.2"/>')
        text(X + k * step * sc, Y + 4.2, str(k * step), size=1.8)
    text(X + n * step * sc, Y + 4.2, str(n * step), size=1.8)
    text(X + n * step * sc / 2, Y - 1.5, label, size=1.8)
scale_bar(TF(L, 0)[0] - 50, TF(0, 0)[1] + 41, 10, 5, 1, "SCALE 1:100 (METRES)")

# ---------- SITE PLAN 1:200 ----------
TSITE = T(58, 512, 6.6667)
TB = T(58, 512, 6.6667, dx=FRONT, dy=SIDE)
PW = SIDE + D + SIDE
fence = [(0, 0), (PLOT_L, 0), (PLOT_L, PW - NARROW), (FRONT + XS, PW), (0, PW)]
# hatch setback zone lightly
poly(TSITE, fence, fill="#f4f4f0", stroke="none")
# parking & paving
pk = "#888"
rect(TSITE, 0.2, 0.2, FRONT, PW - 0.2, fill="#e9e9e9", stroke="none")
# building
for w in wall_list():
    poly(TB, w, fill=WALL, stroke=WALL, sw=0.03)
for wing, i, name, side in ROOMS:
    for w in toilet_walls(wing, i, side):
        poly(TB, w, fill=WALL, stroke=WALL, sw=0.03)
draw_openings(TB, doors=False)
rect(TB, EXT, yS_court[1], BLK_W[0], yN_court[0], fill="#dfeedd", stroke="none")
# fence line
p = " ".join(f"{f(X)},{f(Y)}" for X, Y in (TSITE(*q) for q in fence))
E(f'<polygon points="{p}" fill="none" stroke="#000" stroke-width="0.6" stroke-dasharray="3,0.8,0.8,0.8"/>')
# gate (vehicle 4500 sliding) + pedestrian gate
G0, G1 = 7.8, 12.3
X0, Y0 = TSITE(0, G0); X1, Y1 = TSITE(0, G1)
E(f'<line x1="{f(X0)}" y1="{f(Y0)}" x2="{f(X1)}" y2="{f(Y1)}" stroke="#fff" stroke-width="1.2"/>')
E(f'<rect x="{f(X0 - 1.6)}" y="{f(Y1)}" width="1.0" height="{f(Y0 - Y1)}" fill="none" stroke="#000" stroke-width="0.3"/>')
for k in range(9):
    yy = Y1 + k * (Y0 - Y1) / 9
    E(f'<line x1="{f(X0 - 1.6)}" y1="{f(yy)}" x2="{f(X0 - 0.6)}" y2="{f(yy + (Y0 - Y1) / 9)}" stroke="#000" stroke-width="0.12"/>')
text(X0 - 3.5, (Y0 + Y1) / 2, "SLIDING GATE 4500", size=1.9, rot=-90, weight="bold")
P0, P1 = 12.45, 13.45
X0, Y0 = TSITE(0, P0); X1, Y1 = TSITE(0, P1)
E(f'<line x1="{f(X0)}" y1="{f(Y0)}" x2="{f(X1)}" y2="{f(Y1)}" stroke="#fff" stroke-width="1.2"/>')
arc_door(TSITE, (0, P1), (0, P0), (1, 0), 1.0)
text(X0 - 3.5, (Y0 + Y1) / 2 - 7, "PED. GATE", size=1.5, rot=-90)
# gatehouse block: security post + generator room
gx0, gx1, gy0, gy1 = 0.2, 4.2, 17.9, PW - 0.2
rect(TSITE, gx0, gy0, gx1, gy1, fill=WALL, stroke=WALL, sw=0.05)
rect(TSITE, gx0 + 0.15, gy0 + 0.15, 1.95, gy1 - 0.15, fill="#fff", stroke="none")
rect(TSITE, 2.1, gy0 + 0.15, gx1 - 0.15, gy1 - 0.15, fill="#fff", stroke="none")
door_h(TSITE, 0.5, 1.3, gy0, gy0 + 0.15, -1, hinge="L")
window_v(TSITE, 18.4, 19.4, gx0, gx0 + 0.15)
door_h(TSITE, 2.5, 3.7, gy0, gy0 + 0.15, -1, double=True)
wtext(TSITE, 1.05, 19.0, "SEC.", size=1.5, weight="bold")
wtext(TSITE, 3.15, 19.0, "GEN.", size=1.5, weight="bold")
# convenience (2 WCs)
cx0, cx1, cy0, cy1 = 0.2, 2.9, 0.2, 2.1
rect(TSITE, cx0, cy0, cx1, cy1, fill=WALL, stroke=WALL, sw=0.05)
rect(TSITE, cx0 + 0.15, cy0 + 0.15, 1.475, cy1 - 0.15, fill="#fff", stroke="none")
rect(TSITE, 1.625, cy0 + 0.15, cx1 - 0.15, cy1 - 0.15, fill="#fff", stroke="none")
door_h(TSITE, 0.55, 1.25, cy1 - 0.15, cy1, +1, hinge="L")
door_h(TSITE, 1.85, 2.55, cy1 - 0.15, cy1, +1, hinge="L")
wc(TSITE, 0.9, cy0 + 0.15, (0, 1)); wc(TSITE, 2.2, cy0 + 0.15, (0, 1))
wtext(TSITE, 1.55, -1.3, "", size=1)
# parking bays 2400 x 4800
bays = [(1.8, 4.2), (4.2, 6.6), (6.6, 9.0), (11.0, 13.4), (13.4, 15.8), (15.8, 18.2)]
for k, (y0, y1) in enumerate(bays):
    rect(TSITE, 4.2, y0, 9.0, y1, fill="#fff", stroke="#000", sw=0.2)
    wtext(TSITE, 6.6, (y0 + y1) / 2 - 0.35, f"P{k + 1}", size=1.9, weight="bold")
    rect(TSITE, 8.6, y0 + 0.5, 8.75, y1 - 0.5, fill="#000", stroke="none")  # wheel stop
# walkway apron & pedestrian path
rect(TSITE, 9.0, SIDE, FRONT, PW - SIDE, fill="#cfcfcf", stroke="none")
rect(TSITE, 0.3, 9.0, FRONT, 11.0, fill="#cfcfcf", stroke="none")
wtext(TSITE, 6.6, 9.75, "PEDESTRIAN WALKWAY", size=1.4)
wtext(TSITE, 2.1, 5.5, "DRIVEWAY", size=1.6, rot=-90)
wtext(TSITE, 2.5, 15.0, "4200", size=1.4, rot=-90)
wtext(TSITE, 56.5, 9.8, "REAR YARD", size=2.4, weight="bold")
wtext(TSITE, 56.5, 8.6, "(kept clear)", size=1.6)
wtext(TSITE, 31.0, 9.85, "COURTYARD", size=2.2, weight="bold", fill="#3a6b35")
wtext(TSITE, 30.0, 6.2, "SOUTH WING — LOUNGE/BAR + ROOMS 1–6", size=1.6, fill="#555")
wtext(TSITE, 30.0, 13.55, "NORTH WING — ROOMS 7–13 + KITCHEN", size=1.6, fill="#555")
wtext(TSITE, 30.0, PW + 0.8, "BOUNDARY FENCE", size=1.7)
# site dims
dim_h(TSITE, [0, FRONT, FRONT + L, PLOT_L], 0, 9, size=1.7)
dim_h(TSITE, [0, PLOT_L], 0, 16, size=1.7)
dim_v(TSITE, [0, SIDE, SIDE + D, PW], 0, -10, size=1.6)
dim_v(TSITE, [0, PW - NARROW], PLOT_L, 9, size=1.6)
dim_v(TSITE, [0, SIDE, SIDE + yN_out(L)], FRONT + L, 5, size=1.3, show_small=True)
X, Y = TSITE(PLOT_L, PW - NARROW)
text(X - 22, Y - 6, "FENCE NARROWS ≈2000 TOWARD REAR", size=1.6)
X, Y = TSITE(0, 0)
text(TSITE(PLOT_L / 2, 0)[0], Y + 26, "SITE LAYOUT PLAN", size=5, weight="bold")
text(TSITE(PLOT_L / 2, 0)[0], Y + 31.5, "SCALE 1:150 @ A1   ·   SETBACKS: FRONT 10 m · REAR 10 m · SIDES 1.5 m", size=2.2)
north_arrow(TSITE(PLOT_L, 0)[0] + 20, TSITE(0, PW)[1] + 6, 5.5)
scale_bar(TSITE(PLOT_L, 0)[0] - 66, Y + 22, 6.6667, 5, 2, "SCALE 1:150 (METRES)")

# ---------- RIGHT INFO PANEL (legend + schedules) between plan & title column ----------
px = 545
def box_title(X, Y, s):
    text(X, Y, s, size=2.6, anchor="start", weight="bold")
    E(f'<line x1="{X}" y1="{Y + 1.2}" x2="{X + 115}" y2="{Y + 1.2}" stroke="#000" stroke-width="0.3"/>')

# LEGEND
Y0 = 64
box_title(px, Y0, "LEGEND")
lg = T(px, 0, 10)
rows = [
    ("wall225", "225 mm sandcrete block wall (external)"),
    ("wall150", "150 mm block wall (internal partition)"),
    ("wall100", "100 mm block wall (en-suite partition)"),
    ("door", "Door (leaf + swing)"),
    ("window", "Window"),
    ("wc", "WC  ·  wash-hand basin  ·  shower tray"),
    ("dim", "Dimension (mm)"),
    ("fence", "Boundary fence"),
]
for k, (kind, lab) in enumerate(rows):
    yy = Y0 + 7 + k * 7.2
    if kind.startswith("wall"):
        th = {"wall225": 2.25, "wall150": 1.5, "wall100": 1.0}[kind]
        E(f'<rect x="{px}" y="{yy - th / 2}" width="14" height="{th}" fill="{WALL}"/>')
    elif kind == "door":
        E(f'<rect x="{px}" y="{yy + 1}" width="2" height="1.5" fill="{WALL}"/><rect x="{px + 11}" y="{yy + 1}" width="3" height="1.5" fill="{WALL}"/>')
        E(f'<line x1="{px + 2}" y1="{yy + 1}" x2="{px + 2}" y2="{yy - 8 + 1}" stroke="#000" stroke-width="0.25"/>')
        E(f'<path d="M {px + 2} {yy - 7} A 9 9 0 0 1 {px + 11} {yy + 1}" fill="none" stroke="#000" stroke-width="0.12" stroke-dasharray="0.8,0.5"/>')
    elif kind == "window":
        E(f'<rect x="{px}" y="{yy - 1.1}" width="2.5" height="2.25" fill="{WALL}"/><rect x="{px + 11.5}" y="{yy - 1.1}" width="2.5" height="2.25" fill="{WALL}"/>')
        E(f'<rect x="{px + 2.5}" y="{yy - 1.1}" width="9" height="2.25" fill="none" stroke="#000" stroke-width="0.15"/><line x1="{px + 2.5}" y1="{yy}" x2="{px + 11.5}" y2="{yy}" stroke="#000" stroke-width="0.15"/>')
    elif kind == "wc":
        tl = T(px, yy + 2.0, 6)
        wc(tl, 0.4, 0, (0, 1))
        poly(tl, [(1.0, 0), (1.6, 0), (1.6, 0.42), (1.0, 0.42)], fill="#fff", sw=0.13)
        poly(tl, [(1.9, 0), (2.5, 0), (2.5, 0.6), (1.9, 0.6)], fill="#fff", sw=0.13)
        line(tl, 1.9, 0, 2.5, 0.6, sw=0.08); line(tl, 2.5, 0, 1.9, 0.6, sw=0.08)
    elif kind == "dim":
        E(f'<line x1="{px}" y1="{yy}" x2="{px + 14}" y2="{yy}" stroke="#000" stroke-width="0.13"/>')
        for xx in (px + 1, px + 13):
            E(f'<line x1="{xx - 0.9}" y1="{yy + 0.9}" x2="{xx + 0.9}" y2="{yy - 0.9}" stroke="#000" stroke-width="0.3"/>')
        text(px + 7, yy - 0.8, "5000", size=1.3)
    elif kind == "fence":
        E(f'<line x1="{px}" y1="{yy}" x2="{px + 14}" y2="{yy}" stroke="#000" stroke-width="0.6" stroke-dasharray="3,0.8,0.8,0.8"/>')
    text(px + 18, yy + 0.8, lab, size=2.0, anchor="start")

# DOOR & WINDOW SCHEDULE
Y1 = Y0 + 7 + len(rows) * 7.2 + 8
box_title(px, Y1, "DOOR & WINDOW SCHEDULE")
sched = [
    ("D1", "1200 × 2100", "Double-leaf, glazed/panel", "Corridor↔courtyard, lounge↔courtyard, reception, lounge front"),
    ("D2", "1000 × 2100", "Single-leaf, solid", "Rear corridor exit"),
    ("D3", "900 × 2100", "Single-leaf flush + louvred fanlight", "Guest rooms, kitchen, store"),
    ("D4", "700 × 2100", "Single-leaf flush (PVC/WPC)", "En-suite toilets"),
    ("W1", "1500 × 1200", "Casement, sill 900, burglar-proof", "Guest rooms, lounge"),
    ("W2", "1200 × 1200", "Casement, sill 900, burglar-proof", "Corridors (courtyard side), kitchen, reception"),
    ("W3", "600 × 600", "High-level louvre, sill 1800", "En-suite toilets, store"),
]
hdr = ["MARK", "SIZE (mm)", "TYPE", "LOCATION"]
cols = [px, px + 11, px + 31, px + 72]
yy = Y1 + 6
for c, h in zip(cols, hdr):
    text(c, yy, h, size=1.8, anchor="start", weight="bold")
for k, r in enumerate(sched):
    y2 = yy + 5.5 + k * 8.2
    E(f'<line x1="{px}" y1="{y2 - 3.8}" x2="{px + 115}" y2="{y2 - 3.8}" stroke="#bbb" stroke-width="0.15"/>')
    text(cols[0], y2, r[0], size=1.9, anchor="start", weight="bold")
    text(cols[1], y2, r[1], size=1.8, anchor="start")
    # wrap type and location
    def wrap(s, n):
        words, lines, cur = s.split(), [], ""
        for w in words:
            if len(cur) + len(w) + 1 > n:
                lines.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur); return lines
    for j, ln in enumerate(wrap(r[2], 24)):
        text(cols[2], y2 + j * 2.6, ln, size=1.7, anchor="start")
    for j, ln in enumerate(wrap(r[3], 26)):
        text(cols[3], y2 + j * 2.6, ln, size=1.7, anchor="start")

# ROOM SCHEDULE (below site plan to the right)
gfa = L * D - (BLK_W[0] - 0) * (yN_court[0] - yS_court[1]) - K * (L - XS) ** 2 / 2
court = BLK_W[0] * (yN_court[0] - yS_court[1])
rx, ry = 545, 222
text(rx, ry, "ACCOMMODATION SCHEDULE", size=2.6, anchor="start", weight="bold")
E(f'<line x1="{rx}" y1="{ry + 1.2}" x2="{rx + 120}" y2="{ry + 1.2}" stroke="#000" stroke-width="0.3"/>')
rows2 = [
    ("SPACE", "NO.", "CLEAR SIZE (mm)", "AREA m²"),
    ("Guest rooms 1–6, 8–13 (en-suite)", "12", "5000 × 4000", "20.0 each"),
    ("Guest room 7 (slanted rear wall)", "1", "5000 × 3500–4000", f"{room_area('N', 6):.1f}"),
    ("En-suite toilet (WC, basin, shower)", "13", "1800 × 2100", "3.8 each"),
    ("Lounge / bar (no corridor)", "1", f"{round((b[1] - a[0]) * 1000)} × {round((yS_court[0] - yS_in) * 1000)}", f"{(b[1] - a[0]) * (yS_court[0] - yS_in):.1f}"),
    ("Kitchen", "1", "5000 × 3000–3500", f"{BAY * (yN_in(cen[7]) - yN_corr_wall[1]):.1f}"),
    ("Reception", "1", "3500 × 3350", f"{3.5 * 3.35:.1f}"),
    ("Store", "1", "3500 × 2000", "7.0"),
    ("Corridors: north / south / rear", "3", "1500 / 1200 / 1200 wide", "—"),
    ("Security post · generator room", "1+1", "1800 × 2200 · 1950 × 2200", "4.0 · 4.3"),
    ("Outdoor convenience (2 WCs)", "1", "2 × 1125 × 1600", "3.6"),
    ("Car parking bays", "6", "2400 × 4800", "—"),
    ("GROSS FLOOR AREA (main building)", "", "", f"≈ {gfa:.0f}"),
    ("Open courtyard", "", f"{round(BLK_W[0] * 1000)} × 5500", f"≈ {court:.0f}"),
    ("Plot (approx.)", "", "61500 × 20400 / 18400", f"≈ {PLOT_L * PW - NARROW * (PLOT_L - FRONT - XS) / 2:.0f}"),
]
cx = [rx, rx + 52, rx + 62, rx + 102]
for k, r in enumerate(rows2):
    y2 = ry + 6.5 + k * 4.6
    bold = "bold" if k == 0 or r[0].startswith("GROSS") else "normal"
    for c, v in zip(cx, r):
        text(c, y2, v, size=1.75, anchor="start", weight=bold)
    if k in (0, 11):
        E(f'<line x1="{rx}" y1="{y2 + 1.5}" x2="{rx + 120}" y2="{y2 + 1.5}" stroke="#999" stroke-width="0.15"/>')
text(rx, ry + 6.5 + len(rows2) * 4.6 + 1, "Total guest rooms: 13 (all en-suite)", size=2.0, anchor="start", weight="bold")

# ---------- TITLE COLUMN ----------
tx0 = 671
E(f'<line x1="{tx0}" y1="12" x2="{tx0}" y2="{H_ - 12}" stroke="#000" stroke-width="0.5"/>')
# GENERAL NOTES
ny = 24
text(tx0 + 5, ny, "GENERAL NOTES", size=2.8, anchor="start", weight="bold")
E(f'<line x1="{tx0 + 5}" y1="{ny + 1.3}" x2="{W_ - 17}" y2="{ny + 1.3}" stroke="#000" stroke-width="0.3"/>')
notes = [
    "All dimensions are in millimetres unless otherwise stated. Do not scale from this drawing; use figured dimensions only.",
    "Room sizes are clear internal dimensions (face of block to face of block), excluding plaster.",
    "External walls: 225 mm (9\") sandcrete hollow block. Internal partitions: 150 mm (6\"). En-suite partitions: 100 mm (4\").",
    "Site setbacks: front (gate side) 10.0 m, rear 10.0 m, sides 1.5 m. Plot size derived from setbacks; confirm by survey plan.",
    "North boundary narrows approx. 2.0 m toward the rear; Room 7 and kitchen outer wall follows the fence line, keeping 1.5 m clear.",
    "North orientation assumed (top of sheet). Confirm on site before setting out.",
    "Corridor windows facing the courtyard provide daylight and cross-ventilation. Louvred fanlights over guest-room doors.",
    "All external doors and ground-floor windows to be burglar-proofed. Exit doors open outward.",
    "Rear yard kept clear. Septic tank, soakaway and water supply positions to be agreed with the plumbing engineer.",
    "Generator room: louvred double door, exhaust vented to open air, away from guest rooms.",
    "Read with structural, electrical and plumbing drawings. To be checked by a registered architect/engineer before construction.",
]
yy = ny + 7
for k, n in enumerate(notes):
    words, lines, cur = n.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 66:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    text(tx0 + 5, yy, f"{k + 1}.", size=1.9, anchor="start", weight="bold")
    for ln in lines:
        text(tx0 + 10, yy, ln, size=1.9, anchor="start")
        yy += 2.9
    yy += 1.4

# Revision table
yy += 4
text(tx0 + 5, yy, "REVISIONS", size=2.4, anchor="start", weight="bold")
yy += 2
E(f'<rect x="{tx0 + 5}" y="{yy}" width="{W_ - 17 - tx0 - 5}" height="18" fill="none" stroke="#000" stroke-width="0.25"/>')
E(f'<line x1="{tx0 + 5}" y1="{yy + 5}" x2="{W_ - 17}" y2="{yy + 5}" stroke="#000" stroke-width="0.2"/>')
for c in (tx0 + 17, tx0 + 40):
    E(f'<line x1="{c}" y1="{yy}" x2="{c}" y2="{yy + 18}" stroke="#000" stroke-width="0.2"/>')
text(tx0 + 7, yy + 3.6, "REV", size=1.8, anchor="start", weight="bold")
text(tx0 + 19, yy + 3.6, "DATE", size=1.8, anchor="start", weight="bold")
text(tx0 + 42, yy + 3.6, "DESCRIPTION", size=1.8, anchor="start", weight="bold")
text(tx0 + 7, yy + 9.4, "P1", size=1.8, anchor="start")
text(tx0 + 19, yy + 9.4, "05/11/2026", size=1.8, anchor="start")
text(tx0 + 42, yy + 9.4, "Preliminary issue for client review", size=1.8, anchor="start")
E(f'<line x1="{tx0 + 5}" y1="{yy + 11.5}" x2="{W_ - 17}" y2="{yy + 11.5}" stroke="#000" stroke-width="0.15"/>')
text(tx0 + 7, yy + 15.6, "P2", size=1.8, anchor="start", weight="bold")
text(tx0 + 19, yy + 15.6, "05/11/2026", size=1.8, anchor="start")
text(tx0 + 42, yy + 15.6, "Lounge enlarged (no corridor); corridor end doors removed; rear yard cleared", size=1.6, anchor="start")

# TITLE BLOCK
tb_y = 430
E(f'<line x1="{tx0}" y1="{tb_y}" x2="{W_ - 12}" y2="{tb_y}" stroke="#000" stroke-width="0.5"/>')
text(tx0 + 5, tb_y + 7, "PROJECT", size=1.7, anchor="start", fill="#555")
text(tx0 + 5, tb_y + 14, "PROPOSED TOCHI HOTEL", size=4.6, anchor="start", weight="bold")
text(tx0 + 5, tb_y + 19.5, "Single-storey, 13 en-suite guest rooms · lounge/bar · kitchen", size=2.0, anchor="start")
E(f'<line x1="{tx0}" y1="{tb_y + 23}" x2="{W_ - 12}" y2="{tb_y + 23}" stroke="#000" stroke-width="0.3"/>')
text(tx0 + 5, tb_y + 29, "DRAWING TITLE", size=1.7, anchor="start", fill="#555")
text(tx0 + 5, tb_y + 36, "GROUND FLOOR PLAN &amp; SITE LAYOUT", size=3.9, anchor="start", weight="bold")
E(f'<line x1="{tx0}" y1="{tb_y + 40}" x2="{W_ - 12}" y2="{tb_y + 40}" stroke="#000" stroke-width="0.3"/>')
cells = [
    ("CLIENT", "________________", "LOCATION", "________________"),
    ("SCALE", "1:100 & 1:150 @ A1", "DATE", "05 NOVEMBER 2026"),
    ("DRAWING NO.", "TH-A-101", "REVISION", "P2"),
    ("SHEET", "1 OF 1", "STATUS", "PRELIMINARY"),
    ("CHECKED BY", "________________", "APPROVED BY", "________________"),
]
cw = (W_ - 12 - tx0) / 2
for k, (l1, v1, l2, v2) in enumerate(cells):
    y0 = tb_y + 40 + k * 12
    E(f'<line x1="{tx0}" y1="{y0 + 12}" x2="{W_ - 12}" y2="{y0 + 12}" stroke="#000" stroke-width="0.25"/>')
    E(f'<line x1="{tx0 + cw}" y1="{y0}" x2="{tx0 + cw}" y2="{y0 + 12}" stroke="#000" stroke-width="0.25"/>')
    text(tx0 + 4, y0 + 4.2, l1, size=1.6, anchor="start", fill="#555")
    text(tx0 + 4, y0 + 9.6, v1.replace("&", "&amp;"), size=2.5, anchor="start", weight="bold")
    text(tx0 + cw + 4, y0 + 4.2, l2, size=1.6, anchor="start", fill="#555")
    text(tx0 + cw + 4, y0 + 9.6, v2, size=2.5, anchor="start", weight="bold")
y0 = tb_y + 40 + 5 * 12
text(tx0 + 4, y0 + 5, "DRAWN BY", size=1.6, anchor="start", fill="#555")
text(tx0 + 4, y0 + 12.5, "Engr. Chinemenum Paul Ogbonda", size=3.6, anchor="start", weight="bold")
text(tx0 + 4, y0 + 18, "Signature: ______________________", size=2.0, anchor="start")
E(f'<rect x="{tx0}" y="{H_ - 26}" width="{W_ - 12 - tx0}" height="14" fill="#111"/>')
text(tx0 + (W_ - 12 - tx0) / 2, H_ - 17, "NOT FOR CONSTRUCTION — FOR CLIENT REVIEW", size=2.8, weight="bold", fill="#fff")

E('</svg>')
open('/home/claude/hotel/tochi_hotel_floor_plan.svg', 'w').write("\n".join(out))
print("GFA", round(gfa, 1), "court", round(court, 1), "Rm7", round(room_area('N', 6), 2), "K", K)
