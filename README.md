# Household Electricity Bill Estimator (SDG 7)

A Python console application that supports **SDG 7: Affordable and Clean Energy**.
Users record their household appliances, and the app estimates monthly electricity
usage (kWh), the bill under a tiered tariff, CO2 emissions, and how much they could
save by changing their habits.

## Group members
- Isameldin Widaatalla Taha Omer
- Mohamed Abdelmajed Ahmed

## How to run
Requires Python 3.8+ and no extra libraries.

```bash
python3 run.py           # console version (or: python3 -m energy_saver)
python3 run_gui.py       # simple window (GUI) version, uses Tkinter
python3 -m unittest -v   # run the unit tests
```

The GUI uses Tkinter, which is part of Python's standard library.

**macOS note:** use the Python installer from [python.org](https://www.python.org/downloads/).
The Apple system Python (`/usr/bin/python3`) ships an old Tk that shows a blank
window. After installing python.org Python, run:

```bash
/usr/local/bin/python3 run_gui.py
```

(With Homebrew Python, run `brew install python-tk` if you get `No module named '_tkinter'`.)

## Features (main menu)
| Option | Feature |
|---|---|
| 1 | Add an appliance (name, watts, quantity, hours/day, days/month) |
| 2 | View appliance list with monthly kWh |
| 3 | Remove an appliance |
| 4 | Calculate monthly usage and bill (tariff block breakdown) |
| 5 | Energy-saving analysis (rating, CO2, usage share chart, tips) |
| 6 | "What-if" simulator (savings from fewer hours of use) |
| 7 | Load sample household (demo data) |
| 8 | Save / load appliances to a CSV file |
| 0 | Exit |

## Project structure
```
energy_saver/
  main.py              entry point (main)
  app.py               EnergyApp: menu loop and features
  models/appliance.py  Appliance class
  models/household.py  Household class (list of appliances, CSV save/load)
  services/tariff.py   TariffCalculator (tiered bill calculation)
  services/analysis.py EnergyAnalyzer (CO2, rating, tips, what-if)
  utils/validation.py  input validation helpers
  ui/display.py        formatted console output
  ui/gui.py            EnergyGUI: simple Tkinter window (optional)
tests/                 unit tests
docs/                  UML diagram, sample output, report and slide drafts
```

## Assumptions
Tariff rates (RM 0.218 to 0.571 per kWh in five blocks), 8% service tax above
600 kWh, and the grid emission factor of 0.585 kg CO2/kWh are teaching values.
They are defined as constants at the top of `services/tariff.py` and
`services/analysis.py` so they can be updated easily.
