# patina-engraver

Loads steps data from a manually downloaded Fitbit export and converts it into lines to engrave with an AxiDraw V3.

## 1) Add your Fitbit data

Download your Fitbit data export and place the CSV files in:

```
Fitbit/Physical Activity_GoogleData/steps_*.csv
```

## 2) Load and view steps data

```bash
python scripts/load_steps.py
```

## 3) Connect and draw with AxiDraw V3

*(coming soon)*

## Project structure

```text
.
|-- Fitbit/
|   `-- Physical Activity_GoogleData/
|       `-- steps_*.csv
|-- scripts/
|   `-- load_steps.py
`-- src/
    `-- patina_engraver/
        `-- axidraw_service.py
```

