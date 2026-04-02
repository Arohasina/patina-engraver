"""Draw a triangle on the AxiDraw V3.

Requires: pip install pyaxidraw
"""

from pyaxidraw import axidraw

ad = axidraw.AxiDraw()
ad.interactive()
ad.connect()

ad.options.units = 1  # inches

# Pen up, move to start
ad.penup()
ad.moveto(1, 1)

# Draw triangle
ad.pendown()
ad.lineto(3, 1)   # bottom right
ad.lineto(2, 3)   # top
ad.lineto(1, 1)   # back to start

ad.penup()
ad.moveto(0, 0)   # return home

ad.disconnect()
print("Done.")
