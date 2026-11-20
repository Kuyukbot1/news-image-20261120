#!/usr/bin/env python3
"""Draw the news-image-20261120 front page: one 1024x1024 PNG.

Friday 20 November 2026: 42 stories, 6 continents, one front page and a map.
All stories come from RESEARCH_20NOV.md (verified 20 Nov 2026). Nothing invented.
Deterministic: no randomness, no time, fixed PNG settings.
Layout engine adapted from the 19 Nov entry; all 13 illustrations are new,
drawn for today's stories.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (247, 241, 227)      # cream paper
INK = (26, 26, 26)
NAVY = (20, 36, 61)
GOLD = (201, 162, 39)
RED = (179, 35, 42)
BLUE = (31, 78, 121)
ORANGE = (180, 90, 27)
GREEN = (46, 125, 50)
PURPLE = (106, 61, 154)
TEAL = (15, 118, 110)
GREY = (107, 114, 128)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    """Wrap text to fit max_w; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(d, text, path, max_size, max_w, min_size=8):
    """Largest font size (<= max_size) at which text fits max_w."""
    size = max_size
    while size > min_size:
        f = font(path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, min_size)


def kicker_color(region):
    return {
        "AMERICAS": RED, "UNITED STATES": RED, "EUROPE": BLUE,
        "MIDDLE EAST": ORANGE, "AFRICA": GREEN, "ASIA": PURPLE,
        "OCEANIA": TEAL, "GLOBAL": GREY, "VATICAN": BLUE,
    }[region]


# ---------------------------------------------------------------- data
# (region, topic, headline, deck) -- all from RESEARCH_20NOV.md
FEATURES = [
    ("ASIA", "DIPLOMACY",
     "Trump, Xi and Putin hail \u2018peace declaration\u2019",
     "After the first trilateral, the three call for UN reform and nuclear-risk talks."),
    ("ASIA", "WEATHER",
     "Cyclone Akvan makes landfall in east India",
     "Storm crosses near Gopalpur by noon; 3 lakh evacuated, 423 rescue teams out."),
    ("EUROPE", "UKRAINE WAR",
     "Russian strikes hit Kyiv; embassies damaged",
     "One killed as drones hit the capital; Putin vows payback for bridge strikes."),
    ("GLOBAL", "MARKETS",
     "Anthropic closes up 17% after wild debut",
     "ANT ends day one at $97.17 after opening at $111.50; the offering closes today."),
    ("GLOBAL", "CLIMATE",
     "COP31 closes today with deal still unwritten",
     "Ministers race the Friday deadline over fossil fuels and $120bn finance."),
    ("MIDDLE EAST", "IRAN WAR",
     "Houthi strike hits Riyadh tower in escalation",
     "Saudi reports damage, no injuries; Iran has hit 18 ships this month, monitors say."),
    ("EUROPE", "DIPLOMACY",
     "Allies meet in Berlin after Shenzhen talks",
     "Kushner says Europe is united and sees a \u2018real desire for peace\u2019 on Ukraine."),
    ("ASIA", "DIPLOMACY",
     "Modi opens first SCO dialogue forum in Delhi",
     "Forum opens at Purana Quila; Pakistan sends a minister to Delhi."),
    ("OCEANIA", "SPORT",
     "Nicholls century lifts New Zealand in Test",
     "Hosts reach 243 for five on day one against India; Phillips makes 94."),
    ("AMERICAS", "AVIATION",
     "FAA halts US departures after system failure",
     "Duffy says no sign of a hack as officials probe a router fault."),
    ("AFRICA", "SPORT",
     "Tunisia book World Cup place with late winner",
     "Ben Romdhane strikes in stoppage time; eight qualifiers, no goals conceded."),
    ("ASIA", "POLITICS",
     "Bangladesh lockdown turns violent; home torched",
     "Two ruling-party men killed; 72 Grameen Bank branches attacked in ten days."),
    ("GLOBAL", "CULTURE",
     "Hagia Sophia\u2019s hidden tunnels explored at last",
     "Archaeologists clear 3,000 tons of debris to reach Roman passages."),
]

# (number, country, text) -- all from RESEARCH_20NOV.md
ALSO_ON = [
    (14, "US", "Senate GOP rejects Iran war-powers curb"),
    (15, "Iran", "ministry slams US bio-weapons claim"),
    (16, "US", "Trump won't rush Iran decision"),
    (17, "Yemen", "Houthis confirm Riyadh tower strike"),
    (18, "Russia", "Putin invites EU leaders to Moscow"),
    (19, "Ukraine", "probe finds Russia used chemical arms"),
    (20, "South Korea", "court sends ex-PM Han case back"),
    (21, "US", "Dow falls 997 pts, S&P down 1.8%"),
    (22, "India", "Sensex surges ~1,000 pts to 83,021"),
    (23, "India", "firms announce $20.5bn US investment"),
    (24, "India", "NEET leak charges framed vs 14"),
    (25, "India", "11 states/UTs reach full literacy"),
    (26, "India", "Shah: Kashmir free of local recruits"),
    (27, "US", "court orders summonses for Doval, Goel"),
    (28, "Australia", "sanctions Israeli settlers"),
    (29, "Bulgaria", "sunken tanker hit by projectiles"),
    (30, "Fiji", "disaster declared over El Ni\u00f1o drought"),
    (31, "Slovenia", "border warning for South China Sea"),
    (32, "Hong Kong", "Rakshitha stuns Olympic champion"),
    (33, "US", "oldest Pearl Harbor survivor dies at 106"),
    (34, "US", "TSA finds cocaine worth $27,750 in tin"),
    (35, "Global", "World Children's Day marked today"),
    (36, "US", "Games gold medallist loses arm in crash"),
    (37, "India", "Modi asks industry 'Where are jobs?'"),
    (38, "India", "EPFO approves systematic PF withdrawal"),
    (39, "India", "60 days of fuel held in Hormuz crisis"),
    (40, "Pakistan", "minister to lead Delhi SCO delegation"),
    (41, "Global", "NASA probes 'potato chip' Mars shapes"),
    (42, "Europe", "Germany rout Slovakia 6-0; NI win 1-0"),
]

# map pins: (lon, lat) per feature number, nudged where the cluster is tight
PINS = {
    1: (114, 22.5), 2: (85, 19.5), 3: (30.5, 50.4), 4: (-74, 40.7),
    5: (35, 36), 6: (46.7, 24.7), 7: (13.4, 52.5), 8: (77.2, 28.6),
    9: (168, -41.3), 10: (-87.6, 41.9), 11: (10.2, 36.8), 12: (97, 26),
    13: (23, 42),
}
# Nudges (map is 424 px wide, pins r=7): 5 Antalya east to (35,36) so it
# clears 3 Kyiv and 13; 9 Wellington west so it fits inside the map edge;
# 10 = Chicago O'Hare, a major hub, so it clears 4 New York; 12 Chattogram
# north-east to (97,26) so it clears 2 Gopalpur; 13 Istanbul west to (23,42)
# so it clears 5 Antalya.
PIN_REGION = {1: "ASIA", 2: "ASIA", 3: "EUROPE", 4: "GLOBAL",
              5: "GLOBAL", 6: "MIDDLE EAST", 7: "EUROPE", 8: "ASIA",
              9: "OCEANIA", 10: "AMERICAS", 11: "AFRICA", 12: "ASIA",
              13: "GLOBAL"}

# rough flat continents, (lon, lat) polygons
CONTINENTS = [
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
    # Asia (drawn before Europe so Europe overlaps it)
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

# ---------------------------------------------------------------- helpers
def chip(d, x, y, text, bg, fg=(255, 255, 255), size=11, pad=5):
    f = font(SANS_B, size)
    w = d.textlength(text, font=f) + pad * 2
    d.rounded_rectangle([x, y, x + w, y + size + pad], radius=3, fill=bg)
    d.text((x + pad, y + 2), text, font=f, fill=fg)
    return w


def flag_us(d, x, y, w, h):
    for i in range(13):
        d.rectangle([x, y + i * h / 13, x + w, y + (i + 1) * h / 13],
                    fill=RED if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y, x + w * 0.4, y + h * 7 / 13], fill=NAVY)
    for r in range(3):
        for c in range(4):
            d.ellipse([x + 3 + c * w * 0.09, y + 2 + r * h * 0.18,
                       x + 6 + c * w * 0.09, y + 5 + r * h * 0.18],
                      fill=(255, 255, 255))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy = x + w * 0.2, y + h * 0.28
    d.polygon([(cx, cy - 5), (cx + 2, cy - 1), (cx + 6, cy - 1), (cx + 3, cy + 2),
               (cx + 4, cy + 6), (cx, cy + 3), (cx - 4, cy + 6), (cx - 3, cy + 2),
               (cx - 6, cy - 1), (cx - 2, cy - 1)], fill=(255, 222, 0))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 43, 30))


def flagpole(d, x, y, h, flagfn, fw=34, fh=22):
    d.line([x, y, x, y - h], fill=(90, 80, 70), width=3)
    d.ellipse([x - 2, y - h - 3, x + 2, y - h + 1], fill=GOLD)
    flagfn(d, x + 2, y - h + 2, fw, fh)


def person(d, x, y, s, suit, skin=(232, 190, 150), hair=(40, 30, 25)):
    d.ellipse([x - s * 0.32, y - s * 1.05, x + s * 0.32, y - s * 0.42],
              fill=skin)
    d.pieslice([x - s * 0.32, y - s * 1.08, x + s * 0.32, y - s * 0.55],
               180, 360, fill=hair)
    d.polygon([(x - s * 0.5, y), (x + s * 0.5, y), (x + s * 0.42, y - s * 0.45),
               (x - s * 0.42, y - s * 0.45)], fill=suit)
    d.polygon([(x - s * 0.08, y - s * 0.42), (x + s * 0.08, y - s * 0.42),
               (x, y - s * 0.1)], fill=(255, 255, 255))


def starburst(d, cx, cy, r, color):
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color)


def mine(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 40, 45))
    for i in range(8):
        ang = i * math.pi / 4
        x2 = cx + (r + 4) * math.cos(ang)
        y2 = cy + (r + 4) * math.sin(ang)
        d.line([cx, cy, x2, y2], fill=(40, 40, 45), width=2)
    d.ellipse([cx - r * 0.4, cy - r * 0.4, cx + r * 0.4, cy + r * 0.4],
              fill=(90, 90, 100))

# ---------------------------------------------------------------- illustrations
def ill_1(d, x0, y0, x1, y1):
    """Trilateral: three flags, three leaders, the peace declaration."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 232, 240))
    d.rectangle([x0, y0, x1, y0 + 46], fill=(30, 48, 78))
    fap = font(SANS_B, 11)
    atxt = "APEC \u00b7 SHENZHEN"
    d.text((x0 + (x1 - x0 - d.textlength(atxt, font=fap)) / 2, y0 + 16),
           atxt, font=fap, fill=GOLD)
    for i, fn in enumerate([flag_us, flag_cn, flag_ru]):
        fx = x0 + 52 + i * 108
        flagpole(d, fx, y0 + 82, 40, fn, 44, 28)
    # round table
    d.ellipse([x0 + 60, y0 + 82, x1 - 60, y0 + 106], fill=(120, 82, 50))
    d.ellipse([x0 + 60, y0 + 78, x1 - 60, y0 + 98], fill=(150, 105, 65))
    person(d, x0 + 96, y0 + 80, 22, (30, 40, 60))
    person(d, x0 + 160, y0 + 80, 22, (140, 30, 30))
    person(d, x0 + 224, y0 + 80, 22, (40, 60, 90))
    # declaration paper on the table
    d.rectangle([x0 + 128, y0 + 88, x0 + 192, y0 + 116], fill=(255, 255, 255),
                outline=INK)
    for i in range(3):
        d.line([x0 + 133, y0 + 93 + i * 5, x0 + 187, y0 + 93 + i * 5],
               fill=(120, 120, 120), width=1)
    d.ellipse([x0 + 182, y0 + 106, x0 + 190, y0 + 114], fill=RED, outline=GOLD)
    chip(d, x0 + 8, y1 - 20, "DECLARATION TOWARDS PEACE", NAVY, size=9)


def ill_2(d, x0, y0, x1, y1):
    """Cyclone Akvan: spiral over the Bay of Bengal, coast, shelters."""
    d.rectangle([x0, y0, x1, y1], fill=(150, 190, 220))
    # India coast, right
    d.polygon([(x0 + 150, y0), (x1, y0), (x1, y1), (x0 + 168, y1),
               (x0 + 158, y0 + 50), (x0 + 148, y0 + 22)], fill=(214, 190, 140))
    # spiral bands
    cx, cy = x0 + 78, y0 + 42
    for r, col in [(36, (255, 255, 255)), (28, (220, 235, 245)),
                   (20, (255, 255, 255)), (12, (220, 235, 245))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], 30, 310, fill=col, width=6)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255))
    # storm track arrow toward the coast
    d.line([(cx + 30, cy + 20), (x0 + 138, y0 + 58)], fill=RED, width=3)
    d.polygon([(x0 + 138, y0 + 58), (x0 + 126, y0 + 52), (x0 + 130, y0 + 64)],
              fill=RED)
    # shelter bus on the coast road
    d.rectangle([x0 + 168, y0 + 66, x0 + 196, y0 + 82], fill=(240, 180, 40))
    for wx in range(3):
        d.rectangle([x0 + 172 + wx * 8, y0 + 69, x0 + 178 + wx * 8, y0 + 75],
                    fill=(180, 220, 240))
    d.ellipse([x0 + 172, y0 + 80, x0 + 178, y0 + 86], fill=INK)
    d.ellipse([x0 + 186, y0 + 80, x0 + 192, y0 + 86], fill=INK)
    # rain streaks
    for i in range(5):
        d.line([x0 + 14 + i * 12, y0 + 68, x0 + 10 + i * 12, y0 + 80],
               fill=(90, 130, 170), width=2)
    chip(d, x0 + 8, y0 + 6, "BAY OF BENGAL", NAVY, size=10)
    chip(d, x0 + 92, y1 - 20, "3 LAKH EVACUATED", (180, 90, 27), size=9)


def ill_3(d, x0, y0, x1, y1):
    """Kyiv under drone attack: night skyline, drone, blast, embassy flags."""
    d.rectangle([x0, y0, x1, y1], fill=(18, 24, 44))
    # stars
    for sx, sy in [(20, 12), (90, 8), (180, 16), (250, 10), (140, 6)]:
        d.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                  fill=(255, 255, 255))
    # skyline
    for bx, bw, bh in [(8, 30, 40), (44, 24, 55), (74, 34, 34), (200, 28, 48),
                       (234, 30, 36), (270, 26, 52)]:
        d.rectangle([x0 + bx, y1 - bh - 18, x0 + bx + bw, y1 - 18],
                    fill=(45, 55, 80))
        for wy in range(2):
            for wx in range(2):
                d.rectangle([x0 + bx + 5 + wx * 11, y1 - bh - 12 + wy * 11,
                             x0 + bx + 9 + wx * 11, y1 - bh - 8 + wy * 11],
                            fill=(255, 220, 120))
    # drone, top right
    dx, dy = x0 + 180, y0 + 22
    d.rectangle([dx, dy, dx + 26, dy + 8], fill=(200, 200, 200))
    d.line([dx - 8, dy - 2, dx + 34, dy - 2], fill=(220, 220, 220), width=2)
    d.ellipse([dx - 12, dy - 6, dx - 2, dy + 2], fill=(160, 160, 160))
    d.ellipse([dx + 28, dy - 6, dx + 38, dy + 2], fill=(160, 160, 160))
    # blast over a building
    starburst(d, x0 + 130, y0 + 52, 14, (255, 170, 0))
    starburst(d, x0 + 130, y0 + 52, 7, (255, 230, 120))
    d.ellipse([x0 + 120, y0 + 30, x0 + 140, y0 + 42], fill=(120, 120, 120))
    # street
    d.rectangle([x0, y1 - 18, x1, y1], fill=(30, 32, 40))
    # two embassy flags on small poles, bottom left
    def flag_nl(fx, fy):
        d.rectangle([fx, fy, fx + 22, fy + 5], fill=RED)
        d.rectangle([fx, fy + 5, fx + 22, fy + 10], fill=(255, 255, 255))
        d.rectangle([fx, fy + 10, fx + 22, fy + 15], fill=(30, 60, 160))
    def flag_at(fx, fy):
        d.rectangle([fx, fy, fx + 22, fy + 5], fill=RED)
        d.rectangle([fx, fy + 5, fx + 22, fy + 10], fill=(255, 255, 255))
        d.rectangle([fx, fy + 10, fx + 22, fy + 15], fill=RED)
    d.line([x0 + 120, y1 - 18, x0 + 120, y1 - 34], fill=(200, 200, 200), width=2)
    flag_nl(x0 + 122, y1 - 34)
    d.line([x0 + 152, y1 - 18, x0 + 152, y1 - 34], fill=(200, 200, 200), width=2)
    flag_at(x0 + 154, y1 - 34)
    chip(d, x0 + 8, y0 + 6, "KYIV", NAVY, size=10)
    chip(d, x0 + 8, y1 - 20, "1 KILLED", RED, size=10)


def ill_4(d, x0, y0, x1, y1):
    """Anthropic debut: dark board, chart up then down, $97.17 close."""
    d.rectangle([x0, y0, x1, y1], fill=(14, 22, 32))
    for gy in range(4):
        d.line([x0 + 8, y0 + 14 + gy * 18, x1 - 8, y0 + 14 + gy * 18],
               fill=(40, 55, 75), width=1)
    # rocketing green line that then falls back
    d.line([(x0 + 12, y0 + 62), (x0 + 50, y0 + 54), (x0 + 88, y0 + 34),
            (x0 + 126, y0 + 10), (x0 + 150, y0 + 26), (x0 + 172, y0 + 40)],
           fill=(80, 220, 120), width=3)
    d.polygon([(x0 + 126, y0 + 10), (x0 + 114, y0 + 8), (x0 + 124, y0 + 22)],
              fill=(80, 220, 120))
    # bars
    for i, hgt in enumerate([8, 14, 20, 30]):
        d.rectangle([x0 + 20 + i * 14, y0 + 78 - hgt, x0 + 30 + i * 14, y0 + 78],
                    fill=(60, 120, 180))
    f = font(SANS_B, 20)
    d.text((x0 + 96, y0 + 50), "$97.17", font=f, fill=(255, 255, 255))
    f2 = font(SANS_B, 10)
    d.text((x0 + 96, y0 + 72), "+17% DAY ONE", font=f2, fill=(80, 220, 120))
    chip(d, x0 + 8, y0 + 6, "ANT \u00b7 NASDAQ", (200, 120, 30), size=10)


def ill_5(d, x0, y0, x1, y1):
    """COP31: globe, thermometer at 1.5C, Antalya deadline."""
    d.rectangle([x0, y0, x1, y1], fill=(222, 228, 236))
    # globe, left
    gx, gy, gr = x0 + 52, y0 + 44, 34
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(90, 150, 210),
              outline=(40, 80, 140), width=2)
    d.ellipse([gx - 18, gy - 22, gx + 2, gy - 2], fill=(90, 170, 90))
    d.ellipse([gx + 4, gy + 6, gx + 24, gy + 24], fill=(90, 170, 90))
    d.ellipse([gx - 26, gy + 10, gx - 8, gy + 26], fill=(120, 190, 110))
    # thermometer, right
    tx, ty = x0 + 130, y0 + 14
    d.rectangle([tx, ty, tx + 12, ty + 56], fill=(255, 255, 255),
                outline=INK, width=1)
    d.rectangle([tx + 2, ty + 30, tx + 10, ty + 54], fill=RED)
    d.ellipse([tx - 4, ty + 52, tx + 16, ty + 72], fill=RED)
    d.line([tx + 14, ty + 30, tx + 22, ty + 30], fill=INK, width=1)
    f = font(SANS_B, 9)
    d.text((tx + 24, ty + 26), "1.5\u00b0C", font=f, fill=RED)
    d.text((tx + 24, ty + 40), "LIMIT", font=f, fill=INK)
    chip(d, x0 + 8, y0 + 6, "ANTALYA", NAVY, size=10)
    chip(d, x0 + 8, y1 - 20, "DEAL DUE FRI", (180, 90, 27), size=9)
    chip(d, x0 + 118, y1 - 20, "194 NATIONS", NAVY, size=9)


def ill_6(d, x0, y0, x1, y1):
    """Riyadh tower hit: skyline, one tower burning, smoke."""
    d.rectangle([x0, y0, x1, y1], fill=(232, 222, 200))
    # dusk sky
    d.rectangle([x0, y0, x1, y0 + 30], fill=(250, 200, 120))
    d.ellipse([x0 + 160, y0 + 8, x0 + 184, y0 + 30], fill=(255, 240, 180))
    # towers
    d.rectangle([x0 + 16, y0 + 30, x0 + 46, y0 + 82], fill=(90, 100, 120))
    d.rectangle([x0 + 56, y0 + 18, x0 + 96, y0 + 82], fill=(70, 80, 100))
    d.rectangle([x0 + 106, y0 + 38, x0 + 136, y0 + 82], fill=(100, 110, 130))
    d.rectangle([x0 + 146, y0 + 26, x0 + 176, y0 + 82], fill=(80, 90, 110))
    for tx in [16, 56, 106, 146]:
        for wy in range(3):
            for wx in range(2):
                d.rectangle([x0 + tx + 5 + wx * 12, y0 + 40 + wy * 12,
                             x0 + tx + 9 + wx * 12, y0 + 44 + wy * 12],
                            fill=(255, 220, 120))
    # blast on the tall tower
    starburst(d, x0 + 76, y0 + 16, 12, (255, 170, 0))
    starburst(d, x0 + 76, y0 + 16, 6, (255, 230, 120))
    d.ellipse([x0 + 66, y0 - 2, x0 + 86, y0 + 10], fill=(120, 120, 120))
    # incoming streak
    d.line([(x0 + 120, y0 + 4), (x0 + 82, y0 + 14)], fill=RED, width=2)
    # ground
    d.rectangle([x0, y0 + 82, x1, y1], fill=(200, 180, 140))
    chip(d, x0 + 8, y0 + 6, "RIYADH", NAVY, size=10)
    chip(d, x0 + 106, y1 - 20, "NO INJURIES", (46, 125, 50), size=9)

def ill_7(d, x0, y0, x1, y1):
    """Berlin: Brandenburg Gate, EU and Ukraine flags."""
    d.rectangle([x0, y0, x1, y1], fill=(214, 226, 240))
    # Brandenburg Gate
    d.rectangle([x0 + 40, y0 + 20, x0 + 152, y0 + 30], fill=(210, 195, 160))
    for i in range(6):
        cx = x0 + 48 + i * 20
        d.rectangle([cx, y0 + 30, cx + 10, y0 + 74], fill=(200, 185, 150))
    d.rectangle([x0 + 34, y0 + 74, x0 + 158, y0 + 82], fill=(190, 175, 140))
    # quadriga hint on top
    d.polygon([(x0 + 88, y0 + 20), (x0 + 96, y0 + 10), (x0 + 104, y0 + 20)],
              fill=(120, 100, 70))
    d.rectangle([x0 + 84, y0 + 12, x0 + 108, y0 + 20], fill=(120, 100, 70))
    # EU flag, left; Ukraine flag, right
    d.rectangle([x0 + 14, y0 + 56, x0 + 34, y0 + 70], fill=(0, 51, 153))
    for i in range(6):
        ang = i * math.pi / 3
        d.ellipse([x0 + 24 + 5 * math.cos(ang) - 1, y0 + 63 + 4 * math.sin(ang) - 1,
                   x0 + 24 + 5 * math.cos(ang) + 1, y0 + 63 + 4 * math.sin(ang) + 1],
                  fill=(255, 215, 0))
    d.rectangle([x0 + 158, y0 + 56, x0 + 178, y0 + 63], fill=(0, 91, 187))
    d.rectangle([x0 + 158, y0 + 63, x0 + 178, y0 + 70], fill=(255, 213, 0))
    # ground
    d.rectangle([x0, y0 + 82, x1, y1], fill=(170, 185, 165))
    chip(d, x0 + 8, y0 + 6, "BERLIN", NAVY, size=10)
    chip(d, x0 + 118, y1 - 20, "COALITION", (31, 78, 121), size=9)


def ill_8(d, x0, y0, x1, y1):
    """SCO forum at Purana Quila: red sandstone fort, arched gate, flags."""
    d.rectangle([x0, y0, x1, y1], fill=(250, 230, 200))
    # fort wall with crenellations
    d.rectangle([x0 + 10, y0 + 30, x0 + 182, y0 + 82], fill=(176, 92, 60))
    for i in range(9):
        d.rectangle([x0 + 12 + i * 19, y0 + 22, x0 + 24 + i * 19, y0 + 30],
                    fill=(176, 92, 60))
    # arched gate
    d.pieslice([x0 + 76, y0 + 40, x0 + 116, y0 + 82], 180, 360, fill=(90, 50, 30))
    d.rectangle([x0 + 76, y0 + 60, x0 + 116, y0 + 82], fill=(90, 50, 30))
    d.rectangle([x0 + 88, y0 + 62, x0 + 104, y0 + 82], fill=(60, 35, 20))
    # domes on the wall
    d.pieslice([x0 + 24, y0 + 12, x0 + 52, y0 + 32], 180, 360, fill=(220, 180, 120))
    d.pieslice([x0 + 140, y0 + 12, x0 + 168, y0 + 32], 180, 360, fill=(220, 180, 120))
    # small flags along the top
    for i, col in enumerate([RED, (255, 153, 51), (0, 104, 71), GREEN]):
        px = x0 + 30 + i * 40
        d.line([px, y0 + 8, px, y0 + 20], fill=(90, 80, 70), width=2)
        d.rectangle([px, y0 + 8, px + 14, y0 + 16], fill=col)
    # ground
    d.rectangle([x0, y0 + 82, x1, y1], fill=(200, 170, 120))
    chip(d, x0 + 8, y0 + 6, "PURANA QUILA", NAVY, size=10)
    chip(d, x0 + 118, y1 - 20, "SCO FORUM", (106, 61, 154), size=9)


def ill_9(d, x0, y0, x1, y1):
    """Wellington Test: pitch, batsman, stumps, scoreboard NZ 243/5."""
    d.rectangle([x0, y0, x1, y1], fill=(90, 160, 80))
    # pitch strip
    d.rectangle([x0 + 60, y0 + 8, x0 + 132, y1 - 8], fill=(214, 190, 140))
    # crease lines
    d.line([x0 + 60, y0 + 22, x0 + 132, y0 + 22], fill=(255, 255, 255), width=2)
    d.line([x0 + 60, y1 - 22, x0 + 132, y1 - 22], fill=(255, 255, 255), width=2)
    # stumps, bottom
    for sx in [88, 94, 100]:
        d.line([x0 + sx, y1 - 30, x0 + sx, y1 - 18], fill=(255, 220, 120), width=2)
    d.line([x0 + 88, y1 - 30, x0 + 100, y1 - 30], fill=(255, 220, 120), width=2)
    # batsman
    person(d, x0 + 96, y1 - 34, 18, (0, 0, 0), skin=(200, 160, 120))
    d.line([x0 + 106, y1 - 40, x0 + 118, y1 - 14], fill=(160, 120, 60), width=4)
    # red ball in the air
    d.ellipse([x0 + 122, y0 + 20, x0 + 130, y0 + 28], fill=RED)
    # scoreboard
    f = font(SANS_B, 10)
    d.rectangle([x0 + 8, y0 + 8, x0 + 56, y0 + 26], fill=NAVY)
    d.text((x0 + 11, y0 + 11), "NZ 243/5", font=f, fill=(255, 255, 255))
    d.rectangle([x0 + 8, y0 + 30, x0 + 56, y0 + 48], fill=NAVY)
    d.text((x0 + 11, y0 + 33), "DAY 1", font=f, fill=(255, 255, 255))
    # fielders
    person(d, x0 + 160, y1 - 20, 14, (255, 255, 255))
    person(d, x0 + 36, y1 - 20, 14, (255, 255, 255))


def ill_10(d, x0, y0, x1, y1):
    """FAA ground stop: departures board, all GROUNDED, plane on tarmac."""
    d.rectangle([x0, y0, x1, y1], fill=(20, 36, 61))
    # departures board
    d.rectangle([x0 + 8, y0 + 6, x0 + 110, y0 + 30], fill=(255, 255, 255))
    f = font(SANS_B, 11)
    d.text((x0 + 12, y0 + 11), "DEPARTURES", font=f, fill=NAVY)
    chip(d, x0 + 116, y0 + 6, "GROUND STOP", RED, size=9)
    for i, city in enumerate(["NEW YORK", "ATLANTA", "CHICAGO"]):
        yy = y0 + 34 + i * 14
        f2 = font(SANS_B, 9)
        d.text((x0 + 10, yy), city, font=f2, fill=(255, 255, 255))
        d.rectangle([x0 + 82, yy - 1, x0 + 128, yy + 10], fill=RED)
        d.text((x0 + 85, yy), "GROUNDED", font=f2, fill=(255, 255, 255))
    # plane silhouette on the tarmac, right
    px, py = x0 + 140, y0 + 52
    d.ellipse([px, py - 6, px + 44, py + 6], fill=(220, 220, 220))
    d.polygon([(px + 44, py - 2), (px + 56, py - 8), (px + 56, py + 2)],
              fill=(220, 220, 220))
    d.polygon([(px + 10, py - 6), (px + 18, py - 16), (px + 24, py - 6)],
              fill=(220, 220, 220))
    d.polygon([(px + 34, py - 6), (px + 40, py - 14), (px + 44, py - 6)],
              fill=(220, 220, 220))
    d.rectangle([x0, y1 - 12, x1, y1], fill=(60, 60, 70))


def ill_11(d, x0, y0, x1, y1):
    """Tunisia qualify: pitch, goal, ball in the net, EQG 0-1 TUN."""
    d.rectangle([x0, y0, x1, y1], fill=(90, 160, 80))
    d.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], outline=(255, 255, 255), width=2)
    d.line([x0 + (x1 - x0) // 2, y0 + 8, x0 + (x1 - x0) // 2, y1 - 8],
           fill=(255, 255, 255), width=2)
    d.ellipse([x0 + 78, y0 + 30, x0 + 112, y0 + 56], outline=(255, 255, 255),
              width=2)
    # goal, left
    d.rectangle([x0 + 14, y0 + 26, x0 + 26, y0 + 50], outline=(255, 255, 255),
                width=2)
    # ball in the net
    d.ellipse([x0 + 16, y0 + 38, x0 + 26, y0 + 48], fill=(255, 255, 255),
              outline=INK)
    # Tunisian flag on a pole, right
    d.line([x0 + 160, y0 + 20, x0 + 160, y0 + 62], fill=(200, 200, 200), width=2)
    d.rectangle([x0 + 162, y0 + 20, x0 + 184, y0 + 36], fill=RED)
    d.ellipse([x0 + 168, y0 + 23, x0 + 178, y0 + 33], fill=(255, 255, 255))
    d.ellipse([x0 + 171, y0 + 26, x0 + 175, y0 + 30], fill=RED)
    # players
    person(d, x0 + 70, y0 + 66, 14, (200, 30, 30))
    person(d, x0 + 130, y0 + 66, 14, (255, 255, 255))
    # scoreboard
    f = font(SANS_B, 10)
    d.rectangle([x0 + 104, y0 + 8, x1 - 6, y0 + 26], fill=NAVY)
    d.text((x0 + 108, y0 + 11), "EQG 0\u20131 TUN", font=f, fill=(255, 255, 255))
    d.rectangle([x0 + 104, y0 + 30, x1 - 6, y0 + 48], fill=NAVY)
    d.text((x0 + 108, y0 + 33), "90+3\u2032 WINNER", font=f, fill=(255, 255, 255))


def ill_12(d, x0, y0, x1, y1):
    """Bangladesh: family house on fire, Grameen Bank branch, smoke."""
    d.rectangle([x0, y0, x1, y1], fill=(214, 200, 170))
    # sky strip
    d.rectangle([x0, y0, x1, y0 + 22], fill=(220, 210, 190))
    # two-storey house, left
    d.rectangle([x0 + 16, y0 + 30, x0 + 84, y0 + 78], fill=(240, 225, 200))
    d.polygon([(x0 + 12, y0 + 30), (x0 + 50, y0 + 14), (x0 + 88, y0 + 30)],
              fill=(160, 60, 40))
    d.rectangle([x0 + 24, y0 + 56, x0 + 38, y0 + 78], fill=(90, 70, 50))
    d.rectangle([x0 + 58, y0 + 40, x0 + 74, y0 + 54], fill=(140, 190, 230))
    d.rectangle([x0 + 24, y0 + 40, x0 + 40, y0 + 54], fill=(140, 190, 230))
    # flames at the ground floor
    starburst(d, x0 + 50, y0 + 72, 12, (255, 170, 0))
    starburst(d, x0 + 50, y0 + 72, 6, (255, 230, 120))
    d.ellipse([x0 + 44, y0 + 46, x0 + 60, y0 + 58], fill=(120, 120, 120))
    # Grameen Bank branch, right
    d.rectangle([x0 + 108, y0 + 34, x0 + 178, y0 + 78], fill=(60, 110, 70))
    for i in range(3):
        d.rectangle([x0 + 116 + i * 20, y0 + 44, x0 + 128 + i * 20, y0 + 60],
                    fill=(200, 230, 200))
    f = font(SANS_B, 8)
    d.text((x0 + 112, y0 + 66), "GRAMEEN BANK", font=f, fill=(255, 255, 255))
    # ground
    d.rectangle([x0, y0 + 78, x1, y1], fill=(180, 160, 120))
    chip(d, x0 + 8, y0 + 6, "CHATTOGRAM", NAVY, size=10)
    chip(d, x0 + 96, y1 - 20, "72 BRANCHES HIT", RED, size=9)


def ill_13(d, x0, y0, x1, y1):
    """Hagia Sophia: great dome above, cleared tunnel below."""
    d.rectangle([x0, y0, x1, y1], fill=(232, 226, 210))
    # dome
    d.pieslice([x0 + 62, y0 + 6, x0 + 130, y0 + 52], 180, 360,
               fill=(190, 150, 90))
    d.rectangle([x0 + 92, y0 + 0, x0 + 100, y0 + 10], fill=(190, 150, 90))
    d.ellipse([x0 + 93, y0 - 4, x0 + 99, y0 + 2], fill=GOLD)
    # arches
    for i in range(3):
        d.pieslice([x0 + 56 + i * 26, y0 + 44, x0 + 78 + i * 26, y0 + 64],
                   180, 360, outline=(120, 100, 70), width=2)
    d.rectangle([x0 + 52, y0 + 52, x0 + 140, y0 + 60], fill=(170, 140, 100))
    # ground line
    d.rectangle([x0, y0 + 60, x1, y0 + 64], fill=(120, 100, 70))
    # tunnel below ground
    d.rectangle([x0 + 30, y0 + 68, x0 + 162, y0 + 86], fill=(60, 50, 40))
    d.pieslice([x0 + 30, y0 + 64, x0 + 162, y0 + 86], 180, 360, fill=(90, 75, 60))
    # lantern light in the tunnel
    d.ellipse([x0 + 88, y0 + 70, x0 + 104, y0 + 86], fill=(255, 220, 120))
    d.ellipse([x0 + 92, y0 + 74, x0 + 100, y0 + 82], fill=(255, 240, 180))
    # cleared rubble piles at the sides
    d.polygon([(x0 + 30, y0 + 86), (x0 + 44, y0 + 74), (x0 + 58, y0 + 86)],
              fill=(140, 120, 90))
    d.polygon([(x0 + 134, y0 + 86), (x0 + 148, y0 + 74), (x0 + 162, y0 + 86)],
              fill=(140, 120, 90))
    chip(d, x0 + 8, y0 + 6, "ISTANBUL", NAVY, size=10)
    chip(d, x0 + 108, y1 - 20, "1,600 YEARS", (31, 78, 121), size=9)


ILLUSTRATIONS = {1: ill_1, 2: ill_2, 3: ill_3, 4: ill_4, 5: ill_5, 6: ill_6,
                 7: ill_7, 8: ill_8, 9: ill_9, 10: ill_10, 11: ill_11,
                 12: ill_12, 13: ill_13}

# ---------------------------------------------------------------- page build
def draw_card(d, num, x, y, w, h, large):
    region, topic, headline, deck = FEATURES[num - 1]
    col = kicker_color(region)
    d.rectangle([x, y, x + w, y + h], fill=(255, 252, 244),
                outline=(150, 140, 120), width=1)
    ill_h = 118 if large else 88
    ILLUSTRATIONS[num](d, x + 1, y + 1, x + w - 1, y + 1 + ill_h)
    d.line([x, y + 1 + ill_h, x + w, y + 1 + ill_h], fill=(150, 140, 120), width=1)
    # number circle + kicker
    cx, cy, r = x + 14, y + ill_h + 16, 9
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    fnum = font(SANS_B, 11)
    tw = d.textlength(str(num), font=fnum)
    d.text((cx - tw / 2, cy - 7), str(num), font=fnum, fill=(255, 255, 255))
    fk = font(SANS_B, 11 if large else 9)
    d.text((x + 28, y + ill_h + 9), f"{region} \u00b7 {topic}", font=fk, fill=col)
    # headline, bold serif, 2 lines (shrink font until it fits)
    hs = 20 if large else 14
    while True:
        hf = font(SERIF_B, hs)
        hl = wrap(d, headline, hf, w - 16)
        if len(hl) <= 2 or hs <= 11:
            break
        hs -= 1
    hy = y + ill_h + 28
    for i, line in enumerate(hl[:2]):
        d.text((x + 8, hy + i * (hs + 2)), line, font=hf, fill=INK)
    # deck, 2 lines (shrink font until it fits)
    ds = 12 if large else 10
    while True:
        df = font(SANS, ds)
        dl = wrap(d, deck, df, w - 16)
        if len(dl) <= 2 or ds <= 8:
            break
        ds -= 1
    dy = hy + 2 * (hs + 2) + 2
    for i, line in enumerate(dl[:2]):
        d.text((x + 8, dy + i * (ds + 3)), line, font=df, fill=(60, 55, 45))


def lonlat_to_xy(lon, lat, mx0, my0, mw, mh):
    x = mx0 + (lon + 180) / 360 * mw
    y = my0 + (84 - lat) / 142 * mh
    return x, y


def draw_map(d, mx0, my0, mw, mh):
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=(207, 227, 238),
                outline=(150, 140, 120), width=1)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, mx0, my0, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=(232, 220, 192), outline=(180, 165, 130))
    # pins, numbered, coloured by continent
    fnum = font(SANS_B, 8)
    for num in range(1, 14):
        lon, lat = PINS[num]
        px, py = lonlat_to_xy(lon, lat, mx0, my0, mw, mh)
        col = kicker_color(PIN_REGION[num])
        r = 7
        d.ellipse([px - r, py - r, px + r, py + r], fill=col,
                  outline=(255, 255, 255), width=1)
        tw = d.textlength(str(num), font=fnum)
        d.text((px - tw / 2, py - 5), str(num), font=fnum, fill=(255, 255, 255))


def draw_legend(d, x, y, w):
    items = [("Americas", RED), ("Europe", BLUE), ("Middle East", ORANGE),
             ("Africa", GREEN), ("Asia", PURPLE), ("Oceania", TEAL),
             ("Global", GREY)]
    f = font(SANS_B, 9)
    cx = x
    for name, col in items:
        d.ellipse([cx, y, cx + 9, y + 9], fill=col)
        d.text((cx + 12, y - 1), name, font=f, fill=INK)
        cx += 12 + d.textlength(name, font=f) + 8
    return cx


ALSO_COLORS = {
    "US": RED, "Iran": ORANGE, "Yemen": ORANGE, "Russia": BLUE,
    "Ukraine": BLUE, "South Korea": PURPLE, "India": PURPLE,
    "Australia": TEAL, "Bulgaria": BLUE, "Fiji": TEAL, "Slovenia": BLUE,
    "Hong Kong": PURPLE, "Pakistan": PURPLE, "Global": GREY, "Europe": BLUE,
}


def draw_also_on(d, x0, y0, w, h):
    fnum = font(SANS_B, 8)
    f = font(SANS, 10)
    col_w = (w - 10) // 2
    rows = 15
    rh = h / rows
    for idx, (num, country, text) in enumerate(ALSO_ON):
        col_i = 0 if idx < 15 else 1
        row = idx if idx < 15 else idx - 15
        cx = x0 + col_i * (col_w + 10)
        cy = y0 + row * rh + rh / 2
        col = ALSO_COLORS.get(country, GREY)
        d.ellipse([cx, cy - 6, cx + 12, cy + 6], fill=col)
        tw = d.textlength(str(num), font=fnum)
        d.text((cx + 6 - tw / 2, cy - 5), str(num), font=fnum,
               fill=(255, 255, 255))
        label = f"{country}: {text}"
        d.text((cx + 16, cy - 5), label, font=f, fill=INK)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # outer border
    d.rectangle([4, 4, W - 5, H - 5], outline=NAVY, width=3)

    # ---- masthead: navy band ----
    d.rectangle([8, 8, W - 9, 122], fill=NAVY)
    fk = font(SANS_B, 13)
    d.text((16, 16), "THE DAY IN WORLD NEWS", font=fk, fill=GOLD)
    right = "42 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM FRIDAY"
    tw = d.textlength(right, font=fk)
    d.text((W - 16 - tw, 16), right, font=fk, fill=(255, 255, 255))
    date_f = fit_font(d, "Friday 20 November 2026", SERIF_B, 56, W - 40)
    d.text((16, 42), "Friday 20 November 2026", font=date_f,
           fill=(255, 255, 255))
    d.line([8, 122, W - 9, 122], fill=GOLD, width=3)

    # ---- feature cards ----
    # row 1: 3 large cards
    y1, h1 = 130, 232
    for i in range(3):
        draw_card(d, i + 1, 16 + i * 328, y1, 320, h1, large=True)
    # rows 2-3: 5 small cards each
    for row, base in enumerate([4, 9]):
        y = 370 + row * 190
        for i in range(5):
            draw_card(d, base + i, 16 + i * 200, y, 192, 190, large=False)

    # ---- bottom band ----
    by = 766
    fh = font(SANS_B, 13)
    d.text((16, by), "WHERE IT HAPPENED", font=fh, fill=RED)
    d.line([16, by + 20, 440, by + 20], fill=INK, width=2)
    d.text((452, by), "ALSO ON FRIDAY 20 NOVEMBER", font=fh, fill=RED)
    d.line([452, by + 20, 1008, by + 20], fill=INK, width=2)
    draw_map(d, 16, 792, 424, 166)
    draw_legend(d, 16, 964, 424)
    draw_also_on(d, 452, 792, 556, 196)

    # ---- footer ----
    d.line([16, 988, 1008, 988], fill=INK, width=2)
    ff = font(SANS, 10)
    footer = ("Every story happened or was first reported on Friday "
              "20 November 2026; disputed claims are attributed. Sources: "
              "AP, Reuters, AFP, BBC, Al Jazeera, UN News. Original drawings.")
    d.text((16, 996), footer, font=ff, fill=(60, 55, 45))

    img.save(OUT, format="PNG", optimize=True)
    return OUT


if __name__ == "__main__":
    path = build()
    print(path, os.path.getsize(path))
