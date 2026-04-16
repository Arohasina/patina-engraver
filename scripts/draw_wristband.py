"""
draw_wristband.py — Engrave Patina Tracker wristband patterns from Fitbit data.

Zones (band-local x, left to right):
  Zone 2 – Activity Calories    (  0– 43 mm)  20 %
  Zone 1 – Steps / Active Time  ( 43–129 mm)  40 %
  Zone 3 – Time in Bed          (129–172 mm)  20 %
  Zone 4 – Total Walk Distance  (172–215 mm)  20 %

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
BAND_W  = 215.0   # mm — physical band width  (21.5 cm)
BAND_H  =  34.0   # mm — physical band height ( 3.4 cm)
MARGIN  =   2.0   # mm — distance from AxiDraw home (0,0) to band top-left corner

Y_TOP    = 0.0
Y_BOTTOM = BAND_H

# Zone X boundaries (band-local mm)
Z2_X0, Z2_X1 = 0.0,            BAND_W * 0.20   # Calories     (20 %)
Z1_X0, Z1_X1 = BAND_W * 0.20,  BAND_W * 0.60   # Steps/Active (40 %)
Z3_X0, Z3_X1 = BAND_W * 0.60,  BAND_W * 0.80   # Time in Bed  (20 %)
Z4_X0, Z4_X1 = BAND_W * 0.80,  BAND_W           # Distance     (20 %)

DOT_SPACING      = 0.5   # mm between dots in Zone 1 (zigzag)
DOT_SPACING_LINE = 2.0   # mm between dots in Zones 2 & 3 (stipple lines)

FITBIT_DIR   = Path(__file__).parent.parent / "Fitbit"
ACTIVITY_DIR = FITBIT_DIR / "Physical Activity_GoogleData"
GLOBAL_DIR   = FITBIT_DIR / "Global Export Data"


#Data loading

def _csv_daily_totals(pattern, col):
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
    totals = defaultdict(int)
    for pattern in ("very_active_minutes-*.json", "moderately_active_minutes-*.json"):
        for f in sorted(GLOBAL_DIR.glob(pattern)):
            with f.open(encoding="utf-8") as fh:
                data = json.load(fh)
            for entry in data:
                totals[_parse_date(entry["dateTime"])] += int(entry["value"])
    return dict(totals)


def load_sleep_minutes():
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
    ad.moveto(x0 + MARGIN, y0 + MARGIN)
    ad.pendown()
    ad.lineto(x1 + MARGIN, y1 + MARGIN)
    ad.penup()


#Zone 1: Steps / Active Time 

def draw_zone1(ad, avg_steps, avg_active_min):
    n_lines  = max(1, min(avg_steps // 1000, 10))  # 1000 steps = 1 stroke, cap at 10
    stroke_w = (Z1_X1 - Z1_X0) / 10               # always sized for 10 strokes; unused space stays blank
    noise_sigma = (1.0 - min(1.0, avg_active_min / 120.0)) * 3.0  # mm

    for i in range(n_lines):
        xl, xr = Z1_X0 + i * stroke_w, Z1_X0 + (i + 1) * stroke_w
        if i % 2 == 0:
            xa, ya, xb, yb = xl, Y_BOTTOM, xr, Y_TOP
        else:
            xa, ya, xb, yb = xl, Y_TOP, xr, Y_BOTTOM

        n_dots = max(1, int(math.hypot(xb - xa, yb - ya) / DOT_SPACING))
        for j in range(n_dots + 1):
            t = j / n_dots
            cx = max(Z1_X0, min(Z1_X1, xa + t * (xb - xa) + random.gauss(0, noise_sigma)))
            cy = max(Y_TOP,  min(Y_BOTTOM, ya + t * (yb - ya) + random.gauss(0, noise_sigma)))
            dot(ad, cx, cy)


#Zone 2: Activity Calories

def draw_zone2(ad, calories_per_day):
    zone_w  = Z2_X1 - Z2_X0
    max_cal = max((c for c in calories_per_day if c > 0), default=1.0)

    for i, cal in enumerate(calories_per_day):
        if cal <= 0:
            continue
        x = Z2_X0 + (i + 0.5) * zone_w / 7
        line_dots(ad, x, Y_TOP, x, Y_TOP + (cal / max_cal) * BAND_H, DOT_SPACING_LINE)


#Zone 3: Time in Bed

def draw_zone3(ad, sleep_per_day):
    zone_w = Z3_X1 - Z3_X0

    for i, mins in enumerate(sleep_per_day):
        if not (240 <= mins <= 540):
            continue
        x        = Z3_X0 + (i + 0.5) * zone_w / 7
        line_len = ((mins - 240) / (540 - 240)) * BAND_H
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
    arm = min(Z4_X1 - Z4_X0, BAND_H) * 0.35
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
    ad.options.units = 2   # mm
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
