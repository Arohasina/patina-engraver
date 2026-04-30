"""
draw_outline.py — Draw the wristband outline rectangle.

Run: .venv\Scripts\python.exe scripts\draw_outline.py
"""
from pyaxidraw import axidraw

BAND_W    = 220.0  # mm
BAND_H    =  45.0  # mm
MARGIN    =   2.0  # mm — AxiDraw home (0,0) to band top-left corner

# Tracker hole (must match draw_wristband.py constants)
CLASP_W   =  20.0
TRACKER_W =  10.0
GAP_Z2_Z1 =   3.0
GAP_Z3_Z4 =   3.0
TRACKER_H =  17.0  # mm — 1.7 cm tall

_UNIT     = (BAND_W - CLASP_W - TRACKER_W - GAP_Z2_Z1 - GAP_Z3_Z4) / 90
ZT_X0     = 55 * _UNIT + GAP_Z2_Z1          # left edge of tracker hole
ZT_X1     = ZT_X0 + TRACKER_W               # right edge
ZT_Y0     = (BAND_H - TRACKER_H) / 2        # centered vertically
ZT_Y1     = ZT_Y0 + TRACKER_H


def rect(ad, x0, y0, x1, y1):
    ad.moveto(x0 + MARGIN, y0 + MARGIN)
    ad.pendown()
    ad.lineto(x1 + MARGIN, y0 + MARGIN)
    ad.lineto(x1 + MARGIN, y1 + MARGIN)
    ad.lineto(x0 + MARGIN, y1 + MARGIN)
    ad.lineto(x0 + MARGIN, y0 + MARGIN)
    ad.penup()


def main():
    input("Press Enter to draw outline, or Ctrl-C to cancel...")

    ad = axidraw.AxiDraw()
    ad.interactive()
    ad.options.units = 2  # mm
    ad.connect()

    ad.penup()
    rect(ad, 0,     0,     BAND_W, BAND_H)   # band outline
    rect(ad, ZT_X0, ZT_Y0, ZT_X1, ZT_Y1)    # tracker hole

    ad.moveto(0, 0)
    ad.disconnect()
    print("Done.")


if __name__ == "__main__":
    main()
