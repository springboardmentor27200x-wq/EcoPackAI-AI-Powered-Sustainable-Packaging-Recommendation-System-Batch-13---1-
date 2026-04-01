
# 🌿 EcoPackAI – AI-Powered Sustainable Packaging Recommendation System

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue)
![Render](https://img.shields.io/badge/Deployed-Render-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

> An AI-powered full-stack web platform that recommends optimal eco-friendly packaging materials based on product attributes, sustainability parameters, and industry standards.

🔗 **Live Demo:** [https://ecopack-qbsi.onrender.com](https://ecopack-qbsi.onrender.com)

---

## 📌 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [ML Models](#ml-models)
- [Project Structure](#project-structure)
- [Installation & Local Setup](#installation--local-setup)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [BI Dashboard](#bi-dashboard)
- [Deployment](#deployment)
- [Future Scope](#future-scope)

---

## 📖 Overview

Traditional packaging in industries and e-commerce heavily relies on non-biodegradable and costly materials, causing increasing environmental damage and financial inefficiency. **EcoPackAI** solves this by:

- Recommending optimal packaging materials using Machine Learning
- Predicting environmental impact (CO₂ footprint) and cost efficiency
- Providing a Business Intelligence dashboard for sustainability insights
- Supporting data-driven decisions towards greener supply chains

---

## ✨ Features

- 🤖 AI-powered material recommendation engine (Random Forest + XGBoost)
- 📊 BI Dashboard with CO₂ savings and cost analytics
- 🗄️ PostgreSQL cloud database integration
- 🌐 REST API with Flask backend
- 📱 Responsive UI with Bootstrap
- 📄 Sustainability report export (PDF/Excel)
- 🚀 Deployed on Render with cloud PostgreSQL

---

## 🏗️ System Architecture

```
User Interface (HTML + Bootstrap + JavaScript)
        ↓
Flask Backend API (REST Endpoints)
        ↓              ↓
AI/ML Layer        PostgreSQL Database
(Random Forest,    (Cloud - Render)
 XGBoost)
        ↓
Business Intelligence Dashboard
        ↓
Deployment Layer (Render)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Bootstrap, JavaScript |
| Backend | Python, Flask 3.1.3 |
| ML Models | scikit-learn, XGBoost |
| Database | PostgreSQL 18 |
| Data Processing | Pandas, NumPy, SciPy |
| Visualization | Matplotlib, Plotly |
| Deployment | Render (Web Service + PostgreSQL) |
| Version Control | Git, GitHub |

---

## 🤖 ML Models

### 1. Random Forest Regressor — Cost Prediction
- Predicts packaging cost based on material attributes
- Features: material type, weight capacity, strength, recyclability %
- Evaluation: RMSE, MAE, R² Score

### 2. XGBoost Regressor — CO₂ Footprint Prediction
- Predicts environmental impact of packaging materials
- Features: biodegradability score, CO₂ emission index, material suitability score
- Evaluation: RMSE, MAE, R² Score

### Feature Engineering
- **CO₂ Impact Index** — derived from emission score and material type
- **Cost Efficiency Index** — normalized cost vs durability ratio
- **Material Suitability Score** — composite score for product-material compatibility

---

## 📁 Project Structure

```
EcoPack/
└── sustainable_material_ai/
    ├── app.py                  # Main Flask application
    ├── Procfile                # Render/Heroku process file
    ├── requirements.txt        # Python dependencies
    ├── models/                 # Trained ML model files
    │   ├── cost_model.pkl
    │   └── co2_model.pkl
    ├── static/                 # CSS, JS, images
    └── templates/              # HTML templates
        ├── index.html
        ├── dashboard.html
        └── results.html
```

---

## ⚙️ Installation & Local Setup

### Prerequisites
- Python 3.14+
- PostgreSQL installed locally
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/N-BKM/EcoPack.git
cd EcoPack/sustainable_material_ai

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
# Create a .env file or set directly:
set DATABASE_URL=your_postgresql_connection_url   # Windows
export DATABASE_URL=your_postgresql_connection_url # Mac/Linux

# 5. Run the application
python app.py
```

The app will be available at `http://localhost:5000`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page — product input form |
| POST | `/recommend` | Submit product attributes, get AI material recommendations |
| GET | `/dashboard` | BI Dashboard with analytics |
| GET | `/api/materials` | Returns all materials from database (JSON) |
| POST | `/api/predict` | Returns cost and CO₂ predictions for a material (JSON) |

### Sample Request — `/api/predict`

```json
POST /api/predict
Content-Type: application/json

{
  "material_type": "Recycled Cardboard",
  "weight_capacity": 5.0,
  "strength": 8,
  "product_category": "electronics"
}
```

### Sample Response

```json
{
  "material": "Recycled Cardboard",
  "predicted_cost": 2.35,
  "predicted_co2": 0.84,
  "suitability_score": 87.4,
  "recommendation_rank": 1
}
```

---

## 🗄️ Database Schema

### `materials` Table
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique material ID |
| material_type | VARCHAR | Name of the material |
| strength | FLOAT | Strength rating (1–10) |
| weight_capacity | FLOAT | Max weight in kg |
| biodegradability_score | FLOAT | Score 0–100 |
| co2_emission_score | FLOAT | CO₂ emission index |
| recyclability_pct | FLOAT | Recyclability percentage |
| cost_per_unit | FLOAT | Cost in USD |

### `products` Table
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique product ID |
| product_name | VARCHAR | Product name |
| category | VARCHAR | Industry category |
| weight | FLOAT | Product weight |
| fragility | VARCHAR | Fragility level |

---

## 📊 BI Dashboard

The Business Intelligence Dashboard provides:

- 📉 CO₂ reduction percentage compared to traditional packaging
- 💰 Cost savings analysis across material categories
- 📈 Material usage trends over time
- 🌱 Biodegradability comparison charts
- 📄 Export sustainability reports in PDF/Excel format

---

## 🚀 Deployment

The application is deployed on **Render** with the following setup:

- **Web Service**: Python 3 / Flask via Gunicorn
- **Database**: PostgreSQL 18 (Cloud instance on Render)
- **Root Directory**: `sustainable_material_ai`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Environment Variable**: `DATABASE_URL` (Internal PostgreSQL URL)

### Render Configuration

```
Root Directory:   sustainable_material_ai
Build Command:    pip install -r requirements.txt
Start Command:    gunicorn app:app
```

---

## 🔮 Future Scope

- Integration with live supply chain APIs for real-time material pricing
- Mobile application for on-the-go packaging recommendations
- Multi-language support for global adoption
- Advanced NLP for product description-based recommendations
- Carbon credit tracking and reporting module

---

## 👤 Author

**NIRANJAN B**
GitHub: [@N-BKM](https://github.com/N-BKM)

---

## 📃 License

This project is licensed under the MIT License.

---

*Developed as part of an AI internship project focused on sustainable packaging innovation.*
