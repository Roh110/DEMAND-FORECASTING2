# 🔮 Project FORESIGHT

### Retail Demand Forecasting & Inventory Intelligence Platform

**Project FORESIGHT** is an end-to-end retail analytics and machine learning platform designed to help businesses understand sales performance, forecast future product demand, identify inventory risks, and convert analytical insights into actionable business recommendations.

The platform combines:

- 📊 Data Analytics
- 📈 Time-Series Feature Engineering
- 🤖 Machine Learning
- ⚠️ Inventory Risk Analysis
- 💰 Revenue-at-Risk Analysis
- 💡 Business Recommendations
- 🖥️ Streamlit Interactive Dashboard
- ☁️ Cloud Deployment
- 🤗 Hugging Face Artifact Storage

The application is deployed as a **fully Streamlit-based web application**, while large datasets and the production ML model are stored externally in a Hugging Face Dataset repository.

---

## 🚀 Live Demo

**Project FORESIGHT — Live Streamlit Application**

`https://project-foresight-webapp.streamlit.app/`

The deployed application provides access to all four major modules:

1. KPI Dashboard
2. Demand Forecasting
3. Inventory Risk Analysis
4. Business Recommendations

---

# 📌 Project Overview

Retail businesses commonly face two major inventory challenges:

### Excess Inventory

Excess stock can result in:

- Increased holding costs
- Overstocking
- Markdown requirements
- Reduced inventory turnover
- Capital being locked in unsold products

### Insufficient Inventory

Insufficient stock can result in:

- Stockouts
- Lost sales
- Missed revenue opportunities
- Poor customer experience
- Reduced product availability

Project FORESIGHT addresses these challenges by connecting:

```text
Historical Analytics
        ↓
Demand Forecasting
        ↓
Inventory Risk Detection
        ↓
Business Recommendations
```

The platform processes retail sales and inventory-related data and transforms the results into interactive business intelligence and predictive insights.

---

# 🎯 Key Features

## 📊 1. KPI Dashboard

The KPI Dashboard provides an executive-level overview of retail business performance.

### Key Metrics

- Total Revenue
- Total Profit
- Customers
- Products
- Stores

### Visualizations

- Monthly Revenue Trend
- Inventory Risk Distribution
- Inventory Action Distribution
- Top Revenue Categories
- Top Revenue-at-Risk Products

### Interactive Filtering

The dashboard supports filtering based on:

- Category
- SKU

This allows users to move from an overall business view to more granular product-level analysis.

---

# 🔮 2. Demand Forecasting

The Forecasting module provides SKU-level machine learning demand forecasting.

Users can:

- Select a SKU
- View historical weekly demand
- Generate a six-week demand forecast
- Compare historical demand with predicted demand
- View average forecast demand
- View the forecast trend
- Identify the associated inventory risk

### Forecast Horizon

The model generates predictions for:

```text
6 future weeks
```

---

# 🤖 Machine Learning Model

The forecasting model is based on:

```text
RandomForestRegressor
```

The original model used:

```text
100 trees
unrestricted tree depth
```

This resulted in a very large model of approximately:

```text
389 MB
```

The large model caused memory problems during free cloud deployment.

Therefore, a production-optimized Random Forest model was developed and evaluated against multiple smaller candidates.

### Production Model

```text
RandomForestRegressor

n_estimators     = 30
max_depth        = 12
min_samples_leaf = 2
random_state     = 42
```

### Production Model Size

Approximately:

```text
1.68 MB
```

This reduced the model size by more than **99%** compared with the original model.

---

# 📈 Model Evaluation

Four Random Forest configurations were evaluated using the same dataset and the same chronological 80/20 train-test split used by the original forecasting pipeline.

| Model | Trees | Max Depth | MAE | RMSE | R² | Size |
|---|---:|---:|---:|---:|---:|---:|
| RF Depth 20 | 50 | 20 | 3.7694 | 13.2032 | 0.9819 | 63.39 MB |
| RF Depth 15 | 50 | 15 | 3.8349 | 13.3235 | 0.9816 | 10.89 MB |
| RF Depth 15 | 30 | 15 | 3.8355 | 13.3912 | 0.9814 | 6.52 MB |
| **Production Model** | **30** | **12** | **3.9832** | **13.0601** | **0.9823** | **1.60 MB** |

The production model was selected because it achieved:

- Excellent predictive performance
- The lowest RMSE among the tested candidates
- The highest R² among the tested candidates
- Dramatically lower model size
- Much lower memory requirements for deployment

### Production Model Metrics

```text
MAE  = 3.9832
RMSE = 13.0601
R²   = 0.9823
```

> Model evaluation metrics are based on the project's existing forecasting dataset and chronological test split. They should not be interpreted as a guarantee of future production accuracy.

---

# 🧠 Forecast Features

The forecasting model uses engineered time-series and promotional features.

The 14 model features are:

```text
promo_count
has_promo
year
month
quarter
weekofyear
lag_1
lag_2
lag_4
lag_8
rolling_mean_4
rolling_mean_8
rolling_std_4
expanding_mean
```

### Feature Engineering

The forecasting preprocessing pipeline includes:

- Weekly sales aggregation
- Promotional activity aggregation
- Calendar features
- Lag features
- Rolling mean features
- Rolling standard deviation
- Expanding mean
- Promotion indicators

---

# ⚠️ 3. Inventory Risk Analysis

The Risk Analysis module classifies products into four operational categories.

| Risk Category | Meaning |
|---|---|
| 🔵 **MARKDOWN** | Excess inventory requiring reduction strategies |
| 🔴 **REORDER NOW** | Products requiring immediate replenishment |
| 🟢 **HEALTHY** | Inventory currently in a healthy position |
| 🟡 **WATCH** | Products requiring closer monitoring |

### Current Risk Dataset

The current risk dataset contains:

```text
21,228 products
```

Distribution:

```text
MARKDOWN      12,431
REORDER NOW    3,746
HEALTHY        2,897
WATCH          2,154
```

Approximate distribution:

```text
MARKDOWN       58.56%
REORDER NOW    17.65%
HEALTHY        13.65%
WATCH          10.15%
```

The risk analysis helps identify both:

- Excess inventory requiring markdown strategies
- Products requiring replenishment

---

# 💰 Revenue-at-Risk Analysis

Project FORESIGHT also identifies products associated with inventory risk and estimates revenue exposure.

This allows users to prioritize:

- High-risk products
- Potentially affected revenue
- Replenishment opportunities
- Markdown opportunities

The dashboard surfaces the highest revenue-at-risk products for easier business prioritization.

---

# 💡 4. Business Recommendations

The recommendation module converts analytical outputs into actionable business priorities.

### 🔴 REORDER NOW

Prioritize immediate replenishment to reduce potential stockout risk.

### 🟡 WATCH

Closely monitor inventory and demand before taking further action.

### 🔵 MARKDOWN

Consider:

- Promotional campaigns
- Discounts
- Pricing adjustments
- Inventory reduction strategies

to reduce excess inventory.

### 🟢 HEALTHY

Maintain the current inventory strategy while continuing regular monitoring.

---

# 🏗️ System Architecture

The current production architecture is intentionally lightweight so that the complete application can run on free Streamlit infrastructure.

```text
                    ┌──────────────────────┐
                    │    Retail Dataset    │
                    │ Sales / Inventory /  │
                    │ Product / Promotion  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Data Cleaning &      │
                    │ Feature Engineering  │
                    │     Notebooks        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Processed Parquet    │
                    │      Artifacts       │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ KPI Artifacts│ │ Risk Scoring │ │ Weekly Sales │
        │   Parquet    │ │   Parquet    │ │   Parquet    │
        └──────────────┘ └──────────────┘ └──────┬───────┘
                                                 │
                                                 ▼
                                      ┌────────────────────┐
                                      │ Production ML Model│
                                      │ Random Forest      │
                                      │      ~1.68 MB      │
                                      └──────────┬─────────┘
                                                 │
                                                 ▼
                                      ┌────────────────────┐
                                      │ Hugging Face       │
                                      │ Artifact Repository│
                                      └──────────┬─────────┘
                                                 │
                                                 ▼
                              ┌────────────────────────────────┐
                              │      Streamlit Application      │
                              │                                │
                              │  ┌────────┐ ┌───────────────┐  │
                              │  │  KPI   │ │  Forecasting  │  │
                              │  └────────┘ └───────────────┘  │
                              │                                │
                              │  ┌────────┐ ┌───────────────┐  │
                              │  │  Risk  │ │ Recommendations│ │
                              │  └────────┘ └───────────────┘  │
                              └────────────────────────────────┘
```

---

# ☁️ Production Deployment Architecture

The application is deployed through **Streamlit Community Cloud**.

Large artifacts are not committed to GitHub.

Instead:

```text
GitHub
   │
   │ Application Source Code
   ▼
Streamlit Community Cloud
   │
   │ downloads required artifacts
   ▼
Hugging Face Dataset Repository
   │
   ├── KPI artifacts
   ├── Risk data
   ├── Weekly sales data
   └── Production ML model
```

This architecture keeps the GitHub repository lightweight while allowing the deployed application to retrieve the required datasets and model dynamically.

---

# 🤗 Hugging Face Artifacts

The project uses a Hugging Face Dataset repository for large deployment artifacts.

Repository:

```text
sibamsen07/project-foresight-artifacts
```

The repository contains deployment resources such as:

```text
data/processed/risk_scoring.parquet
data/processed/weekly_sales.parquet

data/deployment/kpi_summary.parquet
data/deployment/monthly_revenue.parquet
data/deployment/category_revenue.parquet
data/deployment/revenue_risk.parquet

models/rf_30_depth12_leaf2.pkl
```

The production ML model is intentionally stored outside GitHub because of its binary size and deployment requirements.

---

# 📦 Data Scale

The project processes a large retail dataset.

| Dataset | Approximate Records |
|---|---:|
| Master Dataset | 9,959,019 |
| Weekly Sales | 738,143 |
| Inventory Risk | 21,228 |

The large raw and processed datasets are excluded from the GitHub repository.

Instead, deployment-specific artifacts are stored externally and downloaded when required.

---

# 🔄 Forecasting Workflow

```text
Raw Retail Sales
        ↓
Data Cleaning
        ↓
Weekly Aggregation
        ↓
Feature Engineering
        ↓
Lag Features
        ↓
Rolling Statistics
        ↓
Calendar Features
        ↓
Promotion Features
        ↓
Chronological Train/Test Split
        ↓
Random Forest Training
        ↓
Model Evaluation
        ↓
Production Model Optimization
        ↓
Six-Week Forecast
        ↓
Streamlit Visualization
```

---

# ⚠️ Inventory Risk Workflow

```text
Inventory Data
      +
Demand Information
      +
Inventory Metrics
      ↓
Risk Scoring
      ↓
Recommended Action
      │
      ├── MARKDOWN
      ├── REORDER NOW
      ├── WATCH
      └── HEALTHY
      ↓
Business Recommendations
```

---

# 🖥️ Dashboard Modules

## KPI Dashboard

Provides:

- Revenue
- Profit
- Customers
- Products
- Stores
- Monthly revenue trends
- Inventory risk distribution
- Inventory action distribution
- Top categories
- Revenue-at-risk products

---

## Forecasting

Provides SKU-level:

- Historical demand
- Weekly demand visualization
- Six-week ML forecast
- Average forecast demand
- Forecast trend
- Inventory risk

---

## Risk Analysis

Provides:

- Risk distribution
- Risk percentages
- Product-level filtering
- Risk summaries
- Business insights
- Recommended actions

---

## Business Recommendations

Provides:

- Recommendation summary
- Priority actions
- Risk distribution
- Executive insights
- Overall business priority

---

# 🧰 Technology Stack

## Programming

- Python

## Data Analysis

- Pandas
- NumPy
- Matplotlib

## Machine Learning

- Scikit-learn
- Random Forest Regression
- Feature Engineering
- Time-Series Feature Engineering

## Dashboard

- Streamlit

## Data Storage

- Parquet
- CSV

## Artifact Storage

- Hugging Face Hub

## Development

- Jupyter Notebook
- VS Code
- Git
- GitHub

## Deployment

- Streamlit Community Cloud
- Hugging Face Dataset Repository

---

# 📁 Project Structure

```text
Project-FORESIGHT/
│
├── app/
│   ├── app.py
│   │
│   ├── pages/
│   │   ├── 1_KPI_Dashboard.py
│   │   ├── 2_Forecasting.py
│   │   ├── 3_Risk_Analysis.py
│   │   └── 4_Recommendations.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── backend.py
│
├── api/
│   └── main.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── deployment/
│
├── models/
│   ├── forecast_model.pkl
│   ├── forecast_model_compressed.pkl
│   └── rf_30_depth12_leaf2.pkl
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_master_table_creation.ipynb
│   ├── 04_eda.ipynb
│   ├── 05_inventory_analysis.ipynb
│   ├── 06_forecast_preprocessing.ipynb
│   ├── 07_forecasting.ipynb
│   ├── 08_risk_scoring.ipynb
│   └── 09_dashboard.ipynb
│
├── reports/
│   └── screenshots/
│
├── create_kpi_artifacts.py
├── create_production_forecast_model.py
├── requirements.txt
├── .gitignore
└── README.md
```

> **Note:** Large datasets, trained model binaries, and environment configuration files are excluded from GitHub through `.gitignore`. Deployment artifacts are stored externally in the Hugging Face Dataset repository.

---

# ⚙️ Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/sibamsen/Project-FORESIGHT.git
cd Project-FORESIGHT
```

---

## 2. Create a virtual environment

### Windows

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

# ▶️ Run the Application Locally

The current production dashboard is **Streamlit-native**.

You do not need to start the FastAPI server to use the current dashboard.

Run:

```bash
streamlit run app/app.py
```

The application will open in the browser.

Typical local address:

```text
http://localhost:8501
```

---

# 🔐 Environment Configuration

The backend can retrieve large artifacts from the Hugging Face Dataset repository.

The repository is configured through:

```text
HF_ARTIFACT_REPO
```

Default repository:

```text
sibamsen07/project-foresight-artifacts
```

For local development, an environment variable can be used:

```env
HF_ARTIFACT_REPO=sibamsen07/project-foresight-artifacts
```

Never commit secrets or access tokens to GitHub.

---

# 🗃️ Local vs Deployment Data Loading

The application uses a simple fallback strategy.

### Local Development

If an artifact exists locally:

```text
local file
    ↓
use local artifact
```

### Cloud Deployment

If the artifact is not present locally:

```text
local file missing
       ↓
Hugging Face Hub
       ↓
download artifact
       ↓
use artifact
```

This allows the same application code to work both locally and on Streamlit Cloud.

---

# 🧪 Model Development

The forecasting model was developed through the following notebooks:

```text
06_forecast_preprocessing.ipynb
07_forecasting.ipynb
```

The preprocessing stage creates:

- Weekly sales
- Lag variables
- Rolling statistics
- Calendar features
- Promotion features

The forecasting notebook performs:

- Train/test split
- Model training
- Prediction
- Evaluation
- Feature importance analysis
- Model serialization

---

# 🏭 Production Model Optimization

The production model was optimized specifically for deployment constraints.

The comparison script:

```text
create_production_forecast_model.py
```

evaluates multiple Random Forest configurations.

Run:

```bash
python create_production_forecast_model.py
```

The script compares:

- MAE
- RMSE
- R²
- Model size
- Training time
- Tree depth

The selected production model is:

```text
rf_30_depth12_leaf2.pkl
```

---

# 📊 Why Model Optimization Was Necessary

The original Random Forest model was approximately:

```text
389 MB
```

Deploying the original model on free Streamlit infrastructure caused the application process to terminate when the forecasting model was loaded.

The optimized model is approximately:

```text
1.68 MB
```

This represents a model-size reduction of more than:

```text
99%
```

while maintaining excellent test-set performance.

The optimization allowed the ML forecasting functionality to remain available without requiring paid high-memory infrastructure.

---

# 🌐 Deployment

## Streamlit Community Cloud

The current application is deployed using Streamlit Community Cloud.

Deployment flow:

```text
GitHub Repository
       ↓
Streamlit Community Cloud
       ↓
Install requirements.txt
       ↓
Run app/app.py
       ↓
Download required Hugging Face artifacts
       ↓
Application becomes available online
```

### Production Application

```text
https://project-foresight-webapp.streamlit.app/
```

---

# 🤗 Hugging Face Artifact Storage

Large files are stored in:

```text
sibamsen07/project-foresight-artifacts
```

Example upload command:

```powershell
& "$env:APPDATA\Python\Python312\Scripts\hf.exe" upload `
    sibamsen07/project-foresight-artifacts `
    ".\models\rf_30_depth12_leaf2.pkl" `
    "models/rf_30_depth12_leaf2.pkl" `
    --repo-type dataset
```

The production model is therefore not required to be committed to GitHub.

---

# 🔄 Updating the Application

After making code changes:

```bash
git status
```

Stage the changes:

```bash
git add .
```

Commit:

```bash
git commit -m "Update Project FORESIGHT"
```

Push:

```bash
git push origin main
```

Streamlit Community Cloud can then rebuild the application from the updated GitHub repository.

---

# 🧠 Design Decisions

## Why Streamlit?

Streamlit provides a simple way to turn Python-based analytics and machine learning workflows into interactive web applications.

It is particularly suitable for:

- Data dashboards
- ML prototypes
- Business analytics applications
- Portfolio projects
- Rapid deployment

---

## Why Parquet?

Parquet provides efficient columnar storage for large tabular datasets.

It is used for processed artifacts such as:

```text
weekly_sales.parquet
risk_scoring.parquet
kpi_summary.parquet
monthly_revenue.parquet
category_revenue.parquet
revenue_risk.parquet
```

---

## Why Hugging Face for Artifacts?

The project's datasets and model binaries are too large or unnecessary to store directly in the GitHub source repository.

Hugging Face provides a convenient external artifact repository while keeping the GitHub repository lightweight.

---

# 📈 Business Value

Project FORESIGHT connects:

```text
Historical Analytics
        ↓
Demand Forecasting
        ↓
Risk Detection
        ↓
Business Recommendations
```

The platform can help businesses:

- Identify excess inventory
- Reduce potential stockout risk
- Prioritize replenishment
- Identify products requiring markdown
- Understand revenue exposure
- Monitor inventory risk
- Support data-driven decisions
- Improve inventory visibility

---

# 🎓 Learning Outcomes

This project provided practical experience with:

- Data preprocessing
- Large-scale tabular data
- Feature engineering
- Time-series feature construction
- Machine learning model training
- Model evaluation
- Model optimization
- Streamlit dashboard development
- Git/GitHub workflows
- External ML artifact storage
- Cloud deployment
- Memory-constrained deployment
- Production-oriented application design

---

# 🚧 Future Improvements

Potential future improvements include:

- [ ] Automated model retraining
- [ ] Forecast accuracy monitoring
- [ ] Model performance dashboard
- [ ] Automated inventory alerts
- [ ] Real-time data integration
- [ ] Production database integration
- [ ] Authentication and role-based access
- [ ] Advanced pricing optimization
- [ ] CI/CD pipeline
- [ ] Automated testing
- [ ] Dockerized deployment
- [ ] Production monitoring
- [ ] Model drift detection
- [ ] Automated artifact versioning
- [ ] More advanced forecasting algorithms
- [ ] Scenario-based demand forecasting

---

# 👨‍💻 Author

## Sibam Sen

**B.Tech — Electronics & Communication Engineering**

Areas of interest:

- Data Analytics
- Data Science
- Machine Learning
- Artificial Intelligence
- Backend Development
- Business Intelligence

---

# 📜 License

This project is currently intended for:

- Educational purposes
- Learning
- Demonstration
- Portfolio presentation

---

# ⭐ Project Summary

Project FORESIGHT demonstrates how a retail analytics workflow can be transformed into a complete decision-support platform.

The project combines:

```text
Data Engineering
      +
Data Analytics
      +
Machine Learning
      +
Inventory Risk Analysis
      +
Business Intelligence
      +
Cloud Deployment
```

into a single interactive application.

### Final Architecture

```text
                 PROJECT FORESIGHT
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
      Analytics     Forecasting      Risk
          │             │             │
          └─────────────┼─────────────┘
                        │
                        ▼
                Recommendations
                        │
                        ▼
                  Streamlit App
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        GitHub Source       Hugging Face
                              Artifacts
             │                     │
             └──────────┬──────────┘
                        ▼
               Streamlit Cloud
                        │
                        ▼
                 Live Web App
```

---

## 🔗 Links

**GitHub Repository**

`https://github.com/sibamsen/Project-FORESIGHT`

**Live Application**

`https://project-foresight-webapp.streamlit.app/`

**Hugging Face Artifacts**

`sibamsen07/project-foresight-artifacts`#   A I - B U I S N E S S - A N A L Y S I S  
 #   a n a l y s i s  
 