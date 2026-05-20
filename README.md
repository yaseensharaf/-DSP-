<div align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>
<img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
<img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white"/>
<img src="https://img.shields.io/badge/Status-Complete-success?style=for-the-badge"/>

<br/><br/>

# Intelligent Retail Demand Forecasting System

### Hybrid ARIMA-LSTM machine learning platform for retail sales forecasting and inventory optimisation


<br/>

</div>

---

## Table of Contents

1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Forecasting Model](#-forecasting-model)
5. [Tech Stack](#-tech-stack)
6. [Project Structure](#-project-structure)
7. [Getting Started](#-getting-started)
8. [Dashboard Features](#-dashboard-features)
9. [Data Pipeline](#-data-pipeline)
10. [Testing](#-testing)
11. [Known Limitations & Future Work](#-known-limitations--future-work)
12. [Developer](#-developer)

---

## 🌟 Overview

This project presents a fully functional **Intelligent Demand Planning System** designed to tackle one of retail's most persistent challenges: accurate product-level sales forecasting. Retailers operating with inaccurate forecasts face costly consequences — overstocking ties up capital, while stockouts drive customers away and erode revenue.

The system addresses this by combining a **hybrid ARIMA-LSTM machine learning engine** with a **real-time Flask web dashboard**, enabling retail managers to:

- Forecast monthly product sales up to **5 years ahead** (2024–2028)
- Identify **top-performing and underperforming** products across stores
- Receive **data-driven inventory recommendations** derived from cross-store market analysis
- Visualise **historical trends and future projections** in an interactive, accessible interface

The system was trained and validated on **H&M transactional sales data (2015–2023)**, supplemented with two additional external retail datasets to broaden market context and forecasting accuracy.


---

## ✨ Key Features

### 🤖 Hybrid Forecasting Engine
- **ARIMA** models linear seasonality and long-term sales trends per product
- **LSTM** network captures non-linear residual patterns ARIMA cannot explain
- **Weighted integration** (90% ARIMA + 10% LSTM) produces the final hybrid forecast
- Forecasts generated for **60 months** (January 2024 – December 2028)
- Products with fewer than 24 months of data are automatically excluded to ensure model stability

### 📊 Interactive Dashboard
- Browse and search all products from H&M and two external retail stores
- Filter by **product name, category, and store**
- View individual **interactive time-series charts** showing historical sales (2015–2023) and predictions (2024–2028)
- Toggle between **light and dark mode**
- Fully **responsive** — works on desktop, tablet, and mobile

### 📈 Business Intelligence Pages
- **Trending Products** — top performers by aggregated post-2023 sales volume
- **Lowest-Selling Products** — five weakest H&M products flagged for action
- **Recommendations** — high-performing external products suggested to replace underperforming H&M inventory
- **All Products** — complete cross-store product catalogue with dynamic search and category filtering

### 🗂️ Data Management
- Automated **CSV export** of all forecast outputs
- Consolidated **Excel report** (`ALL_H&M.xlsx`) merging historical and predicted data for all products
- Modular preprocessing pipeline handles missing values, date standardisation, and monthly resampling

---

## 🏗️ System Architecture

The system is structured into three cleanly separated layers:

```
┌──────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                        │
│                                                                  │
│   Flask Web Server · HTML/CSS/JS · Bootstrap · Jinja2 Templates  │
│   Dashboard Pages: Home · Trending · Lowest · Recommend · Help  │
└────────────────────────────┬─────────────────────────────────────┘
                             │  HTTP requests / template rendering
┌────────────────────────────▼─────────────────────────────────────┐
│                       Application Layer                          │
│                                                                  │
│   Data Preprocessing Pipeline  ──►  Hybrid Forecasting Engine   │
│   (Pandas: resample, impute,         (ARIMA → residuals → LSTM   │
│    feature engineering)               → weighted integration)    │
│                                                                  │
│   Recommendation Engine  ·  Product Insights Aggregator         │
└────────────────────────────┬─────────────────────────────────────┘
                             │  reads / writes
┌────────────────────────────▼─────────────────────────────────────┐
│                          Data Layer                              │
│                                                                  │
│   H_M.csv (2015–2023)  ·  Retail_Store_1/  ·  Retail_Store_2/   │
│   Sales_Forecast_Results_with_Accuracy/  ·  ALL_H&M.xlsx         │
│   static/images/  (product image rendering)                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Forecasting Model

The forecasting pipeline follows a sequential four-stage process:

### Stage 1 — Data Preparation
- Load H&M and external store datasets from CSV into Pandas DataFrames
- Standardise `SaleDate` to datetime index using `to_datetime()`
- Resample to **monthly intervals** using `resample('M').sum()` to reduce noise and surface seasonality
- Impute missing values via **forward-fill** and **linear interpolation**
- Engineer temporal features: `Month`, `Year`, `Season` for cyclical learning

### Stage 2 — ARIMA Modelling
- Apply `auto_arima()` (pmdarima) per product to automatically select optimal `(p, d, q)` and seasonal `(P, D, Q, m=12)` parameters by minimising **AIC and BIC**
- Train on 2015–2023 data and project a **60-month forecast** (2024–2028)
- Compute **residuals** = actual values − ARIMA predictions (capturing unexplained variance)

### Stage 3 — LSTM Residual Modelling
- Scale residuals to zero mean and unit variance using `StandardScaler`
- Build input sequences with a **3-month sliding window**
- LSTM architecture:
  ```
  Input → LSTM(100 units, ReLU) → Dropout(20%)
        → LSTM(50 units, ReLU)  → Dropout(20%)
        → Dense(1)
  ```
- Compiled with **Adam optimiser** and **MSE loss**; trained for 100 epochs, batch size 16
- Inverse-transform predicted residuals back to original scale

### Stage 4 — Hybrid Integration
```
Final Forecast = (0.90 × ARIMA Forecast) + (0.10 × LSTM Residual Forecast)
```
- Outputs rounded to nearest integer and floored at 1 to prevent negative predictions
- Results exported as **CSV** and **PNG** visualisation per product

```
Historical Sales (solid blue) ────────────┐
                                           ├──► Merged Chart per Product
Predicted Sales (dashed red) ─────────────┘
```

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.x | All backend logic, modelling, and data processing |
| **Deep Learning** | TensorFlow / Keras | LSTM model architecture and training |
| **Statistical ML** | pmdarima / Statsmodels | ARIMA model fitting with auto-parameter selection |
| **Data Processing** | Pandas, NumPy | Data loading, resampling, feature engineering |
| **Preprocessing** | Scikit-learn | StandardScaler for residual normalisation |
| **Visualisation** | Matplotlib, Plotly | Forecast plots and dashboard charts |
| **Web Framework** | Flask | Backend server and REST API endpoints |
| **Frontend** | HTML, CSS, JavaScript, Bootstrap | Responsive dashboard UI |
| **Templating** | Jinja2 | Dynamic page rendering |
| **API Testing** | Postman | Endpoint validation and error-case testing |
| **Data Format** | CSV, Excel (`.xlsx`) | Dataset storage and forecast export |
| **Methodology** | CRISP-DM + Agile Scrum | Project planning and iterative development |

---

## 📂 Project Structure

```
Intelligent-Retail-Demand-Forecasting-System/
│
├── Retail_Store_1/                        ← External retail dataset 1 (CSV files)
│
├── Retail_Store_2/                        ← External retail dataset 2 (CSV files)
│
├── Sales_Forecast_Results_with_Accuracy/  ← Generated forecast outputs
│   ├── <ProductName>_forecast.csv         ← Per-product hybrid forecast (2024–2028)
│   └── <ProductName>_forecast.png         ← Per-product time-series plot
│
├── data/                                  ← Raw datasets
│   └── H_M.csv                            ← Primary H&M sales data (2015–2023)
│
├── src/                                   ← Forecasting model source code
│   └── *.py                               ← ARIMA, LSTM, hybrid pipeline scripts
│
├── static/                                ← Frontend static assets
│   ├── css/                               ← Stylesheets (light and dark mode)
│   ├── js/                                ← JavaScript (dark mode toggle, filtering)
│   └── images/                            ← Product images for dynamic rendering
│
├── templates/                             ← Flask HTML templates (Jinja2)
│   ├── index.html                         ← Home — H&M product dashboard
│   ├── trending.html                      ← Top-selling products page
│   ├── lowest.html                        ← Lowest-selling products page
│   ├── recommend.html                     ← Inventory recommendations page
│   ├── all_products.html                  ← Full cross-store product catalogue
│   └── help.html                          ← User guidance and feature documentation
│
├── app.py                                 ← Flask application entry point
├── H_M.ipynb                              ← H&M data exploration and model notebook
├── R1.ipynb                               ← Retail Store 1 analysis notebook
├── R2.ipynb                               ← Retail Store 2 analysis notebook
└── tempCodeRunnerFile.py                  ← IDE temp file (safe to ignore)
```

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version |
|---|---|
| Python | 3.8 or later |
| pip | Latest |
| Git | Any recent version |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yaseensharaf/-DSP-.git
cd -DSP-

# 2. Create and activate a virtual environment (recommended)
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt
```

### Dependencies

If no `requirements.txt` is present, install manually:

```bash
pip install flask pandas numpy matplotlib scikit-learn tensorflow \
            pmdarima statsmodels plotly openpyxl bootstrap-flask
```

### Generate Forecasts

Run the forecasting notebooks or pipeline scripts first to produce all CSV and PNG outputs.
You can use the provided Jupyter notebooks:

```bash
# Open notebooks for each dataset
jupyter notebook H_M.ipynb     # H&M forecasting pipeline
jupyter notebook R1.ipynb      # Retail Store 1 analysis
jupyter notebook R2.ipynb      # Retail Store 2 analysis
```

Or run the forecasting scripts directly from `src/`:

```bash
python src/<forecasting_script>.py
```

This will:
- Load and preprocess all datasets
- Train ARIMA and LSTM models for each eligible product
- Generate 60-month hybrid forecasts
- Export results to `Sales_Forecast_Results_with_Accuracy/`

### Launch the Dashboard

```bash
python app.py
```

Then open your browser and navigate to:

```
http://127.0.0.1:5000
```

---

## 📱 Dashboard Features

### Home — Product Dashboard
The default view displays all H&M products in a card-based grid. Each card shows the product image, name, category, and price. Users can search by keyword or filter by category in real time without a page reload.

### Trending Products
Aggregates post-2023 predicted sales across all three stores and ranks products by total volume. Designed to help managers prioritise restocking of high-demand items.

### Lowest-Selling Products
Displays the five H&M products with the weakest post-2023 predicted performance. Intended to trigger review decisions — whether to discount, promote, or replace these items.

### Recommendations
Identifies high-performing products from the two external retail datasets that do not currently appear in H&M's catalogue. These are surfaced as potential additions to inventory, ranked by external sales performance within matching categories.

### All Products
A unified catalogue combining products from all three stores. Supports filtering by store, category, and product name simultaneously. Used for broad market comparison and competitor benchmarking.

### Help
A plain-language guide explaining how to navigate the dashboard, interpret forecast charts, and use the filtering and recommendation features. Designed for non-technical retail managers.

---

## 🔄 Data Pipeline

```
Raw CSV Files (H&M + Store 1 + Store 2)
        │
        ▼
  Load with Pandas
        │
        ▼
  Standardise SaleDate → datetime index
        │
        ▼
  Monthly Resampling → resample('M').sum()
        │
        ▼
  Missing Value Imputation → forward-fill + linear interpolation
        │
        ▼
  Feature Engineering → Month, Year, Season
        │
        ▼
  Filter products with < 24 months data (excluded)
        │
        ▼
  ARIMA Training → auto_arima() → 60-month forecast
        │
        ▼
  Residual Computation → actual − ARIMA forecast
        │
        ▼
  StandardScaler → normalise residuals
        │
        ▼
  LSTM Training → 3-month sliding window → residual prediction
        │
        ▼
  Inverse Transform → rescale residuals
        │
        ▼
  Hybrid Integration → (0.9 × ARIMA) + (0.1 × LSTM)
        │
        ▼
  Export → CSV + PNG per product + ALL_H&M.xlsx
        │
        ▼
  Flask Dashboard → interactive visualisation
```

---

## 🧪 Testing

A structured multi-layer testing strategy was applied across all system components:

| Test ID | Module | Type | Result |
|---|---|---|---|
| T1 | Forecast folder creation | File system validation | ✅ Passed |
| T2 | Dataset loading and preprocessing | Data validation | ✅ Passed |
| T3 | ARIMA model training | Model training test | ✅ Passed |
| T4 | Residual computation | Data processing validation | ✅ Passed |
| T5 | LSTM model training | Model training test | ✅ Passed |
| T6 | Hybrid forecast integration | Integration test | ✅ Passed |
| T7 | Forecast CSV and PNG export | File export test | ✅ Passed |
| T8 | Dashboard page navigation | UI navigation test | ✅ Passed |
| T9 | Product image API endpoint | API response test | ✅ Passed |
| T10 | Product sales data API endpoint | API response test | ✅ Passed |
| T11 | Cross-browser compatibility | Browser test (Chrome, Firefox, Edge, Safari) | ✅ Passed |
| T12 | Dark mode toggle | UI functionality test | ✅ Passed |

**Testing tools used:** Manual browser testing · Postman (API endpoints) · Python assertions (model outputs)

---

## ⚠️ Known Limitations & Future Work

### Current Limitations

| Area | Limitation |
|---|---|
| **Forecast accuracy** | Hybrid model is less reliable for products with highly volatile or sparse sales histories |
| **Real-time updates** | Dashboard requires a manual refresh to reflect new forecast data |
| **Scalability** | Flat CSV storage does not scale well beyond a small number of stores |
| **Automated testing** | No Pytest or Selenium suite; testing was primarily manual |
| **Hyperparameter tuning** | LSTM architecture was not exhaustively tuned across all product types |

### Proposed Future Enhancements

- **Advanced models** — evaluate Facebook Prophet, XGBoost, or Temporal Fusion Transformers for improved accuracy on volatile products
- **Real-time dashboard** — integrate Flask-SocketIO for live data streaming without page reloads
- **Database migration** — replace CSV storage with PostgreSQL for multi-user access and faster querying
- **Automated testing** — implement Pytest (unit/integration) and Selenium (UI) test suites with CI/CD integration
- **User research** — conduct usability studies with retail managers to inform future dashboard features and workflows

---

## 👨‍💻 Developer



[![GitHub](https://img.shields.io/badge/GitHub-yaseensharaf-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yaseensharaf)



---

## 📄 License

```
Copyright © 2025 Yaseen Sharaf. All rights reserved.
Developed as a final-year academic project — UXCFXK-30-3 Digital Systems Project.
Unauthorised commercial use or redistribution is not permitted.
```
