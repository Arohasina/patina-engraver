# patina-engraver

Loads steps data from a manually downloaded Fitbit export and converts it into lines to engrave with an AxiDraw V3.

## Requirements

- Python 3

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Your prompt should show `(.venv)` when active.

### 2. Install AxiDraw (only needed for drawing)

```bash
python -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
```

Check it installed:

```bash
pip show pyaxidraw
or pip show axicli
```

---

## Usage

### Load and view your steps data

```bash
python scripts/load_steps.py
```

### Draw a triangle on the AxiDraw - to test AxiDraw V3 connection

1. Plug in and power on the AxiDraw V3
2. Put a pen in the holder and place paper on the bed
3. Run:

```bash
python scripts/draw_triangle.py
```

---

## Adding your Fitbit data

1. Download your data export from your Fitbit/Google account
2. Find the `steps_YYYY-MM-DD.csv` files
3. Place them in:

```
Fitbit/Physical Activity_GoogleData/
```

