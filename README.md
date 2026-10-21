# HeatGuard AI ☀️

**Climate intelligence for everyday decisions.**

HeatGuard AI is a web-based dashboard concept for exploring regional temperatures, reviewing illustrative heat-risk categories, and comparing how different alert-processing strategies handle incoming regional alerts. Users can edit region data, run a simulation, inspect a Gantt chart, compare algorithm metrics, and export results as a CSV.

## Features

- **Editable regional data** — add, edit, or remove regions and change temperature, arrival time, and burst time.
- **Heat-risk categories** — categorize entered temperatures into illustrative severity bands.
- **Five scheduling algorithms** — FCFS, SJF, SRTF, Round Robin, and Priority Scheduling.
- **Gantt chart** — view the selected algorithm's execution timeline, with start and finish times available on hover.
- **Performance metrics** — inspect waiting time, turnaround time, response time, start time, and completion time.
- **Risk insights** — view the severity distribution and general suggested precautions.
- **Algorithm comparison** — compare average waiting, turnaround, and response times across algorithms.
- **CSV export** — download simulation results for further analysis.
- **Sample dataset** — `sample_data.csv` supplies initial regional values and can be restored from the app.

## Scheduling algorithms

| Algorithm | Description |
|---|---|
| **FCFS — First Come, First Served** | Processes alerts in arrival order. |
| **SJF — Shortest Job First** | Runs the available process with the shortest burst time first; non-preemptive. |
| **SRTF — Shortest Remaining Time First** | Preemptive version of SJF; runs the available process with the shortest remaining time. |
| **Round Robin** | Gives each process a turn for a configurable time quantum. |
| **Priority Scheduling** | Runs the available process with the highest priority first; lower numeric values mean higher priority. |

The app maps the illustrative temperature severity category to a numeric priority for Priority Scheduling.

## Technology stack

- Python
- Streamlit
- pandas
- Plotly

## Project structure

Keep these files together in the same project directory:

```text
HeatGuardAI/
├── .gitignore
├── app.py
├── heatwave_ai.py
├── metrics.py
├── README.md
├── requirements.txt
├── sample_data.csv
└── scheduler.py
```

- `app.py` — website interface, editable data table, charts, metrics, and simulation flow.
- `heatwave_ai.py` — temperature severity categories, priority mapping, and suggested precaution text.
- `scheduler.py` — implementations of FCFS, SJF, SRTF, Round Robin, and Priority Scheduling.
- `metrics.py` — waiting, turnaround, and response-time calculations and result tables.
- `sample_data.csv` — initial sample region data.
- `requirements.txt` — Python package dependencies.

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/BiyasMaji06/HeatGuardAI.git
cd HeatGuardAI
```

### 2. Create and activate a virtual environment (recommended)

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the website

```bash
python -m streamlit run app.py
```

Streamlit will print a local URL in the terminal, usually `http://localhost:8501`. Open that URL in your browser.

## How to use the dashboard

1. Edit the regional rows in the data table, or add and remove rows.
2. Enter a unique Process ID, region name, temperature, arrival time, and burst time for each row.
3. Choose one of the five scheduling algorithms.
4. If using Round Robin, select a time quantum.
5. Click **Analyze conditions**.
6. Review the execution timeline, risk insights, and algorithm comparison.
7. Download the results as a CSV if needed.
8. Click **Restore sample data** to return to the initial dataset.

Arrival time must be a non-negative whole number, burst time must be a positive whole number, and Process IDs must be unique.

## Data and scope

- The included regional dataset is sample data, not a live observation feed.
- Temperatures can be edited manually in the dashboard.
- The current version does not fetch live weather observations or forecasts from a weather provider.
- Severity bands are illustrative rules, not official meteorological classifications.
- Suggested precautions are general informational text, not official forecasts or emergency instructions, and are not a substitute for local authority guidance.
- The current severity and advisory logic is rule-based, not a trained machine-learning model.

## Contributing

Suggestions and contributions are welcome. Consider opening an issue describing a proposed improvement before submitting a pull request.

## License

No license is specified here. Unless a license file is added to the repository, reuse and redistribution permissions are not explicitly granted.