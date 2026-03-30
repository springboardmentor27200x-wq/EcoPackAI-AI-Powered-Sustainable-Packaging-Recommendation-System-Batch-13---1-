# EcoPackAI

EcoPackAI is an AI-powered sustainable packaging recommendation system built with Flask, MySQL, HTML, CSS, and machine learning. The platform helps users choose eco-friendly packaging materials based on product profile, strength needs, shipping type, cost, and environmental impact.

## Features

- User signup, login, and logout
- AI-assisted packaging recommendation flow
- Materials database view backed by MySQL
- BI analytics dashboard
- Recommendation history tracking
- PDF export for analytics reports
- Deployment-ready Flask configuration for Render

## Tech Stack

- Frontend: HTML, CSS, Bootstrap-inspired custom UI
- Backend: Flask
- Database: MySQL
- Machine Learning: scikit-learn, pandas, joblib
- PDF Export: reportlab

## Project Structure

```text
Ecopackai/
|-- app.py
|-- requirements.txt
|-- Procfile
|-- runtime.txt
|-- render.yaml
|-- models/
|   |-- cost_model.pkl
|   |-- co2_model.pkl
|   |-- feature_names.pkl
|   |-- create_models.py
|-- static/
|   |-- style.css
|-- templates/
|   |-- layout.html
|   |-- dashboard.html
|   |-- recommend.html
|   |-- materials.html
|   |-- analytics.html
|   |-- history.html
|   |-- login.html
|   |-- signup.html
```

## Local Setup

1. Open PowerShell in the project folder.
2. Activate the virtual environment.
3. Install dependencies.
4. Run the Flask application.

```powershell
cd "D:\2nd year\Ecopackai"
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\app.py
```

Open the project in your browser:

[http://127.0.0.1:5000](http://127.0.0.1:5000)

## Database Configuration

The project uses MySQL with the database name:

`ecopackai_db`

Set these environment variables for deployment:

- `DB_ENGINE`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `DB_SSL_DISABLED`
- `DB_SSL_CA`
- `DB_SSL_VERIFY_CERT`
- `DB_SSL_VERIFY_IDENTITY`
- `DB_SSL_MODE`
- `SECRET_KEY`

If you are running locally and do not set them, the app currently defaults to:

- engine: `mysql`
- host: `localhost`
- port: `3306`
- user: `root`
- database: `ecopackai_db`

## Required Tables

The application uses these MySQL tables:

- `users`
- `products`
- `history`
- `recommendations`
- `predictions`
- `final_material_dataset`
- `final_product_dataset`

## Deployment on Render

1. Push this project to GitHub.
2. Go to Render and create a new Web Service.
3. Connect your GitHub repository.
4. Render will detect `render.yaml`.
5. Add the required environment variables:
   - `DB_ENGINE`
   - `DB_HOST`
   - `DB_PORT`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`
   - `DB_SSL_DISABLED`
   - `DB_SSL_CA`
   - `DB_SSL_VERIFY_CERT`
   - `DB_SSL_VERIFY_IDENTITY`
   - `DB_SSL_MODE`
   - `SECRET_KEY`
6. Deploy the service.

Start command used by Render:

```text
gunicorn app:app
```

## Notes

- MySQL Workbench is only the client tool. The deployed app must connect to a real MySQL server.
- HTTPS is handled by Render automatically after deployment.
- The PDF export feature needs `reportlab`, which is already included in `requirements.txt`.
- The Excel export feature uses `openpyxl`.
- The BI dashboard uses Plotly charts.
- Some hosted MySQL services require SSL. This project supports SSL through the database environment variables above.
- For a PostgreSQL cloud instance, set `DB_ENGINE=postgres`, `DB_PORT=5432`, and provide the PostgreSQL credentials from your cloud provider.

## Author

Project: EcoPackAI – AI-Powered Sustainable Packaging Recommendation System
