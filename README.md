# Patina Engraver

A student reproduction of the **Patina Engraver** system, originally presented at CHI 2015:

> Lee, M.-H., Cha, S., & Nam, T.-J. (2015). **Patina Engraver: Visualizing Activity Logs as Patina in Fashionable Trackers.** *Proceedings of the 33rd Annual ACM Conference on Human Factors in Computing Systems (CHI '15)*, 1173–1182. https://doi.org/10.1145/2702123.2702213

The original paper by Moon-Hwan Lee, Seijin Cha, and Tek-Jin Nam (KAIST) explored how activity tracking data could be engraved as patina-like patterns onto a wristband, turning personal data into a gradually accumulating, visible, material record instead of numbers on a screen.

This project recreates that system using a Fitbit Inspire 3 and an AxiDraw V3 plotter, with our own zone layout, pattern encoding logic, and wristband construction. The original paper used a custom-built piercing device (solenoid + needle); our reproduction adapts this concept using a Sharpie marker of different color for each week. 

**Reproduced by Arohasina Ravoahanginiainaa &Galina Pokitko, 2026**

---

## Features

- **Data Loader:** Processes manually exported Fitbit data (CSV, JSON).
- **Custom Engraving:** Turns activity metrics into patterns for AxiDraw V3 to draw on the wristband.

---

## How It Works
 
Activity data is exported from Fitbit, processed by a Python script, and sent directly to the AxiDraw, which draws data-driven patterns onto a painted wristband surface. Each week adds a new layer of marks, building up a physical history of your activity.
 
The wristband is 220 mm × 45 mm. The right 20 mm is hidden under the magnet clasp and never engraved, leaving 200 mm of engravable width. That space is divided into four zones separated by fixed gaps, arranged left to right:
 
```
[ Z2: Calories ] 3mm gap [ Z1: Steps/Active ] 10mm tracker hole [ Z3: Sleep ] 3mm gap [ Z4: Distance ] | 20mm clasp
```
 
| Position | Zone | Proportion | Data |
|----------|------|-----------|------|
| Leftmost | Zone 2 | ~15% | Calories (Mon–Sun) |
| — | 3 mm gap | — | Separator |
| Centre-left | Zone 1 | ~40% | Steps + Active Time |
| — | 10 mm blank | — | Tracker module cutout |
| Centre-right | Zone 3 | ~15% | Sleep / Time in Bed (Mon–Sun) |
| — | 3 mm gap | — | Separator |
| Rightmost | Zone 4 | ~20% | Total Walking Distance |
 
Proportions are calculated from 90 proportional units across the 184 mm of drawable area (200 mm minus 16 mm of fixed gaps): Zone 2 = 15 units, Zone 1 = 40 units, Zone 3 = 15 units, Zone 4 = 20 units.

### Pattern Encoding

- **Steps + Active Time** — Diagonal zigzag lines (1000 steps = 1 line). Higher active time produces smoother lines; lower activity introduces noise for a more irregular look.
- **Calories** — One vertical line per day, scaled relative to the highest calorie day of the week.
- **Sleep** — Similar to calories but inverted and filtered; gaps highlight irregular sleep patterns.
- **Distance** — Total weekly distance controls pattern complexity, from simple shapes to dense branching structures.

---

## Requirements

- Python 3 (recommended: 3.9+)
- [pyaxidraw](https://pypi.org/project/pyaxidraw/) (AxiDraw API)
- Fitbit and Google account for data export (CSV/JSON)
- AxiDraw V3 hardware (for engraving)

---

## Installation

1. **Clone the repo:**
    ```bash
    git clone https://github.com/Arohasina/patina-engraver.git
    cd patina-engraver
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\Activate.ps1
    # macOS/Linux:
    source .venv/bin/activate
    ```

3. **Install AxiDraw:**
    ```bash
    python -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
    ```

4. **(Optional) Install other requirements:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Preparing Your Fitbit Data

1. Download your latest Fitbit data from Google data export and extract it on your system.
2. **Replace the entire `Fitbit` folder in this repository with the new one from your export.**
    - The folder structure and contents must match the new export.
    - Example:
      ```
      <repo root>/
        Fitbit/
          Physical Activity_GoogleData/
          Global Export Data/
          ... (other Fitbit data subfolders)
      ```
3. No need to manually copy individual files. Always replace the full `Fitbit` directory to ensure all data is up to date.

---

## Usage

**1. Load and preview your steps data**

Test that your data is being loaded correctly:
```bash
python scripts/load_steps.py
```
Shows a summary (`date` / `steps per day`) from your Fitbit export.

**2. Test your AxiDraw connection**

Connect your AxiDraw via USB cable to your laptop and power it on with the charger:
```bash
python scripts/draw_triangle.py
```
Draws a simple triangle to confirm the AxiDraw is successfully connected.

**3. Draw the wristband outline**
```bash
python scripts/draw_outline.py
```
Draws a reference outline for the intended engraving area and tracker cutout.

**4. Engrave your Patina Wristband**
```bash
python scripts/draw_wristband.py
```
Translates the past week's health data into unique patterns and engraves them onto the wristband. You can manually set the start of the week with:
```python
WEEK_START = "YYYY-MM-DD"
```

---

## Project Structure

```
scripts/
    draw_outline.py     # Draws band outline, serves as setup
    draw_triangle.py    # Basic test pattern for hardware check
    draw_wristband.py   # Engraves visual patterns from Fitbit data
    load_steps.py       # Displays summary of steps for testing data loading
Fitbit/
    Physical Activity_GoogleData/   # Place steps_*.csv here (from export)
    Global Export Data/             # Place relevant JSON here (from export)
requirements.txt
README.md
```

---

## Physical Setup

### Wristband Construction

- **Layer 1** — Silicone base
- **Layer 2** — PVC layer
- **Layer 3** — White painted surface (for visibility)

A modular pouch holds the Fitbit tracker, secured with magnets on both sides and reinforced with staples. A support pad keeps the wristband flat and stable during engraving.

### Patina Coloring

Before engraving, yellow, orange, and blue Sharpie are applied across the surface to mimic the natural variation of patina on copper. A fine-point Sharpie is then used in the AxiDraw pen holder for engraving.

### Weekly Results

Patterns grow more complex as activity increases:
- **Low activity week** → sparse, simpler patterns
- **Moderate activity week** → more defined, varied marks
- **High activity week** → dense, complex patterns across all zones

---

## Links

- [Project Site](https://sites.google.com/view/patinaengraver)
- [Sprint Documentation](https://docs.google.com/document/d/1jsipCbgLdka5UFTaC-yq6kGwP3_bZ4m0GXoSer6dye8/edit?usp=sharing)

---

## Credits

AxiDraw is developed by [Evil Mad Scientist](https://axidraw.com/).
Python interface: [pyaxidraw](https://pypi.org/project/pyaxidraw/).
Link to the original reseach paper:
[Original Paper (ACM DL)](https://doi.org/10.1145/2702123.2702213)

---

## License

[MIT](LICENSE)

---

**Contributions and suggestions welcome!**
