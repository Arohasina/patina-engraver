"""
draw_wristband.py to Engrave Patina Tracker wristband patterns from Fitbit data.

Run: .venv\Scripts\python.exe scripts\draw_wristband.py
"""
import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

from pyaxidraw import axidraw

# Band dimensions & AxiDraw offset
BAND_W    = 220.0  # mm — physical band width  (22 cm)
BAND_H    =  45.0  # mm — physical band height ( 4.5 cm)
MARGIN    =   2.0  # mm — distance from AxiDraw home (0,0) to band top-left corner
MARGIN_Y  =   2.0  # mm — top and bottom drawing margin within the band
CLASP_W   =  20.0  # mm — right side hidden under magnet clasp; never engraved
TRACKER_W =  10.0  # mm — blank hole for tracker module between Z1 and Z3
GAP_Z2_Z1 =   3.0  # mm — blank separator between Calories and Steps zones
GAP_Z3_Z4 =   3.0  # mm — blank separator between Time in Bed and Distance zones

Y_TOP    = MARGIN_Y
Y_BOTTOM = BAND_H - MARGIN_Y
Y_BOT_Z12 = Y_BOTTOM - 2.0  # zones 1 & 2 stop 2 mm above the bottom margin boundary

# Zone X boundaries (band-local mm)
_DRAW  = BAND_W - CLASP_W                              # 200 mm engravable
_FIXED = TRACKER_W + GAP_Z2_Z1 + GAP_Z3_Z4            # 16 mm total fixed gaps
_UNIT  = (_DRAW - _FIXED) / 90                         # 1 proportional part (184 mm / 90 parts)

_A = 15 * _UNIT                                        # end of Z2
_B = _A + GAP_Z2_Z1                                    # start of Z1
_C = _B + 40 * _UNIT                                   # end of Z1 / start of tracker hole
_D = _C + TRACKER_W                                    # end of tracker hole / start of Z3
_E = _D + 15 * _UNIT                                   # end of Z3
_F = _E + GAP_Z3_Z4                                    # start of Z4

Z2_X0, Z2_X1 = 0.0, _A   # Calories     (15 %)
Z1_X0, Z1_X1 = _B,  _C   # Steps/Active (40 %)
ZT_X0, ZT_X1 = _C,  _D   # Tracker hole (10 mm blank)
Z3_X0, Z3_X1 = _D,  _E   # Time in Bed  (15 %)
Z4_X0, Z4_X1 = _F,  _DRAW # Distance     (20 %)

DOT_SPACING      = 0.5   # mm between dots in Zone 1 (zigzag)
DOT_SPACING_LINE = 2.0   # mm between dots in Zones 2 & 3 (stipple lines)

FITBIT_DIR   = Path(__file__).parent.parent / "Fitbit"
ACTIVITY_DIR = FITBIT_DIR / "Physical Activity_GoogleData"
GLOBAL_DIR   = FITBIT_DIR / "Global Export Data"


#Data loading

def _csv_daily_totals(pattern, col):
    """
    pattern: a glob pattern (e.g. "steps_*.csv") to match CSV files in ACTIVITY_DIR
    col:the name of the column whose values you want to sum up
    """
    totals = defaultdict(float)
    for f in sorted(ACTIVITY_DIR.glob(pattern)):
        with f.open(newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            headers = [h.strip() for h in next(reader)]
            try:
                idx = headers.index(col)
            except ValueError:
                continue
            for row in reader:
                if len(row) > idx:
                    date = row[0].strip()[:10]
                    try:
                        totals[date] += float(row[idx].strip())
                    except ValueError:
                        pass
    return dict(totals)


def load_steps():
    return {d: int(v) for d, v in _csv_daily_totals("steps_*.csv", "steps").items()}


def load_calories():
    return _csv_daily_totals("calories_*.csv", "calories")


def load_distance_km():
    meters = _csv_daily_totals("distance_*.csv", "distance")
    return {d: v / 1000.0 for d, v in meters.items()}


def _parse_date(dt_str):
    part = dt_str.split()[0]
    m, d, y = part.split("/")
    return f"20{y}-{m}-{d}"


def load_active_minutes():
    """"
    reads JSON files for "very active" and "moderately active" minutes, 
    adds both together per day, giving total active minutes per day.
    """
    totals = defaultdict(int)
    for pattern in ("very_active_minutes-*.json", "moderately_active_minutes-*.json"):
        for f in sorted(GLOBAL_DIR.glob(pattern)):
            with f.open(encoding="utf-8") as fh:
                data = json.load(fh)
            for entry in data:
                totals[_parse_date(entry["dateTime"])] += int(entry["value"])
    return dict(totals)


def load_sleep_minutes():
    """"
    reads sleep JSON files and extracts timeInBed (in minutes) per date.
    """
    totals = defaultdict(int)
    for f in sorted(GLOBAL_DIR.glob("sleep-*.json")):
        with f.open(encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            data = [data]
        for entry in data:
            date = entry.get("dateOfSleep", "")[:10]
            if date:
                totals[date] += entry.get("timeInBed", 0)
    return dict(totals)


def pick_week(steps):
    """"
    from all days that have step data, picks the 7 most recent days with non-zero steps. 
    If fewer than 7 exist, it pads the front with empty strings.
    """
    dates = sorted(d for d, s in steps.items() if s > 0)[-7:]
    while len(dates) < 7:
        dates.insert(0, "")
    return dates


#AxiDraw helpers (all coordinates are band-local mm; MARGIN shifts to AxiDraw space)

def dot(ad, x, y):
    ad.moveto(x + MARGIN, y + MARGIN)
    ad.pendown()
    ad.penup()


def line_dots(ad, x0, y0, x1, y1, spacing=DOT_SPACING):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return
    n = max(1, int(length / spacing))
    for i in range(n + 1):
        t = i / n
        dot(ad, x0 + t * dx, y0 + t * dy)


def draw_line(ad, x0, y0, x1, y1):
    """
    draws a solid line between two points
    """
    ad.moveto(x0 + MARGIN, y0 + MARGIN)
    ad.pendown()
    ad.lineto(x1 + MARGIN, y1 + MARGIN)
    ad.penup()


#Zone 1: Steps / Active Time 

def draw_zone1(ad, avg_steps, avg_active_min):
    n_lines  = max(1, min(avg_steps // 1000, 10))  # 1000 steps = 1 stroke, cap at 10
    stroke_w = (Z1_X1 - Z1_X0) / 10               # always sized for 10 strokes; unused space stays blank
    noise_sigma = (1.0 - min(1.0, avg_active_min / 120.0)) * 2.5  # mm

    for i in range(n_lines):
        xl, xr = Z1_X0 + i * stroke_w, Z1_X0 + (i + 1) * stroke_w
        if i % 2 == 0:
            xa, ya, xb, yb = xl, Y_BOT_Z12, xr, Y_TOP
        else:
            xa, ya, xb, yb = xl, Y_TOP, xr, Y_BOT_Z12

        n_dots = max(1, int(math.hypot(xb - xa, yb - ya) / DOT_SPACING))
        for j in range(n_dots + 1):
            t = j / n_dots
            cx = max(Z1_X0,  min(Z1_X1,   xa + t * (xb - xa) + random.gauss(0, noise_sigma)))
            cy = max(Y_TOP,   min(Y_BOT_Z12, ya + t * (yb - ya) + random.gauss(0, noise_sigma)))
            dot(ad, cx, cy)


#Zone 2: Activity Calories

def draw_zone2(ad, calories_per_day):
    zone_w  = Z2_X1 - Z2_X0
    max_cal = max((c for c in calories_per_day if c > 0), default=1.0)

    for i, cal in enumerate(calories_per_day):
        if cal <= 0:
            continue
        x = Z2_X0 + (i + 0.5) * zone_w / 7
        line_dots(ad, x, Y_TOP, x, Y_TOP + (cal / max_cal) * (Y_BOT_Z12 - Y_TOP), DOT_SPACING_LINE)


#Zone 3: Time in Bed

def draw_zone3(ad, sleep_per_day):
    zone_w = Z3_X1 - Z3_X0

    for i, mins in enumerate(sleep_per_day):
        if not (240 <= mins <= 540):
            continue
        x        = Z3_X0 + (i + 0.5) * zone_w / 7
        line_len = ((mins - 240) / (540 - 240)) * (Y_BOTTOM - Y_TOP)
        line_dots(ad, x, Y_BOTTOM, x, Y_BOTTOM - line_len, DOT_SPACING_LINE)


#Zone 4: Total Walking Distance

def _fractal_plus(ad, cx, cy, arm, depth):
    if depth <= 0 or arm < 0.5:
        return
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        ex = max(Z4_X0, min(Z4_X1, cx + dx * arm))
        ey = max(Y_TOP,  min(Y_BOTTOM, cy + dy * arm))
        draw_line(ad, cx, cy, ex, ey)
        _fractal_plus(ad, ex, ey, arm * 0.5, depth - 1)


def draw_zone4(ad, total_km):
    level = 1 if total_km < 20 else (2 if total_km < 40 else 3)
    cx  = (Z4_X0 + Z4_X1) / 2
    cy  = (Y_TOP + Y_BOTTOM) / 2
    arm = min(Z4_X1 - Z4_X0, Y_BOTTOM - Y_TOP) * 0.35
    _fractal_plus(ad, cx, cy, arm, depth=level)


def main():
    random.seed(42)

    steps_by_day    = load_steps()
    calories_by_day = load_calories()
    active_by_day   = load_active_minutes()
    sleep_by_day    = load_sleep_minutes()
    dist_by_day     = load_distance_km()

    if not steps_by_day:
        print("No steps data found. Check that Fitbit CSVs are in the Fitbit/ folder.")
        return

    week = pick_week(steps_by_day)

    steps_vals    = [steps_by_day.get(d, 0)      for d in week]
    calories_vals = [calories_by_day.get(d, 0.0)  for d in week]
    active_vals   = [active_by_day.get(d, 0)      for d in week]
    sleep_vals    = [sleep_by_day.get(d, 0)       for d in week]
    dist_vals     = [dist_by_day.get(d, 0.0)      for d in week]

    avg_steps  = sum(steps_vals)  // max(1, sum(1 for s in steps_vals  if s > 0))
    avg_active = sum(active_vals) // max(1, sum(1 for a in active_vals if a > 0))
    total_km   = sum(dist_vals)

    print(f"Week:               {week[0] or '?'}  ->  {week[-1]}")
    print(f"Avg daily steps:    {avg_steps}")
    print(f"Avg active min/day: {avg_active}")
    print(f"Total distance km:  {total_km:.2f}")
    print(f"Calories by day:    {[round(c) for c in calories_vals]}")
    print(f"Sleep min by day:   {sleep_vals}")
    print()
    input("Press Enter to start engraving, or Ctrl-C to cancel...")

    ad = axidraw.AxiDraw()
    ad.interactive()
    ad.options.units         = 2    # mm
    ad.options.speed_pendown = 20   # % — drawing speed (default 25)
    ad.options.speed_penup   = 60   # % — travel speed (default 75)
    ad.options.pen_delay_up  = 150  # ms — wait after pen lifts before moving (prevents drag)
    ad.connect()

    ad.penup()
    ad.moveto(0, 0)

    print("Drawing Zone 2 (Calories)...")
    draw_zone2(ad, calories_vals)

    print("Drawing Zone 1 (Steps / Active Time)...")
    draw_zone1(ad, avg_steps, avg_active)

    print("Drawing Zone 3 (Time in Bed)...")
    draw_zone3(ad, sleep_vals)

    print("Drawing Zone 4 (Walking Distance)...")
    draw_zone4(ad, total_km)

    ad.penup()
    ad.moveto(0, 0)
    ad.disconnect()
    print("Done.")


if __name__ == "__main__":
    main()
