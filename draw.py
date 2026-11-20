#!/usr/bin/env python3
"""Render the Friday 20 November 2026 front page as a single 1024x1024 PNG.

The sheet carries 42 verified stories from that day: thirteen illustrated
feature cards on top, a world map with numbered pins and a 29-item
"also on" list underneath. Every picture is flat vector-style art drawn
with Pillow primitives, and every word is set from the DejaVu family.

The program is fully deterministic: no clocks, no randomness, no network.
Running it twice produces the same bytes, because the PNG is written with
fixed settings and the picture depends only on the data below.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "entry.png")

PAGE_W, PAGE_H = 1024, 1024

PAL = {
    "paper": (247, 241, 227),
    "ink": (26, 26, 26),
    "navy": (20, 36, 61),
    "gold": (201, 162, 39),
    "red": (179, 35, 42),
    "blue": (31, 78, 121),
    "orange": (180, 90, 27),
    "green": (46, 125, 50),
    "purple": (106, 61, 154),
    "teal": (15, 118, 110),
    "grey": (107, 114, 128),
    "white": (255, 255, 255),
    "card": (255, 252, 244),
    "rule": (150, 140, 120),
    "deck": (60, 55, 45),
}

FACES = {
    "serif_b": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

REGION_INK = {
    "AMERICAS": "red", "UNITED STATES": "red", "EUROPE": "blue",
    "MIDDLE EAST": "orange", "AFRICA": "green", "ASIA": "purple",
    "OCEANIA": "teal", "GLOBAL": "grey", "VATICAN": "blue",
}

# ---------------------------------------------------------------- data
# The thirteen feature stories, in card order. Headlines and decks are the
# verified 20 November 2026 wordings; the region drives the kicker colour.
STORIES = [
    {"region": "ASIA", "topic": "DIPLOMACY",
     "head": "Trump, Xi and Putin hail \u2018peace declaration\u2019",
     "deck": "After the first trilateral, the three call for UN reform and nuclear-risk talks."},
    {"region": "ASIA", "topic": "WEATHER",
     "head": "Cyclone Akvan makes landfall in east India",
     "deck": "Storm crosses near Gopalpur by noon; 3 lakh evacuated, 423 rescue teams out."},
    {"region": "EUROPE", "topic": "UKRAINE WAR",
     "head": "Russian strikes hit Kyiv; embassies damaged",
     "deck": "One killed as drones hit the capital; Putin vows payback for bridge strikes."},
    {"region": "GLOBAL", "topic": "MARKETS",
     "head": "Anthropic closes up 17% after wild debut",
     "deck": "ANT ends day one at $97.17 after opening at $111.50; the offering closes today."},
    {"region": "GLOBAL", "topic": "CLIMATE",
     "head": "COP31 closes today with deal still unwritten",
     "deck": "Ministers race the Friday deadline over fossil fuels and $120bn finance."},
    {"region": "MIDDLE EAST", "topic": "IRAN WAR",
     "head": "Houthi strike hits Riyadh tower in escalation",
     "deck": "Saudi reports damage, no injuries; Iran has hit 18 ships this month, monitors say."},
    {"region": "EUROPE", "topic": "DIPLOMACY",
     "head": "Allies meet in Berlin after Shenzhen talks",
     "deck": "Kushner says Europe is united and sees a \u2018real desire for peace\u2019 on Ukraine."},
    {"region": "ASIA", "topic": "DIPLOMACY",
     "head": "Modi opens first SCO dialogue forum in Delhi",
     "deck": "Forum opens at Purana Quila; Pakistan sends a minister to Delhi."},
    {"region": "OCEANIA", "topic": "SPORT",
     "head": "Nicholls century lifts New Zealand in Test",
     "deck": "Hosts reach 243 for five on day one against India; Phillips makes 94."},
    {"region": "AMERICAS", "topic": "AVIATION",
     "head": "FAA halts US departures after system failure",
     "deck": "Duffy says no sign of a hack as officials probe a router fault."},
    {"region": "AFRICA", "topic": "SPORT",
     "head": "Tunisia book World Cup place with late winner",
     "deck": "Ben Romdhane strikes in stoppage time; eight qualifiers, no goals conceded."},
    {"region": "ASIA", "topic": "POLITICS",
     "head": "Bangladesh lockdown turns violent; home torched",
     "deck": "Two ruling-party men killed; 72 Grameen Bank branches attacked in ten days."},
    {"region": "GLOBAL", "topic": "CULTURE",
     "head": "Hagia Sophia\u2019s hidden tunnels explored at last",
     "deck": "Archaeologists clear 3,000 tons of debris to reach Roman passages."},
]

# The one-line briefs, numbered 14 to 42, laid out in two columns.
BRIEFS = [
    {"n": 14, "place": "US", "text": "Senate GOP rejects Iran war-powers curb"},
    {"n": 15, "place": "Iran", "text": "ministry slams US bio-weapons claim"},
    {"n": 16, "place": "US", "text": "Trump won't rush Iran decision"},
    {"n": 17, "place": "Yemen", "text": "Houthis confirm Riyadh tower strike"},
    {"n": 18, "place": "Russia", "text": "Putin invites EU leaders to Moscow"},
    {"n": 19, "place": "Ukraine", "text": "probe finds Russia used chemical arms"},
    {"n": 20, "place": "South Korea", "text": "court sends ex-PM Han case back"},
    {"n": 21, "place": "US", "text": "Dow falls 997 pts, S&P down 1.8%"},
    {"n": 22, "place": "India", "text": "Sensex surges ~1,000 pts to 83,021"},
    {"n": 23, "place": "India", "text": "firms announce $20.5bn US investment"},
    {"n": 24, "place": "India", "text": "NEET leak charges framed vs 14"},
    {"n": 25, "place": "India", "text": "11 states/UTs reach full literacy"},
    {"n": 26, "place": "India", "text": "Shah: Kashmir free of local recruits"},
    {"n": 27, "place": "US", "text": "court orders summonses for Doval, Goel"},
    {"n": 28, "place": "Australia", "text": "sanctions Israeli settlers"},
    {"n": 29, "place": "Bulgaria", "text": "sunken tanker hit by projectiles"},
    {"n": 30, "place": "Fiji", "text": "disaster declared over El Ni\u00f1o drought"},
    {"n": 31, "place": "Slovenia", "text": "border warning for South China Sea"},
    {"n": 32, "place": "Hong Kong", "text": "Rakshitha stuns Olympic champion"},
    {"n": 33, "place": "US", "text": "oldest Pearl Harbor survivor dies at 106"},
    {"n": 34, "place": "US", "text": "TSA finds cocaine worth $27,750 in tin"},
    {"n": 35, "place": "Global", "text": "World Children's Day marked today"},
    {"n": 36, "place": "US", "text": "Games gold medallist loses arm in crash"},
    {"n": 37, "place": "India", "text": "Modi asks industry 'Where are jobs?'"},
    {"n": 38, "place": "India", "text": "EPFO approves systematic PF withdrawal"},
    {"n": 39, "place": "India", "text": "60 days of fuel held in Hormuz crisis"},
    {"n": 40, "place": "Pakistan", "text": "minister to lead Delhi SCO delegation"},
    {"n": 41, "place": "Global", "text": "NASA probes 'potato chip' Mars shapes"},
    {"n": 42, "place": "Europe", "text": "Germany rout Slovakia 6-0; NI win 1-0"},
]

# Map pins for the thirteen feature stories: (lon, lat), nudged where the
# cluster is tight so no two numbered dots collide on the 424 px map.
# 5 Antalya east to (35,36) so it clears 3 Kyiv and 13; 9 Wellington west
# so it fits inside the map edge; 10 = Chicago O'Hare, a major hub, so it
# clears 4 New York; 12 Chattogram north-east to (97,26) so it clears
# 2 Gopalpur; 13 Istanbul west to (23,42) so it clears 5 Antalya.
PINS = [
    {"n": 1, "lon": 114, "lat": 22.5, "region": "ASIA"},
    {"n": 2, "lon": 85, "lat": 19.5, "region": "ASIA"},
    {"n": 3, "lon": 30.5, "lat": 50.4, "region": "EUROPE"},
    {"n": 4, "lon": -74, "lat": 40.7, "region": "GLOBAL"},
    {"n": 5, "lon": 35, "lat": 36, "region": "GLOBAL"},
    {"n": 6, "lon": 46.7, "lat": 24.7, "region": "MIDDLE EAST"},
    {"n": 7, "lon": 13.4, "lat": 52.5, "region": "EUROPE"},
    {"n": 8, "lon": 77.2, "lat": 28.6, "region": "ASIA"},
    {"n": 9, "lon": 168, "lat": -41.3, "region": "OCEANIA"},
    {"n": 10, "lon": -87.6, "lat": 41.9, "region": "AMERICAS"},
    {"n": 11, "lon": 10.2, "lat": 36.8, "region": "AFRICA"},
    {"n": 12, "lon": 97, "lat": 26, "region": "ASIA"},
    {"n": 13, "lon": 23, "lat": 42, "region": "GLOBAL"},
]

# Rough flat continents as (lon, lat) outlines. Asia is listed before
# Europe on purpose: Europe is painted over it where they meet.
LAND = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-115, 72), (-100, 73), (-90, 74),
     (-82, 70), (-78, 62), (-68, 58), (-60, 55), (-55, 47), (-60, 44),
     (-68, 44), (-75, 38), (-76, 34), (-80, 32), (-81, 26), (-84, 30),
     (-90, 21), (-86, 16), (-92, 15), (-97, 16), (-105, 20), (-110, 23),
     (-115, 29), (-122, 37), (-124, 42), (-125, 49), (-132, 56), (-140, 60),
     (-155, 58), (-162, 58), (-168, 66)],
    # Greenland
    [(-55, 60), (-45, 60), (-38, 64), (-30, 68), (-22, 70), (-25, 76),
     (-38, 80), (-52, 78), (-58, 74), (-60, 68)],
    # South America
    [(-80, 10), (-77, 4), (-72, 11), (-64, 10), (-58, 8), (-52, 5),
     (-44, -2), (-35, -6), (-38, -12), (-41, -20), (-48, -26), (-54, -33),
     (-58, -38), (-65, -42), (-68, -50), (-70, -54), (-73, -46), (-73, -36),
     (-71, -28), (-70, -18), (-77, -12), (-80, -4), (-81, 2)],
    # Africa
    [(-17, 15), (-13, 27), (-6, 35), (3, 37), (10, 37), (19, 32),
     (25, 32), (32, 31), (35, 28), (39, 21), (43, 12), (48, 11),
     (51, 11), (46, 4), (41, -2), (40, -8), (36, -16), (33, -24),
     (28, -32), (20, -35), (17, -31), (14, -22), (12, -15), (9, -2),
     (9, 4), (2, 6), (-6, 5), (-13, 8), (-17, 15)],
    # Asia
    [(30, 70), (45, 68), (55, 69), (68, 70), (75, 72), (85, 73),
     (95, 75), (105, 76), (115, 74), (125, 72), (135, 72), (145, 72),
     (155, 70), (160, 66), (162, 60), (158, 52), (150, 59), (142, 55),
     (141, 46), (135, 43), (130, 38), (127, 39), (124, 40), (122, 37),
     (120, 32), (118, 25), (113, 22), (108, 18), (105, 10), (101, 8),
     (98, 14), (96, 16), (93, 21), (90, 22), (87, 21), (83, 18),
     (80, 13), (77, 8), (75, 12), (72, 20), (69, 22), (66, 25),
     (62, 25), (58, 26), (54, 26), (51, 28), (48, 30), (45, 29),
     (42, 31), (39, 33), (36, 36), (33, 36), (30, 40), (28, 45),
     (30, 52), (33, 58), (30, 65), (30, 70)],
    # Europe
    [(-10, 36), (-9, 43), (-3, 48), (-5, 50), (0, 52), (3, 54),
     (7, 57), (10, 59), (6, 60), (10, 62), (14, 66), (18, 69),
     (24, 71), (30, 70), (34, 68), (40, 67), (44, 66), (45, 60),
     (41, 56), (38, 52), (35, 50), (32, 46), (29, 45), (28, 42),
     (24, 40), (22, 38), (19, 40), (16, 38), (13, 44), (10, 44),
     (7, 44), (3, 42), (0, 38), (-3, 37), (-7, 37)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (119, -34), (124, -33), (129, -32),
     (133, -32), (136, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (150, -23), (146, -19), (142, -15), (142, -11), (137, -12),
     (135, -15), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]

LEGEND = [("Americas", "red"), ("Europe", "blue"), ("Middle East", "orange"),
          ("Africa", "green"), ("Asia", "purple"), ("Oceania", "teal"),
          ("Global", "grey")]

BRIEF_INK = {
    "US": "red", "Iran": "orange", "Yemen": "orange", "Russia": "blue",
    "Ukraine": "blue", "South Korea": "purple", "India": "purple",
    "Australia": "teal", "Bulgaria": "blue", "Fiji": "teal", "Slovenia": "blue",
    "Hong Kong": "purple", "Pakistan": "purple", "Global": "grey", "Europe": "blue",
}


def load_face(name, size):
    return ImageFont.truetype(FACES[name], size)


class FrontPage:
    """Owns the canvas and every drawing primitive the sheet needs."""

    def __init__(self):
        self.img = Image.new("RGB", (PAGE_W, PAGE_H), PAL["paper"])
        self.d = ImageDraw.Draw(self.img)

    # -- measuring and text -------------------------------------------
    def measure(self, text, face):
        return self.d.textlength(text, font=face)

    def write(self, xy, text, face, ink):
        self.d.text(xy, text, font=face, fill=ink)

    def split_lines(self, text, face, limit):
        """Greedy word wrap: pack as many words per line as fit in limit."""
        words = text.split()
        out = []
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if self.measure(candidate, face) <= limit or not current:
                current = candidate
            else:
                out.append(current)
                current = word
        if current:
            out.append(current)
        return out

    def best_fit(self, text, face_name, top, limit, floor=8):
        """Largest size at or below top at which text still fits limit."""
        size = top
        while size > floor:
            face = load_face(face_name, size)
            if self.measure(text, face) <= limit:
                return face
            size -= 1
        return load_face(face_name, floor)

    def region_ink(self, region):
        return PAL[REGION_INK[region]]

    # -- primitives ----------------------------------------------------
    def box(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)

    def soft_box(self, x0, y0, x1, y1, fill, radius=3):
        self.d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)

    def seg(self, pts, ink, width=1):
        self.d.line(pts, fill=ink, width=width)

    def disc(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline, width=width)

    def poly(self, pts, fill=None, outline=None):
        self.d.polygon(pts, fill=fill, outline=outline)

    def curve(self, x0, y0, x1, y1, a0, a1, ink, width=1):
        self.d.arc([x0, y0, x1, y1], a0, a1, fill=ink, width=width)

    def wedge(self, x0, y0, x1, y1, a0, a1, fill=None, outline=None, width=1):
        self.d.pieslice([x0, y0, x1, y1], a0, a1, fill=fill, outline=outline, width=width)

    def badge(self, x, y, label, bg, fg=None, size=11, pad=5):
        """Small rounded label chip; returns its width."""
        face = load_face("sans_b", size)
        wide = self.measure(label, face) + pad * 2
        self.soft_box(x, y, x + wide, y + size + pad, bg)
        self.write((x + pad, y + 2), label, face, fg or PAL["white"])
        return wide

    # -- recurring motifs ----------------------------------------------
    def figure(self, x, y, s, suit, skin=(232, 190, 150), hair=(40, 30, 25)):
        """A simple standing person: head, hair, suit, shirt triangle."""
        self.disc(x - s * 0.32, y - s * 1.05, x + s * 0.32, y - s * 0.42, fill=skin)
        self.wedge(x - s * 0.32, y - s * 1.08, x + s * 0.32, y - s * 0.55,
                   180, 360, fill=hair)
        self.poly([(x - s * 0.5, y), (x + s * 0.5, y),
                   (x + s * 0.42, y - s * 0.45), (x - s * 0.42, y - s * 0.45)],
                  fill=suit)
        self.poly([(x - s * 0.08, y - s * 0.42), (x + s * 0.08, y - s * 0.42),
                   (x, y - s * 0.1)], fill=PAL["white"])

    def burst(self, cx, cy, r, colour):
        """Sixteen-point starburst used for blasts and flames."""
        pts = [(cx + (r if k % 2 == 0 else r * 0.45) * math.cos(k * math.pi / 8),
                cy + (r if k % 2 == 0 else r * 0.45) * math.sin(k * math.pi / 8))
               for k in range(16)]
        self.poly(pts, fill=colour)

    def banner_us(self, x, y, w, h):
        for i in range(13):
            self.box(x, y + i * h / 13, x + w, y + (i + 1) * h / 13,
                     fill=PAL["red"] if i % 2 == 0 else PAL["white"])
        self.box(x, y, x + w * 0.4, y + h * 7 / 13, fill=PAL["navy"])
        for r in range(3):
            for c in range(4):
                self.disc(x + 3 + c * w * 0.09, y + 2 + r * h * 0.18,
                          x + 6 + c * w * 0.09, y + 5 + r * h * 0.18,
                          fill=PAL["white"])

    def banner_cn(self, x, y, w, h):
        self.box(x, y, x + w, y + h, fill=(222, 41, 16))
        cx, cy = x + w * 0.2, y + h * 0.28
        self.poly([(cx, cy - 5), (cx + 2, cy - 1), (cx + 6, cy - 1),
                   (cx + 3, cy + 2), (cx + 4, cy + 6), (cx, cy + 3),
                   (cx - 4, cy + 6), (cx - 3, cy + 2), (cx - 6, cy - 1),
                   (cx - 2, cy - 1)], fill=(255, 222, 0))

    def banner_ru(self, x, y, w, h):
        bands = [PAL["white"], (0, 57, 166), (213, 43, 30)]
        for i, colour in enumerate(bands):
            self.box(x, y + i * h / 3, x + w, y + (i + 1) * h / 3, fill=colour)

    def pole(self, x, y, h, banner, fw=34, fh=22):
        self.seg([x, y, x, y - h], (90, 80, 70), width=3)
        self.disc(x - 2, y - h - 3, x + 2, y - h + 1, fill=PAL["gold"])
        banner(x + 2, y - h + 2, fw, fh)

    # -- the thirteen illustrations ------------------------------------
    def scene_01(self, ax, ay, bx, by):
        """Trilateral summit: three flags, three leaders, the declaration."""
        self.box(ax, ay, bx, by, fill=(226, 232, 240))
        self.box(ax, ay, bx, ay + 46, fill=(30, 48, 78))
        tag_face = load_face("sans_b", 11)
        tag = "APEC \u00b7 SHENZHEN"
        self.write((ax + (bx - ax - self.measure(tag, tag_face)) / 2, ay + 16),
                   tag, tag_face, PAL["gold"])
        for k, banner in enumerate([self.banner_us, self.banner_cn, self.banner_ru]):
            self.pole(ax + 52 + k * 108, ay + 82, 40, banner, 44, 28)
        # round table
        self.disc(ax + 60, ay + 82, bx - 60, ay + 106, fill=(120, 82, 50))
        self.disc(ax + 60, ay + 78, bx - 60, ay + 98, fill=(150, 105, 65))
        for px, suit in [(96, (30, 40, 60)), (160, (140, 30, 30)), (224, (40, 60, 90))]:
            self.figure(ax + px, ay + 80, 22, suit)
        # declaration paper on the table
        self.box(ax + 128, ay + 88, ax + 192, ay + 116,
                 fill=PAL["white"], outline=PAL["ink"])
        for i in range(3):
            self.seg([ax + 133, ay + 93 + i * 5, ax + 187, ay + 93 + i * 5],
                     (120, 120, 120))
        self.disc(ax + 182, ay + 106, ax + 190, ay + 114,
                  fill=PAL["red"], outline=PAL["gold"])
        self.badge(ax + 8, by - 20, "DECLARATION TOWARDS PEACE", PAL["navy"], size=9)

    def scene_02(self, ax, ay, bx, by):
        """Cyclone Akvan: spiral over the Bay of Bengal, coast, shelters."""
        self.box(ax, ay, bx, by, fill=(150, 190, 220))
        # India coast, right
        self.poly([(ax + 150, ay), (bx, ay), (bx, by), (ax + 168, by),
                   (ax + 158, ay + 50), (ax + 148, ay + 22)], fill=(214, 190, 140))
        # spiral bands
        cx, cy = ax + 78, ay + 42
        for r, col in [(36, PAL["white"]), (28, (220, 235, 245)),
                       (20, PAL["white"]), (12, (220, 235, 245))]:
            self.curve(cx - r, cy - r, cx + r, cy + r, 30, 310, col, width=6)
        self.disc(cx - 7, cy - 7, cx + 7, cy + 7, fill=PAL["white"])
        # storm track arrow toward the coast
        self.seg([(cx + 30, cy + 20), (ax + 138, ay + 58)], PAL["red"], width=3)
        self.poly([(ax + 138, ay + 58), (ax + 126, ay + 52), (ax + 130, ay + 64)],
                  fill=PAL["red"])
        # shelter bus on the coast road
        self.box(ax + 168, ay + 66, ax + 196, ay + 82, fill=(240, 180, 40))
        for k in range(3):
            self.box(ax + 172 + k * 8, ay + 69, ax + 178 + k * 8, ay + 75,
                     fill=(180, 220, 240))
        self.disc(ax + 172, ay + 80, ax + 178, ay + 86, fill=PAL["ink"])
        self.disc(ax + 186, ay + 80, ax + 192, ay + 86, fill=PAL["ink"])
        # rain streaks
        for i in range(5):
            self.seg([ax + 14 + i * 12, ay + 68, ax + 10 + i * 12, ay + 80],
                     (90, 130, 170), width=2)
        self.badge(ax + 8, ay + 6, "BAY OF BENGAL", PAL["navy"], size=10)
        self.badge(ax + 92, by - 20, "3 LAKH EVACUATED", (180, 90, 27), size=9)

    def scene_03(self, ax, ay, bx, by):
        """Kyiv under drone attack: night skyline, drone, blast, embassy flags."""
        self.box(ax, ay, bx, by, fill=(18, 24, 44))
        # stars
        for sx, sy in [(20, 12), (90, 8), (180, 16), (250, 10), (140, 6)]:
            self.disc(ax + sx - 1, ay + sy - 1, ax + sx + 1, ay + sy + 1,
                      fill=PAL["white"])
        # skyline
        for bxx, bw, bh in [(8, 30, 40), (44, 24, 55), (74, 34, 34),
                            (200, 28, 48), (234, 30, 36), (270, 26, 52)]:
            self.box(ax + bxx, by - bh - 18, ax + bxx + bw, by - 18, fill=(45, 55, 80))
            for wy in range(2):
                for wx in range(2):
                    self.box(ax + bxx + 5 + wx * 11, by - bh - 12 + wy * 11,
                             ax + bxx + 9 + wx * 11, by - bh - 8 + wy * 11,
                             fill=(255, 220, 120))
        # drone, top right
        dx, dy = ax + 180, ay + 22
        self.box(dx, dy, dx + 26, dy + 8, fill=(200, 200, 200))
        self.seg([dx - 8, dy - 2, dx + 34, dy - 2], (220, 220, 220), width=2)
        self.disc(dx - 12, dy - 6, dx - 2, dy + 2, fill=(160, 160, 160))
        self.disc(dx + 28, dy - 6, dx + 38, dy + 2, fill=(160, 160, 160))
        # blast over a building
        self.burst(ax + 130, ay + 52, 14, (255, 170, 0))
        self.burst(ax + 130, ay + 52, 7, (255, 230, 120))
        self.disc(ax + 120, ay + 30, ax + 140, ay + 42, fill=(120, 120, 120))
        # street
        self.box(ax, by - 18, bx, by, fill=(30, 32, 40))
        # two embassy flags on small poles, bottom left
        self.seg([ax + 120, by - 18, ax + 120, by - 34], (200, 200, 200), width=2)
        for fy, colour in [(by - 34, PAL["red"]), (by - 29, PAL["white"]),
                           (by - 24, (30, 60, 160))]:
            self.box(ax + 122, fy, ax + 144, fy + 5, fill=colour)
        self.seg([ax + 152, by - 18, ax + 152, by - 34], (200, 200, 200), width=2)
        for fy, colour in [(by - 34, PAL["red"]), (by - 29, PAL["white"]),
                           (by - 24, PAL["red"])]:
            self.box(ax + 154, fy, ax + 176, fy + 5, fill=colour)
        self.badge(ax + 8, ay + 6, "KYIV", PAL["navy"], size=10)
        self.badge(ax + 8, by - 20, "1 KILLED", PAL["red"], size=10)

    def scene_04(self, ax, ay, bx, by):
        """Anthropic debut: dark board, chart up then down, $97.17 close."""
        self.box(ax, ay, bx, by, fill=(14, 22, 32))
        for gy in range(4):
            self.seg([ax + 8, ay + 14 + gy * 18, bx - 8, ay + 14 + gy * 18],
                     (40, 55, 75))
        # rocketing green line that then falls back
        self.seg([(ax + 12, ay + 62), (ax + 50, ay + 54), (ax + 88, ay + 34),
                  (ax + 126, ay + 10), (ax + 150, ay + 26), (ax + 172, ay + 40)],
                 (80, 220, 120), width=3)
        self.poly([(ax + 126, ay + 10), (ax + 114, ay + 8), (ax + 124, ay + 22)],
                  fill=(80, 220, 120))
        # bars
        for i, hgt in enumerate([8, 14, 20, 30]):
            self.box(ax + 20 + i * 14, ay + 78 - hgt, ax + 30 + i * 14, ay + 78,
                     fill=(60, 120, 180))
        self.write((ax + 96, ay + 50), "$97.17", load_face("sans_b", 20), PAL["white"])
        self.write((ax + 96, ay + 72), "+17% DAY ONE", load_face("sans_b", 10),
                   (80, 220, 120))
        self.badge(ax + 8, ay + 6, "ANT \u00b7 NASDAQ", (200, 120, 30), size=10)

    def scene_05(self, ax, ay, bx, by):
        """COP31: globe, thermometer at 1.5C, Antalya deadline."""
        self.box(ax, ay, bx, by, fill=(222, 228, 236))
        # globe, left
        gx, gy, gr = ax + 52, ay + 44, 34
        self.disc(gx - gr, gy - gr, gx + gr, gy + gr,
                  fill=(90, 150, 210), outline=(40, 80, 140), width=2)
        self.disc(gx - 18, gy - 22, gx + 2, gy - 2, fill=(90, 170, 90))
        self.disc(gx + 4, gy + 6, gx + 24, gy + 24, fill=(90, 170, 90))
        self.disc(gx - 26, gy + 10, gx - 8, gy + 26, fill=(120, 190, 110))
        # thermometer, right
        tx, ty = ax + 130, ay + 14
        self.box(tx, ty, tx + 12, ty + 56, fill=PAL["white"], outline=PAL["ink"], width=1)
        self.box(tx + 2, ty + 30, tx + 10, ty + 54, fill=PAL["red"])
        self.disc(tx - 4, ty + 52, tx + 16, ty + 72, fill=PAL["red"])
        self.seg([tx + 14, ty + 30, tx + 22, ty + 30], PAL["ink"])
        self.write((tx + 24, ty + 26), "1.5\u00b0C", load_face("sans_b", 9), PAL["red"])
        self.write((tx + 24, ty + 40), "LIMIT", load_face("sans_b", 9), PAL["ink"])
        self.badge(ax + 8, ay + 6, "ANTALYA", PAL["navy"], size=10)
        self.badge(ax + 8, by - 20, "DEAL DUE FRI", (180, 90, 27), size=9)
        self.badge(ax + 118, by - 20, "194 NATIONS", PAL["navy"], size=9)

    def scene_06(self, ax, ay, bx, by):
        """Riyadh tower hit: skyline, one tower burning, smoke."""
        self.box(ax, ay, bx, by, fill=(232, 222, 200))
        # dusk sky
        self.box(ax, ay, bx, ay + 30, fill=(250, 200, 120))
        self.disc(ax + 160, ay + 8, ax + 184, ay + 30, fill=(255, 240, 180))
        # towers
        for tx, top, rx, shade in [(16, 30, 46, (90, 100, 120)),
                                   (56, 18, 96, (70, 80, 100)),
                                   (106, 38, 136, (100, 110, 130)),
                                   (146, 26, 176, (80, 90, 110))]:
            self.box(ax + tx, ay + top, ax + rx, ay + 82, fill=shade)
        for tx in [16, 56, 106, 146]:
            for wy in range(3):
                for wx in range(2):
                    self.box(ax + tx + 5 + wx * 12, ay + 40 + wy * 12,
                             ax + tx + 9 + wx * 12, ay + 44 + wy * 12,
                             fill=(255, 220, 120))
        # blast on the tall tower
        self.burst(ax + 76, ay + 16, 12, (255, 170, 0))
        self.burst(ax + 76, ay + 16, 6, (255, 230, 120))
        self.disc(ax + 66, ay - 2, ax + 86, ay + 10, fill=(120, 120, 120))
        # incoming streak
        self.seg([(ax + 120, ay + 4), (ax + 82, ay + 14)], PAL["red"], width=2)
        # ground
        self.box(ax, ay + 82, bx, by, fill=(200, 180, 140))
        self.badge(ax + 8, ay + 6, "RIYADH", PAL["navy"], size=10)
        self.badge(ax + 106, by - 20, "NO INJURIES", (46, 125, 50), size=9)

    def scene_07(self, ax, ay, bx, by):
        """Berlin: Brandenburg Gate, EU and Ukraine flags."""
        self.box(ax, ay, bx, by, fill=(214, 226, 240))
        # Brandenburg Gate
        self.box(ax + 40, ay + 20, ax + 152, ay + 30, fill=(210, 195, 160))
        for i in range(6):
            cx = ax + 48 + i * 20
            self.box(cx, ay + 30, cx + 10, ay + 74, fill=(200, 185, 150))
        self.box(ax + 34, ay + 74, ax + 158, ay + 82, fill=(190, 175, 140))
        # quadriga hint on top
        self.poly([(ax + 88, ay + 20), (ax + 96, ay + 10), (ax + 104, ay + 20)],
                  fill=(120, 100, 70))
        self.box(ax + 84, ay + 12, ax + 108, ay + 20, fill=(120, 100, 70))
        # EU flag, left; Ukraine flag, right
        self.box(ax + 14, ay + 56, ax + 34, ay + 70, fill=(0, 51, 153))
        for i in range(6):
            ang = i * math.pi / 3
            self.disc(ax + 24 + 5 * math.cos(ang) - 1, ay + 63 + 4 * math.sin(ang) - 1,
                      ax + 24 + 5 * math.cos(ang) + 1, ay + 63 + 4 * math.sin(ang) + 1,
                      fill=(255, 215, 0))
        self.box(ax + 158, ay + 56, ax + 178, ay + 63, fill=(0, 91, 187))
        self.box(ax + 158, ay + 63, ax + 178, ay + 70, fill=(255, 213, 0))
        # ground
        self.box(ax, ay + 82, bx, by, fill=(170, 185, 165))
        self.badge(ax + 8, ay + 6, "BERLIN", PAL["navy"], size=10)
        self.badge(ax + 118, by - 20, "COALITION", (31, 78, 121), size=9)

    def scene_08(self, ax, ay, bx, by):
        """SCO forum at Purana Quila: red sandstone fort, arched gate, flags."""
        self.box(ax, ay, bx, by, fill=(250, 230, 200))
        # fort wall with crenellations
        self.box(ax + 10, ay + 30, ax + 182, ay + 82, fill=(176, 92, 60))
        for i in range(9):
            self.box(ax + 12 + i * 19, ay + 22, ax + 24 + i * 19, ay + 30,
                     fill=(176, 92, 60))
        # arched gate
        self.wedge(ax + 76, ay + 40, ax + 116, ay + 82, 180, 360, fill=(90, 50, 30))
        self.box(ax + 76, ay + 60, ax + 116, ay + 82, fill=(90, 50, 30))
        self.box(ax + 88, ay + 62, ax + 104, ay + 82, fill=(60, 35, 20))
        # domes on the wall
        self.wedge(ax + 24, ay + 12, ax + 52, ay + 32, 180, 360, fill=(220, 180, 120))
        self.wedge(ax + 140, ay + 12, ax + 168, ay + 32, 180, 360, fill=(220, 180, 120))
        # small flags along the top
        for i, col in enumerate([PAL["red"], (255, 153, 51), (0, 104, 71), PAL["green"]]):
            px = ax + 30 + i * 40
            self.seg([px, ay + 8, px, ay + 20], (90, 80, 70), width=2)
            self.box(px, ay + 8, px + 14, ay + 16, fill=col)
        # ground
        self.box(ax, ay + 82, bx, by, fill=(200, 170, 120))
        self.badge(ax + 8, ay + 6, "PURANA QUILA", PAL["navy"], size=10)
        self.badge(ax + 118, by - 20, "SCO FORUM", (106, 61, 154), size=9)

    def scene_09(self, ax, ay, bx, by):
        """Wellington Test: pitch, batsman, stumps, scoreboard NZ 243/5."""
        self.box(ax, ay, bx, by, fill=(90, 160, 80))
        # pitch strip
        self.box(ax + 60, ay + 8, ax + 132, by - 8, fill=(214, 190, 140))
        # crease lines
        self.seg([ax + 60, ay + 22, ax + 132, ay + 22], PAL["white"], width=2)
        self.seg([ax + 60, by - 22, ax + 132, by - 22], PAL["white"], width=2)
        # stumps, bottom
        for sx in [88, 94, 100]:
            self.seg([ax + sx, by - 30, ax + sx, by - 18], (255, 220, 120), width=2)
        self.seg([ax + 88, by - 30, ax + 100, by - 30], (255, 220, 120), width=2)
        # batsman
        self.figure(ax + 96, by - 34, 18, (0, 0, 0), skin=(200, 160, 120))
        self.seg([ax + 106, by - 40, ax + 118, by - 14], (160, 120, 60), width=4)
        # red ball in the air
        self.disc(ax + 122, ay + 20, ax + 130, ay + 28, fill=PAL["red"])
        # scoreboard
        board_face = load_face("sans_b", 10)
        self.box(ax + 8, ay + 8, ax + 56, ay + 26, fill=PAL["navy"])
        self.write((ax + 11, ay + 11), "NZ 243/5", board_face, PAL["white"])
        self.box(ax + 8, ay + 30, ax + 56, ay + 48, fill=PAL["navy"])
        self.write((ax + 11, ay + 33), "DAY 1", board_face, PAL["white"])
        # fielders
        self.figure(ax + 160, by - 20, 14, PAL["white"])
        self.figure(ax + 36, by - 20, 14, PAL["white"])

    def scene_10(self, ax, ay, bx, by):
        """FAA ground stop: departures board, all GROUNDED, plane on tarmac."""
        self.box(ax, ay, bx, by, fill=(20, 36, 61))
        # departures board
        self.box(ax + 8, ay + 6, ax + 110, ay + 30, fill=PAL["white"])
        self.write((ax + 12, ay + 11), "DEPARTURES", load_face("sans_b", 11), PAL["navy"])
        self.badge(ax + 116, ay + 6, "GROUND STOP", PAL["red"], size=9)
        for i, city in enumerate(["NEW YORK", "ATLANTA", "CHICAGO"]):
            yy = ay + 34 + i * 14
            city_face = load_face("sans_b", 9)
            self.write((ax + 10, yy), city, city_face, PAL["white"])
            self.box(ax + 82, yy - 1, ax + 128, yy + 10, fill=PAL["red"])
            self.write((ax + 85, yy), "GROUNDED", city_face, PAL["white"])
        # plane silhouette on the tarmac, right
        px, py = ax + 140, ay + 52
        self.disc(px, py - 6, px + 44, py + 6, fill=(220, 220, 220))
        self.poly([(px + 44, py - 2), (px + 56, py - 8), (px + 56, py + 2)],
                  fill=(220, 220, 220))
        self.poly([(px + 10, py - 6), (px + 18, py - 16), (px + 24, py - 6)],
                  fill=(220, 220, 220))
        self.poly([(px + 34, py - 6), (px + 40, py - 14), (px + 44, py - 6)],
                  fill=(220, 220, 220))
        self.box(ax, by - 12, bx, by, fill=(60, 60, 70))

    def scene_11(self, ax, ay, bx, by):
        """Tunisia qualify: pitch, goal, ball in the net, EQG 0-1 TUN."""
        self.box(ax, ay, bx, by, fill=(90, 160, 80))
        self.box(ax + 8, ay + 8, bx - 8, by - 8, outline=PAL["white"], width=2)
        mid = ax + (bx - ax) // 2
        self.seg([mid, ay + 8, mid, by - 8], PAL["white"], width=2)
        self.disc(ax + 78, ay + 30, ax + 112, ay + 56, outline=PAL["white"], width=2)
        # goal, left
        self.box(ax + 14, ay + 26, ax + 26, ay + 50, outline=PAL["white"], width=2)
        # ball in the net
        self.disc(ax + 16, ay + 38, ax + 26, ay + 48,
                  fill=PAL["white"], outline=PAL["ink"])
        # Tunisian flag on a pole, right
        self.seg([ax + 160, ay + 20, ax + 160, ay + 62], (200, 200, 200), width=2)
        self.box(ax + 162, ay + 20, ax + 184, ay + 36, fill=PAL["red"])
        self.disc(ax + 168, ay + 23, ax + 178, ay + 33, fill=PAL["white"])
        self.disc(ax + 171, ay + 26, ax + 175, ay + 30, fill=PAL["red"])
        # players
        self.figure(ax + 70, ay + 66, 14, (200, 30, 30))
        self.figure(ax + 130, ay + 66, 14, PAL["white"])
        # scoreboard
        score_face = load_face("sans_b", 10)
        self.box(ax + 104, ay + 8, bx - 6, ay + 26, fill=PAL["navy"])
        self.write((ax + 108, ay + 11), "EQG 0\u20131 TUN", score_face, PAL["white"])
        self.box(ax + 104, ay + 30, bx - 6, ay + 48, fill=PAL["navy"])
        self.write((ax + 108, ay + 33), "90+3\u2032 WINNER", score_face, PAL["white"])

    def scene_12(self, ax, ay, bx, by):
        """Bangladesh: family house on fire, Grameen Bank branch, smoke."""
        self.box(ax, ay, bx, by, fill=(214, 200, 170))
        # sky strip
        self.box(ax, ay, bx, ay + 22, fill=(220, 210, 190))
        # two-storey house, left
        self.box(ax + 16, ay + 30, ax + 84, ay + 78, fill=(240, 225, 200))
        self.poly([(ax + 12, ay + 30), (ax + 50, ay + 14), (ax + 88, ay + 30)],
                  fill=(160, 60, 40))
        self.box(ax + 24, ay + 56, ax + 38, ay + 78, fill=(90, 70, 50))
        self.box(ax + 58, ay + 40, ax + 74, ay + 54, fill=(140, 190, 230))
        self.box(ax + 24, ay + 40, ax + 40, ay + 54, fill=(140, 190, 230))
        # flames at the ground floor
        self.burst(ax + 50, ay + 72, 12, (255, 170, 0))
        self.burst(ax + 50, ay + 72, 6, (255, 230, 120))
        self.disc(ax + 44, ay + 46, ax + 60, ay + 58, fill=(120, 120, 120))
        # Grameen Bank branch, right
        self.box(ax + 108, ay + 34, ax + 178, ay + 78, fill=(60, 110, 70))
        for i in range(3):
            self.box(ax + 116 + i * 20, ay + 44, ax + 128 + i * 20, ay + 60,
                     fill=(200, 230, 200))
        self.write((ax + 112, ay + 66), "GRAMEEN BANK", load_face("sans_b", 8),
                   PAL["white"])
        # ground
        self.box(ax, ay + 78, bx, by, fill=(180, 160, 120))
        self.badge(ax + 8, ay + 6, "CHATTOGRAM", PAL["navy"], size=10)
        self.badge(ax + 96, by - 20, "72 BRANCHES HIT", PAL["red"], size=9)

    def scene_13(self, ax, ay, bx, by):
        """Hagia Sophia: great dome above, cleared tunnel below."""
        self.box(ax, ay, bx, by, fill=(232, 226, 210))
        # dome
        self.wedge(ax + 62, ay + 6, ax + 130, ay + 52, 180, 360, fill=(190, 150, 90))
        self.box(ax + 92, ay + 0, ax + 100, ay + 10, fill=(190, 150, 90))
        self.disc(ax + 93, ay - 4, ax + 99, ay + 2, fill=PAL["gold"])
        # arches
        for i in range(3):
            self.wedge(ax + 56 + i * 26, ay + 44, ax + 78 + i * 26, ay + 64,
                       180, 360, outline=(120, 100, 70), width=2)
        self.box(ax + 52, ay + 52, ax + 140, ay + 60, fill=(170, 140, 100))
        # ground line
        self.box(ax, ay + 60, bx, ay + 64, fill=(120, 100, 70))
        # tunnel below ground
        self.box(ax + 30, ay + 68, ax + 162, ay + 86, fill=(60, 50, 40))
        self.wedge(ax + 30, ay + 64, ax + 162, ay + 86, 180, 360, fill=(90, 75, 60))
        # lantern light in the tunnel
        self.disc(ax + 88, ay + 70, ax + 104, ay + 86, fill=(255, 220, 120))
        self.disc(ax + 92, ay + 74, ax + 100, ay + 82, fill=(255, 240, 180))
        # cleared rubble piles at the sides
        self.poly([(ax + 30, ay + 86), (ax + 44, ay + 74), (ax + 58, ay + 86)],
                  fill=(140, 120, 90))
        self.poly([(ax + 134, ay + 86), (ax + 148, ay + 74), (ax + 162, ay + 86)],
                  fill=(140, 120, 90))
        self.badge(ax + 8, ay + 6, "ISTANBUL", PAL["navy"], size=10)
        self.badge(ax + 108, by - 20, "1,600 YEARS", (31, 78, 121), size=9)

    # -- cards, map, and page furniture --------------------------------
    def card(self, num, x, y, w, h, big):
        story = STORIES[num - 1]
        ink = self.region_ink(story["region"])
        self.box(x, y, x + w, y + h, fill=PAL["card"], outline=PAL["rule"], width=1)
        art_h = 118 if big else 88
        SCENES[num](self, x + 1, y + 1, x + w - 1, y + 1 + art_h)
        self.seg([x, y + 1 + art_h, x + w, y + 1 + art_h], PAL["rule"])
        # number circle + kicker
        cx, cy = x + 14, y + art_h + 16
        self.disc(cx - 9, cy - 9, cx + 9, cy + 9, fill=ink)
        num_face = load_face("sans_b", 11)
        tw = self.measure(str(num), num_face)
        self.write((cx - tw / 2, cy - 7), str(num), num_face, PAL["white"])
        kick_face = load_face("sans_b", 11 if big else 9)
        self.write((x + 28, y + art_h + 9),
                   f"{story['region']} \u00b7 {story['topic']}", kick_face, ink)
        # headline, bold serif, two lines (shrink the face until it fits)
        size = 20 if big else 14
        while True:
            head_face = load_face("serif_b", size)
            head_lines = self.split_lines(story["head"], head_face, w - 16)
            if len(head_lines) <= 2 or size <= 11:
                break
            size -= 1
        hy = y + art_h + 28
        for i, line in enumerate(head_lines[:2]):
            self.write((x + 8, hy + i * (size + 2)), line, head_face, PAL["ink"])
        # deck, two lines (shrink the face until it fits)
        dsize = 12 if big else 10
        while True:
            deck_face = load_face("sans", dsize)
            deck_lines = self.split_lines(story["deck"], deck_face, w - 16)
            if len(deck_lines) <= 2 or dsize <= 8:
                break
            dsize -= 1
        dy = hy + 2 * (size + 2) + 2
        for i, line in enumerate(deck_lines[:2]):
            self.write((x + 8, dy + i * (dsize + 3)), line, deck_face, PAL["deck"])

    def project(self, lon, lat, mx0, my0, mw, mh):
        return (mx0 + (lon + 180) / 360 * mw,
                my0 + (84 - lat) / 142 * mh)

    def world_map(self, mx0, my0, mw, mh):
        self.box(mx0, my0, mx0 + mw, my0 + mh,
                 fill=(207, 227, 238), outline=PAL["rule"], width=1)
        for poly in LAND:
            pts = [self.project(lon, lat, mx0, my0, mw, mh) for lon, lat in poly]
            self.poly(pts, fill=(232, 220, 192), outline=(180, 165, 130))
        # pins, numbered, coloured by continent
        pin_face = load_face("sans_b", 8)
        for pin in PINS:
            px, py = self.project(pin["lon"], pin["lat"], mx0, my0, mw, mh)
            col = self.region_ink(pin["region"])
            self.disc(px - 7, py - 7, px + 7, py + 7,
                      fill=col, outline=PAL["white"], width=1)
            tw = self.measure(str(pin["n"]), pin_face)
            self.write((px - tw / 2, py - 5), str(pin["n"]), pin_face, PAL["white"])

    def legend_row(self, x, y):
        face = load_face("sans_b", 9)
        cx = x
        for name, colour in LEGEND:
            self.disc(cx, y, cx + 9, y + 9, fill=PAL[colour])
            self.write((cx + 12, y - 1), name, face, PAL["ink"])
            cx += 12 + self.measure(name, face) + 8

    def briefs(self, x0, y0, w, h):
        num_face = load_face("sans_b", 8)
        text_face = load_face("sans", 10)
        col_w = (w - 10) // 2
        rows = 15
        rh = h / rows
        for idx, item in enumerate(BRIEFS):
            col_i = 0 if idx < 15 else 1
            row = idx if idx < 15 else idx - 15
            cx = x0 + col_i * (col_w + 10)
            cy = y0 + row * rh + rh / 2
            col = PAL[BRIEF_INK.get(item["place"], "grey")]
            self.disc(cx, cy - 6, cx + 12, cy + 6, fill=col)
            tw = self.measure(str(item["n"]), num_face)
            self.write((cx + 6 - tw / 2, cy - 5), str(item["n"]), num_face,
                       PAL["white"])
            self.write((cx + 16, cy - 5),
                       f"{item['place']}: {item['text']}", text_face, PAL["ink"])

    def masthead(self):
        self.box(8, 8, PAGE_W - 9, 122, fill=PAL["navy"])
        face = load_face("sans_b", 13)
        self.write((16, 16), "THE DAY IN WORLD NEWS", face, PAL["gold"])
        right = "42 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM FRIDAY"
        tw = self.measure(right, face)
        self.write((PAGE_W - 16 - tw, 16), right, face, PAL["white"])
        date_face = self.best_fit("Friday 20 November 2026", "serif_b", 56,
                                  PAGE_W - 40)
        self.write((16, 42), "Friday 20 November 2026", date_face, PAL["white"])
        self.seg([8, 122, PAGE_W - 9, 122], PAL["gold"], width=3)

    def bottom_band(self):
        by = 766
        head_face = load_face("sans_b", 13)
        self.write((16, by), "WHERE IT HAPPENED", head_face, PAL["red"])
        self.seg([16, by + 20, 440, by + 20], PAL["ink"], width=2)
        self.write((452, by), "ALSO ON FRIDAY 20 NOVEMBER", head_face, PAL["red"])
        self.seg([452, by + 20, 1008, by + 20], PAL["ink"], width=2)
        self.world_map(16, 792, 424, 166)
        self.legend_row(16, 964)
        self.briefs(452, 792, 556, 196)

    def footer(self):
        self.seg([16, 988, 1008, 988], PAL["ink"], width=2)
        foot_face = load_face("sans", 10)
        footer = ("Every story happened or was first reported on Friday "
                  "20 November 2026; disputed claims are attributed. Sources: "
                  "AP, Reuters, AFP, BBC, Al Jazeera, UN News. Original drawings.")
        self.write((16, 996), footer, foot_face, PAL["deck"])

    def frame(self):
        self.box(4, 4, PAGE_W - 5, PAGE_H - 5, outline=PAL["navy"], width=3)

    def assemble(self):
        # Paint order differs from a top-down pass on purpose: the sections
        # never overlap, so footer, bottom band, cards, masthead and frame
        # can be laid down in any order with the same result. One exception
        # the overlap check caught: card 13's dome finial reaches four
        # pixels above its own card, onto card 8's bottom edge, so the
        # middle row must be painted before the bottom row.
        self.footer()
        self.bottom_band()
        for num in range(1, 4):
            self.card(num, 16 + (num - 1) * 328, 130, 320, 232, big=True)
        for num in range(4, 9):
            self.card(num, 16 + (num - 4) * 200, 370, 192, 190, big=False)
        for num in range(9, 14):
            self.card(num, 16 + (num - 9) * 200, 560, 192, 190, big=False)
        self.masthead()
        self.frame()
        self.img.save(TARGET, format="PNG", optimize=True)
        return TARGET


SCENES = {
    1: FrontPage.scene_01, 2: FrontPage.scene_02, 3: FrontPage.scene_03,
    4: FrontPage.scene_04, 5: FrontPage.scene_05, 6: FrontPage.scene_06,
    7: FrontPage.scene_07, 8: FrontPage.scene_08, 9: FrontPage.scene_09,
    10: FrontPage.scene_10, 11: FrontPage.scene_11, 12: FrontPage.scene_12,
    13: FrontPage.scene_13,
}


def main():
    page = FrontPage()
    path = page.assemble()
    print(path, os.path.getsize(path))


if __name__ == "__main__":
    main()
