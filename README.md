# Mangrove Guardian 🌳🛰️

**An AI Agent for Satellite-Based Monitoring and Conservation of Mangrove Forests**

## 📖 Project Description
Mangrove Guardian is a research-grade project focused on the monitoring and conservation of the Sundarbans Mangrove Forest using satellite imagery (Sentinel-2, Sentinel-5P) and Google Earth Engine. By integrating machine learning and AI agents, this system analyzes environmental data from 2019 to the present, identifies threats, and provides actionable insights for conservation efforts.

## 🎯 Objectives
- **Monitor** mangrove health and coverage over time using high-resolution satellite imagery.
- **Analyze** environmental factors such as atmospheric conditions using Sentinel-5P data.
- **Predict** potential threats or degradation using Machine Learning (Random Forest).
- **Automate** decision-making through an auditable deterministic agent workflow.
- **Visualize** observations, forecasts, evidence, and risk in the React map dashboard.

## 🛠️ Technology Stack
- **Data Source:** Google Earth Engine (Sentinel-2, Sentinel-5P)
- **Programming Language:** Python 3.9+
- **Geospatial Processing:** geemap, geopandas, rasterio
- **Data Science:** pandas, numpy, matplotlib, plotly
- **Machine Learning:** scikit-learn, joblib
- **Backend API:** FastAPI, Uvicorn
- **Frontend / Dashboard:** React (Vite, Leaflet, Recharts, TailwindCSS)
- **Database:** SQLite (SQLAlchemy)
- **AI Agent Framework:** Deterministic observe-analyze-decide-report orchestration

## 📁 Folder Structure
The project follows a scalable data science and software engineering structure:

```text
MangroveGuardian/
│
├── frontend/          # React + Vite interactive web dashboard
├── data/              # Data storage (ignored in version control)
│   ├── raw/           # Original, immutable data dumps
│   ├── processed/     # Cleaned data used for modeling
│   ├── external/      # Third-party data sources
│
├── notebooks/         # Jupyter notebooks for exploration and prototyping
├── src/               # Source code for the project
│   ├── config/        # Configuration management (e.g., loading .env)
│   ├── data/          # Scripts to fetch or generate data
│   ├── features/      # Scripts to turn raw data into features for modeling
│   ├── models/        # Machine learning logic (training, inference)
│   ├── agents/        # AI decision agent logic
│   ├── providers/     # Demo and Google Earth Engine source adapters
│   ├── utils/         # Helper functions
│
├── reports/           # Generated analysis as HTML, PDF, LaTeX, etc.
├── logs/              # Execution logs
├── models/            # Trained and serialized models (e.g., .pkl)
├── tests/             # Unit and integration tests
├── docs/              # Documentation (Sphinx, MkDocs, etc.)
├── scripts/           # Standalone utility or deployment scripts
├── requirements.txt   # Python dependencies
├── README.md          # Project overview
├── .env.example       # Example environment variables
├── .gitignore         # Ignored files and folders
```

## 🚀 Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd MangroveGuardian
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   - **Backend Dependencies:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Frontend Dependencies:**
     ```bash
     cd frontend
     npm install
     cd ..
     ```

4. **Environment Variables:**
   Copy the example environment file and fill in your details:
   ```bash
   cp .env.example .env
   ```

5. **Google Earth Engine Setup (Optional):**
   Run the following command to authenticate your Earth Engine account. Live mode fails explicitly if credentials are unavailable; deterministic demo mode must be selected with `SATELLITE_PROVIDER=demo`:
   ```bash
   earthengine authenticate
   ```

## 🖥️ Running the Servers

### 1. Start the Backend API (FastAPI)
From the project root directory, ensure your virtual environment is activated:
```bash
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Launch the FastAPI server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend API:** `http://localhost:8000`
- **Interactive API Docs (Swagger UI):** `http://localhost:8000/docs`
- **Health Check Endpoint:** `http://localhost:8000/api/v1/health`

### 2. Start the Frontend Dashboard (React + Vite)
In a separate terminal window, start the frontend development server:
```bash
cd frontend
npm run dev
```
- **Web Dashboard URL:** `http://localhost:5173`

### 3. Watch all agents and services live

Open another Command Prompt from the project directory:

```bash
python scripts/watch_operations.py
```

This is a read-only observer. It streams persisted activity from the API,
scheduler, Earth Engine acquisition, data-quality, feature, forecasting,
risk-decision, reporting, alerting and retraining stages. Closing the console
does not stop or change the autonomous system. Use `--history 0` to show only
new events or `--no-color` if ANSI color is unavailable.
If `API_KEY` is configured on the server, pass `--api-key <key>` or set
`MANGROVE_LENS_API_KEY` in the console environment.

## Verified monitoring workflow

The implemented workflow is deliberately deterministic and auditable:

1. Sentinel-2, Sentinel-1, Sentinel-5P OFFL CO, and the CGMD mangrove extent are queried through Earth Engine.
2. Pixel quality, source counts, collection IDs, and model/rule versions are stored with every period.
3. A Random Forest forecasts expected NDVI from leakage-safe lagged features; a declared seasonal persistence baseline is used until a trained artifact is installed.
4. The decision engine combines forecast residual, anomaly score, moisture, SAR, CO context, and data quality. CO is never presented as causal evidence.
5. High and critical decisions require human review.

### Run the offline demonstration

```bash
python -m scripts.bootstrap_demo
python -m scripts.train_model
python -m uvicorn src.main:app --reload
```

Then run `pnpm install && pnpm dev` inside `frontend/`.

### Live Earth Engine mode

See [Earth Engine setup](docs/EARTH_ENGINE_SETUP.md). Set `SATELLITE_PROVIDER=earth_engine` only after `GET /api/v1/health` confirms readiness.

Backfill and validate the observational dataset, then train the model:

```bash
python -m scripts.backfill_earth_engine --start 2019-01-01 --workers 4
python -m scripts.validate_dataset
python -m scripts.train_model
```

The API queues monitoring work at `POST /api/v1/monitoring/run`; progress is available from `GET /api/v1/monitoring/jobs`. The stable analysis grid is available from `GET /api/v1/grid`.

See the [completion report](docs/COMPLETION_REPORT.md) and [operations runbook](docs/RUNBOOK.md) for verified metrics, deployment, recovery, alert approval, and external scientific gates.

### Verification

```bash
python -m pytest -q
python -m compileall -q src scripts
cd frontend
pnpm lint
pnpm build
```

The complete scientific, engineering, and deployment roadmap is in [the implementation plan](docs/IMPLEMENTATION_PLAN.md).

---
*Developed for the conservation of the Sundarbans Mangrove Forest.*
