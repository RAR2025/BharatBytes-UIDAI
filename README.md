<div align="center">

# 🇮🇳 Aadhaar Analytics Platform

**UIDAI Data Hackathon 2026 Submission**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Click_Here-FF4B4B?style=for-the-badge)](https://bharatbytes-uidai-ylygudcjhgpkrhixwpld8s.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

*An end-to-end analytics platform that transforms UIDAI enrollment and biometric data into actionable intelligence for policy evaluation, resource optimization, and strategic planning.*

**[🚀 Try the Live Demo](https://bharatbytes-uidai-ylygudcjhgpkrhixwpld8s.streamlit.app/)**

</div>

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [Features](#-features)
- [Novel Contributions](#-novel-contributions)
- [Technical Architecture](#-technical-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Team](#-team)
- [License](#-license)

---

## 🎯 Problem Statement

UIDAI manages billions of Aadhaar transactions across India but faces critical analytical gaps:

| Challenge | Current State | Impact |
|-----------|---------------|--------|
| **Enrollment-Usage Mismatch** | Regions with high enrollment but low biometric usage remain unidentified | Wasted infrastructure investment |
| **Policy Effectiveness** | No systematic method to measure if enrollment campaigns lead to lasting behavioral change | Inability to optimize campaign strategies |
| **Resource Allocation** | Reactive rather than predictive allocation of enrollment infrastructure | Suboptimal coverage and service delays |
| **Infrastructure Readiness** | Limited visibility into ground-level digital infrastructure stress and capacity | Service delivery failures |

---

## 💡 Solution Overview

We developed a comprehensive analytics platform with **eight integrated modules**:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Aadhaar Analytics Platform                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│  📌 Overview                    │  Landing page with platform guide             │
│  🏠 Executive Summary           │  High-level KPIs and trend indicators         │
│  📋 Detailed Analysis           │  Multi-dimensional data exploration           │
│  🔮 Predictive Analytics        │  ML-powered enrollment forecasting            │
│  🔍 Data Explorer               │  Interactive data tables & anomaly detection  │
│  ⚖️ EUMI Analysis               │  Enrollment-Usage Mismatch Index              │
│  📉 Policy Shock Analyzer       │  Campaign impact measurement                  │
│  🌐 Digital Infrastructure      │  Infrastructure stress & readiness scores     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 1. Executive Summary Dashboard
- Real-time KPIs: Total enrollments, biometric usage, state/UT coverage
- Trend indicators with period-over-period comparisons
- State-level filtering across all visualizations
- Geographic distribution analysis

### 2. Detailed Analysis Module
Three analytical perspectives with dynamic insights:

| Tab | Analysis Type | Key Insights |
|-----|---------------|--------------|
| **Biometric vs Demographic** | Processing ratio analysis | Identifies authentication efficiency by region |
| **Geographic Analysis** | Pareto distribution | 80/20 analysis of state-wise enrollment contribution |
| **Age Cohort** | Enrollment efficiency | Age group performance with effort-weighted analysis |

### 3. Predictive Analytics
- **Model**: Random Forest Classifier with feature engineering
- **Accuracy**: 80.63% with ROC-AUC of 0.7863
- **Features**: 9 engineered features including lag variables and demographic ratios
- **Output**: High-backlog state predictions with feature importance analysis

### 4. Data Explorer
- Interactive sortable and filterable data tables
- IQR-based anomaly detection with visual highlighting
- Statistical summaries (mean, median, std, CV)
- District-level drill-down and efficiency rankings

### 5. EUMI Analysis (Enrollment-Usage Mismatch Index)
A **novel metric** we developed to identify resource allocation inefficiencies:

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
Measures the **lasting impact** of enrollment campaigns:

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

### 7. Digital Infrastructure Readiness
Analyzes the gap between reported digital infrastructure and actual ground-level patterns:

**Three District-Level Indices:**
- **Infrastructure Stress Index (ISI)**: Measures volatility and capacity stress
- **Reporting Consistency Score (RCS)**: Measures regularity of data reporting
- **Age Balance Score (ABS)**: Measures equity across age demographics

**Four District Typologies:**

| Typology | Characteristics | Recommended Action |
|----------|-----------------|-------------------|
| Digitally Strong & Balanced | Low stress, High consistency, High balance | Model for replication |
| Digitally Strong but Overburdened | High stress, High consistency | Capacity expansion needed |
| Digitally Weak but Stable | Low stress, Low consistency | Infrastructure investment |
| Digitally Underserved | Low consistency, Low balance | Priority comprehensive intervention |

---

## 🚀 Novel Contributions

### 1. EUMI (Enrollment-Usage Mismatch Index)
First systematic metric to quantify the gap between Aadhaar enrollment and actual biometric usage at the district level.

### 2. Policy Shock Classification Framework
Novel methodology to categorize enrollment campaign impacts into actionable categories with specific intervention recommendations.

### 3. Digital Infrastructure Readiness Indices
Three-index framework (ISI, RCS, ABS) to assess ground-level digital infrastructure health and classify districts for targeted interventions.

### 4. Dynamic Insight Engine
Auto-generated, data-driven interpretations that adapt language and recommendations based on actual metric values.

### 5. Cross-Dataset Normalization
Unified analysis framework that combines enrollment, biometric, and demographic datasets for holistic insights.

---

## 🏗️ Technical Architecture

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
│   Analytics     │ ← EUMI, Policy Shock, Infrastructure Indices
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Visualization   │ ← Interactive Plotly charts
└─────────────────┘
```

---

## 📦 Installation

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
pandas
streamlit
plotly
numpy
scikit-learn
seaborn
matplotlib
```

---

## 🚀 Usage

### Running the Application

```bash
streamlit run streamlit_app.py
```

Access the dashboard at `http://localhost:8501`

### Live Demo
🔗 **[https://bharatbytes-uidai-ylygudcjhgpkrhixwpld8s.streamlit.app/](https://bharatbytes-uidai-ylygudcjhgpkrhixwpld8s.streamlit.app/)**

### Navigation Guide
1. **Overview**: Start here for platform introduction
2. **Executive Summary**: Quick KPI snapshot
3. **Detailed Analysis**: Deep-dive into specific dimensions
4. **Predictive**: View ML-powered forecasts
5. **Data Explorer**: Browse and filter raw data
6. **EUMI Analysis**: Identify mismatch districts
7. **Policy Shock Analyzer**: Evaluate campaign effectiveness
8. **Digital Infrastructure Readiness**: Assess infrastructure health

### State Filtering
Use the sidebar dropdown to filter all analyses by specific states or union territories.

---

## 📁 Project Structure

```
BharatBytes-UIDAI/
├── streamlit_app.py                       # Main application (2700+ lines)
├── digital_infrastructure_readiness.py   # Infrastructure analysis module
├── uidai_comprehensive_analysis.py       # Standalone analysis module
├── consolidate_and_normalize.py          # Data preprocessing utilities
├── aadhaar_biometric_analysis.py         # Biometric analysis scripts
├── aadhaar_demographic_analysis.py       # Demographic analysis scripts
├── aadhaar_enrolment_analysis.py         # Enrollment analysis scripts
├── eumi_calculation.py                   # EUMI computation module
├── requirements.txt                       # Python dependencies
├── LICENSE                                # MIT License
├── README.md                              # This file
├── api_data_aadhar_enrolment/            # Enrollment data (raw)
├── api_data_aadhar_demographic/          # Demographic data (raw)
├── api_data_aadhar_biometric/            # Biometric data (raw)
├── filtered_data/                         # Consolidated datasets
│   ├── consolidated_enrolment.csv
│   ├── consolidated_demographic.csv
│   └── consolidated_biometric.csv
└── outputs/                               # Generated outputs
    ├── digital_infrastructure_indices.csv
    └── digital_infrastructure_typology.csv
```

---

## 👥 Team

### Team Bharat Bytes

| Member | Role | GitHub |
|--------|------|--------|
| **Vedang Mendhurwar** | Team Leader | [@Vedang-M](https://github.com/Vedang-M) |
| **Ruturaj Rajwade** | Developer | [@RAR2025](https://github.com/RAR2025) |
| **Shreya Dandekar** | Developer | [@shreyadandekar](https://github.com/shreyadandekar) |
| **Harshal Pednekar** | Developer | [@harshalnnpednekar](https://github.com/harshalnnpednekar) |

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**🏆 UIDAI Data Hackathon 2026** | **Team Bharat Bytes**

*Turning Aadhaar Data Into Actionable Intelligence for India* 🇮🇳

**[🚀 Try the Live Demo](https://bharatbytes-uidai-ylygudcjhgpkrhixwpld8s.streamlit.app/)**

</div>
