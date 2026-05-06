# patina-engraver

**patina-engraver** is a Python toolkit for turning your daily Fitbit steps and activity logs into custom visual engravings on an AxiDraw V3 plotter.  
It loads step counts and related activity data from exported Fitbit files, visualizes them, and controls the AxiDraw to engrave personal patterns on a wristband.

---

## Features

- **Data Loader:** Processes manually exported Fitbit data (CSV, JSON).
- **Custom Engraving:** Turns activity metrics into patterns for AxiDraw V3 to draw on the wristband.

---

## Requirements

- Python 3 (recommended: 3.9+)
- [pyaxidraw](https://pypi.org/project/pyaxidraw/) (AxiDraw API)
- Fitbit and Google account for data export (CSV/JSON)
- AxiDraw V3 hardware (for engraving)

---

## Installation

1. **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\Activate.ps1
    # macOS/Linux:
    source .venv/bin/activate
    ```
2. **Install AxiDraw and other requirements:**
    ```bash
    python -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
    ```

3. (Optional) Install other requirements:
    ```bash
    pip install -r requirements.txt
    ```
    
---

## Preparing your Fitbit data

1. Download your latest Fitbit/Google data export and extract it on your system.
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
3. No need to manually copy individual files; always replace the full `Fitbit` directory to ensure all data is up to date.

---

## Usage

**1. Load and preview your steps data to test if data is being loaded correctly**
```bash
python scripts/load_steps.py
```
Shows a summary (`date` / `steps per day`) from your Fitbit export.

**2. Test your AxiDraw connection**
Connect your AxiDraw via USB cable to your laptop and power it on with the charger. 

```bash
python scripts/draw_triangle.py
```
Draws a simple triangle to test if the axidraw is successfully connected to your laptop.

**3. Draw wristband outline**
```bash
python scripts/draw_outline.py
```
Draws a reference outline for the intended engraving area and tracker cutout.

**4. Engrave your Patina Wristband!**
```bash
python scripts/draw_wristband.py
```
This script translates the past week's health data into unique patterns and engraves them on the wristband. You can manually input the start week with:
```python
WEEK_START = "YYYY-MM-DD"
```

---

## Project Structure

```
scripts/
    draw_outline.py     # Draws band outline, serves as setup
    draw_triangle.py    # Basic test pattern for hardware check
    draw_wristband.py   # Engraves visual patterns from Fitbit
    load_steps.py       # Displays summary of your steps for testing data loading.
Fitbit/
    Physical Activity_GoogleData/   # Place steps_*.csv here (from export)
    Global Export Data/             # Place relevant JSON here (from export)
requirements.txt      # (optional) for dependency tracking
README.md            
```

---

## How it works

- Parses your CSV/JSON data for the past week.
- Maps health metrics (steps, calories, sleep, distance, etc.) to positions, lines, or fractal marks on the wristband.
- Controls AxiDraw to engrave physical patterns unique to your data.

---

## License

[MIT](LICENSE) (or your actual license here)

---

## Credits

AxiDraw is developed by [Evil Mad Scientist](https://axidraw.com/).  
Python interface: [pyaxidraw](https://pypi.org/project/pyaxidraw/).

---

**Contributions and suggestions welcome!**  
