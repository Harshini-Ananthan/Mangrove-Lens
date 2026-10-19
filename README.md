# Mangrove Guardian 🌳🛰️

**An AI Agent for Satellite-Based Monitoring and Conservation of Mangrove Forests**

## 📖 Project Description
Mangrove Guardian is a research-grade project focused on the monitoring and conservation of the Sundarbans Mangrove Forest using satellite imagery (Sentinel-2, Sentinel-5P) and Google Earth Engine. By integrating machine learning and AI agents, this system analyzes environmental data from 2019 to the present, identifies threats, and provides actionable insights for conservation efforts.

## 🎯 Objectives
- **Monitor** mangrove health and coverage over time using high-resolution satellite imagery.
- **Analyze** environmental factors such as atmospheric conditions using Sentinel-5P data.
- **Predict** potential threats or degradation using Machine Learning (Random Forest).
- **Automate** decision-making and insights generation via an AI Agent framework (CrewAI/LangGraph).
- **Visualize** the findings interactively using a Streamlit dashboard.

## 🛠️ Technology Stack
- **Data Source:** Google Earth Engine (Sentinel-2, Sentinel-5P)
- **Programming Language:** Python 3.9+
- **Geospatial Processing:** geemap, geopandas, rasterio
- **Data Science:** pandas, numpy, matplotlib, plotly
- **Machine Learning:** scikit-learn, joblib
- **Backend API:** FastAPI, Uvicorn
- **Frontend / Dashboard:** React (Vite, Leaflet, Recharts, TailwindCSS)
- **Database:** SQLite (SQLAlchemy)
- **AI Agent Framework:** To be implemented (CrewAI / LangGraph)

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
│   ├── dashboard/     # Streamlit app code
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
   Run the following command to authenticate your Earth Engine account (a built-in mock satellite data generator is automatically used if not authenticated):
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

## 🗺️ Future Roadmap
- **Phase 1:** Professional Project Setup (Current)
- **Phase 2:** Data Collection via Google Earth Engine (Sentinel-2, Sentinel-5P)
- **Phase 3:** Exploratory Data Analysis & Preprocessing
- **Phase 4:** Machine Learning Model Development (Random Forest)
- **Phase 5:** Dashboard Integration (Streamlit)
- **Phase 6:** AI Decision Agent Implementation (CrewAI/LangGraph)
- **Phase 7:** Alerts & Reporting Modules

---
*Developed for the conservation of the Sundarbans Mangrove Forest.*
