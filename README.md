<div align="center">

# Aadhaar Analytics Platform

**UIDAI Data Hackathon 2026 Submission**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

An end-to-end analytics platform that transforms UIDAI enrollment and biometric data into actionable intelligence for policy evaluation, resource optimization, and strategic planning.

</div>

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Features](#features)
- [Technical Architecture](#technical-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Novel Contributions](#novel-contributions)
- [Team](#team)
- [License](#license)

---

## Problem Statement

UIDAI manages billions of Aadhaar transactions across India but faces critical analytical gaps:

| Challenge | Current State | Impact |
|-----------|---------------|--------|
| **Enrollment-Usage Mismatch** | Regions with high enrollment but low biometric usage remain unidentified | Wasted infrastructure investment |
| **Policy Effectiveness** | No systematic method to measure if enrollment campaigns lead to lasting behavioral change | Inability to optimize campaign strategies |
| **Resource Allocation** | Reactive rather than predictive allocation of enrollment infrastructure | Suboptimal coverage and service delays |
| **Demographic Insights** | Limited understanding of age cohort patterns and regional variations | Missed opportunities for targeted interventions |

---

## Solution Overview

We developed a comprehensive analytics platform with six integrated modules:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Aadhaar Analytics Platform                    │
├─────────────────────────────────────────────────────────────────┤
│  📌 Overview          │  Landing page with platform guide       │
│  🏠 Executive Summary │  High-level KPIs and trend indicators   │
│  📋 Detailed Analysis │  Multi-dimensional data exploration     │
│  🔮 Predictive        │  ML-powered enrollment forecasting      │
│  🔍 Data Explorer     │  Interactive data tables & anomalies    │
│  ⚖️ EUMI Analysis     │  Enrollment-Usage Mismatch Index        │
│  📉 Policy Shock      │  Campaign impact measurement            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

### 1. Executive Summary Dashboard
- Real-time KPIs: Total enrollments, biometric usage, state coverage
- Trend indicators with period-over-period comparisons
- Geographic distribution heatmaps
- State-level filtering across all visualizations

### 2. Detailed Analysis Module
Three analytical perspectives:

| Tab | Analysis Type | Key Insights |
|-----|---------------|--------------|
| **Biometric vs Demographic** | Processing ratio analysis | Identifies authentication efficiency by region |
| **Geographic Analysis** | Pareto distribution | 80/20 analysis of state-wise enrollment contribution |
| **Age Cohort** | Enrollment efficiency | Age group performance and demographic targeting |

### 3. Predictive Analytics
- **Model**: Random Forest Regressor with feature engineering
- **Predictions**: 30-day rolling enrollment forecasts
- **Inputs**: Historical patterns, seasonal indicators, trend components
- **Output**: Confidence intervals with actionable recommendations

### 4. Data Explorer
- Interactive sortable and filterable data tables
- IQR-based anomaly detection with visual highlighting
- Statistical summaries (mean, median, std, min, max)
- District-level drill-down capabilities

### 5. EUMI Analysis (Enrollment-Usage Mismatch Index)
A novel metric we developed to identify resource allocation inefficiencies:

```
EUMI = (District Biometric Share ÷ District Enrollment Share)

Interpretation:
├── EUMI < 0.8  → Over-enrolled, Under-utilized (Infrastructure waste)
├── EUMI = 1.0  → Balanced (Optimal allocation)
└── EUMI > 1.2  → Under-enrolled, High-usage (Infrastructure stress)
```

**Visualizations:**
- Quadrant scatter plot (Enrollment Share vs Usage Share)
- District categorization with actionable recommendations
- Top/Bottom performers ranking

### 6. Policy Shock Impact Analyzer
Measures the lasting impact of enrollment campaigns:

**Methodology:**
1. **Shock Detection**: Identifies months with enrollment > mean + 1.5σ
2. **Impact Window**: Compares 30 days before vs 30 days after
3. **KPI Calculation**:
   - Biometric Persistence Ratio (post_avg ÷ pre_avg)
   - Youth Adoption Change (post_youth% − pre_youth%)
   - District Expansion Rate (coverage change %)

**Classification System:**

| Classification | Criteria | Interpretation |
|----------------|----------|----------------|
| 🟡 Enrollment-Only | Low persistence, stable demographics | Temporary drive, no lasting impact |
| 🟢 Behavioral Adoption | High persistence, youth increase | Successful behavioral change |
| 🔵 Structural Expansion | New districts activated | Geographic coverage expansion |

**Dynamic Insights:**
- Every visualization includes auto-generated data-driven interpretations
- Actionable recommendations based on calculated metrics
- Contextual analysis for stakeholder decision-making

---

## Technical Architecture

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Streamlit 1.30+ | Interactive web application |
| Visualization | Plotly 5.18+ | Interactive charts and graphs |
| Data Processing | Pandas 2.0+, NumPy | Data manipulation and analysis |
| Machine Learning | Scikit-learn | Predictive modeling |
| Styling | Custom CSS | Glassmorphism UI design |

### Data Pipeline

```
UIDAI Datasets (3)
       │
       ▼
┌─────────────────┐
│  Data Loading   │ ← CSV parsing with error handling
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocessing  │ ← Date parsing, type conversion, validation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Aggregation   │ ← State/District/Monthly groupings
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Analytics     │ ← EUMI, Policy Shock, Predictions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Visualization   │ ← Interactive Plotly charts
└─────────────────┘
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- 4GB RAM minimum (8GB recommended for large datasets)

### Setup

```bash
# Clone the repository
git clone https://github.com/RAR2025/BharatBytes-UIDAI.git
cd BharatBytes-UIDAI

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
```
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
scikit-learn>=1.3.0
```

---

## Usage

### Running the Application

```bash
streamlit run streamlit_app.py
```

Access the dashboard at `http://localhost:8501`

### Navigation
1. **Overview**: Start here for platform introduction
2. **Executive Summary**: Quick KPI snapshot
3. **Detailed Analysis**: Deep-dive into specific dimensions
4. **Predictive**: View enrollment forecasts
5. **Data Explorer**: Browse and filter raw data
6. **EUMI Analysis**: Identify mismatch districts
7. **Policy Shock Analyzer**: Evaluate campaign effectiveness

### State Filtering
Use the sidebar dropdown to filter all analyses by specific states.

---

## Project Structure

```
BharatBytes-UIDAI/
├── streamlit_app.py              # Main application (2400+ lines)
├── uidai_comprehensive_analysis.py  # Standalone analysis module
├── sort_by_pincode.py            # Utility script
├── requirements.txt              # Python dependencies
├── LICENSE                       # MIT License
├── README.md                     # This file
├── UIDAI Dataset 1/              # Biometric authentication data
├── UIDAI Dataset 2/              # Demographic data
├── UIDAI Dataset 3/              # Enrollment data
└── outputs/                      # Generated visualizations
```

---

## Novel Contributions

### 1. EUMI (Enrollment-Usage Mismatch Index)
First systematic metric to quantify the gap between Aadhaar enrollment and actual biometric usage at the district level.

### 2. Policy Shock Classification Framework
Novel methodology to categorize enrollment campaign impacts into actionable categories with specific intervention recommendations.

### 3. Dynamic Insight Engine
Auto-generated, data-driven interpretations that adapt language and recommendations based on actual metric values.

### 4. Cross-Dataset Normalization
Unified analysis framework that combines enrollment, biometric, and demographic datasets for holistic insights.

---

## Team

### Team Bharat Bytes

| Member | Role | GitHub |
|--------|------|--------|
| **Vedang Mendhurwar** | Team Leader | [@Vedang-M](https://github.com/Vedang-M) |
| **Ruturaj Rajwade** | Developer | [@RAR2025](https://github.com/RAR2025) |
| **Shreya Dandekar** | Developer | [@shreyadandekar](https://github.com/shreyadandekar) |
| **Harshal Pednekar** | Developer | [@harshalnnpednekar](https://github.com/harshalnnpednekar) |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**UIDAI Data Hackathon 2026** | Team Bharat Bytes

</div>
