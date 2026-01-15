# BharatBytes-UIDAI

Minimal setup to run the analysis script and the Streamlit dashboard.

## Prerequisites
- Python 3.10+ available as `python` or `py`
- pip

## Setup
1) Clone or download this repository.
2) Install dependencies:
```
pip install -r requirements.txt
```

## Run the analysis script (optional)
```
python aadhaar_enrolment_analysis.py
```
```
python aadhaar_demographic_analysis.py
```
```
python aadhaar_demographic_analysis.py
```

## Launch the Streamlit dashboard
```
streamlit run streamlit_app.py
```

If `streamlit` is not on PATH, try:
```
python -m streamlit run streamlit_app.py
```

## Common notes
- The dashboard will print a local URL (default http://localhost:8501).
- Stop the app with Ctrl+C in the terminal.
