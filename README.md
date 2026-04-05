# EcoPackAI

## 1. Project Title
**EcoPackAI - AI Framework for Sustainable Packaging Recommendation**

## 2. Short Project Description
EcoPackAI predicts packaging **cost** and **CO2 impact** for packaging materials and ranks them using an **eco score** to recommend sustainable options.

## 3. Milestone Status (Current)
**Milestone 4 completed** with:
- working ML pipeline + backend API
- integrated frontend recommendation studio
- BI dashboard with CO2 reduction, cost savings, and usage trend charts
- sustainability report export (PDF + Excel)
- deployment-ready configs for Render/Heroku

## 4. Tech Stack
| Layer | Technology |
|---|---|
| Language | Python |
| API | Flask |
| ML/Data | scikit-learn, pandas, numpy, joblib |
| DB (optional scripts) | PostgreSQL |
| DB Access | SQLAlchemy, psycopg2-binary |
| Frontend | HTML, CSS, JavaScript |

## 5. Installation
1. Clone:
```bash
git clone <your-repo-url>
cd EcoPackAI
```
2. Create venv:
```bash
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Configure environment:
```bash
copy .env.example .env
# then update DB_PASSWORD (and other values if needed)
```

## 6. Project Structure (Important Files)
```text
backend/
  app.py                        # Main API used by frontend
frontend/
  index.html                    # Dashboard UI
  script.js                     # API integration + rendering
  style.css                     # UI styling
ml/
  generate_realistic_dataset.py # 600+ realistic row generation
  data_quality_gate.py          # Quality validation checks
  dataset_preparation.py        # Feature prep + scaler + splits
  model_training.py             # Cost/CO2 model training
  recommendation_engine.py      # CLI recommendation script
  predict_api.py                # Legacy/simple ML API
  dataset/
    real_materials_base.csv
    real_production_materials.csv
    materials.csv
    cleaned_materials.csv
    engineered_materials.csv
  models/
    cost_model.pkl
    co2_model.pkl
    scaler.pkl
dashboard/
  analytics.py                  # Metrics + top material analysis
report/
  EcoPackAI_Milestone3_Presentation.pptx
```

## 7. End-to-End Run Order (Current)
Run in this order:
```bash
python ml/generate_realistic_dataset.py
python ml/data_quality_gate.py
python ml/dataset_preparation.py
python ml/model_training.py
python backend/app.py
```

Open frontend:
- `frontend/index.html` in browser
- API base URL: `http://127.0.0.1:5000`

## 8. API Endpoints (backend/app.py)
- `GET /health` -> service status, dataset row count, active feature schema
- `GET /metadata/material-types` -> material type list for frontend dropdown
- `GET /recommend` -> best + top-5 recommendation from dataset
- `POST /recommend` -> recommendation from custom material input
- `GET /analytics/summary` -> BI dashboard metrics + chart data
- `GET /reports/sustainability?format=pdf|excel` -> downloadable sustainability report

Sample payload:
```json
{
  "materials": [
    {
      "material_name": "Custom Candidate",
      "material_type": "Bioplastic",
      "strength_rating": 7.5,
      "weight_capacity": 40,
      "biodegradability_score": 8,
      "recyclability_percentage": 82
    }
  ]
}
```

## 9. What Is Done
- Realistic synthetic dataset generation from original base dataset
- Minimum 600+ rows achieved (currently 700+)
- Data quality checks (range, nulls, distribution, correlations)
- Train/test split, scaling, model artifact saving
- Leakage-prone feature usage reduced in core training/inference flow
- Backend API integrated with frontend
- Frontend renders recommendation cards/tables (not raw JSON dump)
- BI dashboard for analytics insights (CO2 reduction, cost savings, trends)
- PDF + Excel sustainability report export
- Milestone 3 PPT created in `report/`

## 10. Current Limitations
- No automated unit/integration test suite yet
- No Docker/CI pipeline yet
- Some legacy scripts are still present and not part of new primary flow
- DB scripts contain hardcoded credentials and need env-based cleanup
- `backend/models/` has placeholder 0-byte model files; active models are in `ml/models/`

## 11. Recommended Next Steps
- Add `run_pipeline.py` to chain generate -> quality gate -> prepare -> train
- Add tests for API schema and ML pipeline contracts
- Move all secrets/config to `.env`
- Add Docker + CI workflow
- Add model versioning and retraining logs

## 12. Deployment (Render/Heroku)
The repo includes deployment-ready configuration:
- `Procfile` for Heroku (`gunicorn backend.app:app`)
- `render.yaml` for Render

### Render
1. Create a new Web Service and connect the repo (or use Blueprint to auto-read `render.yaml`).
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn backend.app:app --bind 0.0.0.0:$PORT`
4. Add env vars from `.env` (DB_* if using PostgreSQL).

### Heroku
1. `heroku create`
2. `git push heroku main`
3. `heroku config:set` your env vars (DB_* if using PostgreSQL)

## 13. License
No license file currently included. Add a `LICENSE` file (MIT/Apache-2.0 recommended).
# EcoPackAI – AI-Powered Sustainable Packaging Recommendation System

##  Project Repository

Due to file size limitations (exceeding 25MB), the complete project code could not be uploaded directly.
Please access the full project using the GitHub link below:

👉 https://github.com/jayrama039-str/ecopackai-0.1

---

## Project Description

EcoPackAI is an AI-based system developed to recommend sustainable and eco-friendly packaging solutions based on product characteristics. The system uses data analysis techniques to suggest optimal packaging materials that reduce environmental impact while maintaining efficiency and practicality.

---

##  Key Features

* Intelligent packaging recommendations
* Focus on sustainability and environmental impact
* Data-driven decision making using Python and Pandas
* Easy-to-use and scalable design

---

##  Note

The project files exceed the maximum upload size limit (25MB). Therefore, the complete implementation, datasets, and code are available in the GitHub repository provided above.

---

## Thank You

Please review the project using the provided link. Feel free to reach out for any clarifications.
