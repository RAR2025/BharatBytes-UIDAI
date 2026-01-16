"""
================================================================================
UIDAI AADHAAR ANALYTICS PLATFORM
Professional Dashboard for the UIDAI Data Hackathon 2026
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ================================================================================
# PAGE CONFIGURATION
# ================================================================================
st.set_page_config(
    page_title="UIDAI Aadhaar Analytics Platform",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================================
# LIGHT THEME CSS (Same structure as before, just light colors)
# ================================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 50%, #f1f3f5 100%);
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        border-right: 1px solid #dee2e6;
    }
    
    /* Main Title */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .sub-title {
        font-size: 1rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* Glass Card Effect - Light */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(37, 99, 235, 0.3);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.1);
    }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.08) 0%, rgba(124, 58, 237, 0.08) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(37, 99, 235, 0.2);
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.15);
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        font-size: 0.8rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-delta {
        font-size: 0.85rem;
        color: #10b981;
        font-weight: 500;
    }
    
    /* Insight Cards */
    .insight-card {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%);
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.5rem 0;
    }
    
    .insight-card-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(234, 88, 12, 0.08) 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .insight-card-success {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, rgba(16, 185, 129, 0.08) 100%);
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .insight-card-danger {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(220, 38, 38, 0.08) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .insight-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    
    .insight-text {
        font-size: 0.9rem;
        color: #495057;
        line-height: 1.5;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-header::after {
        content: '';
        flex-grow: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(37, 99, 235, 0.3), transparent);
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        color: #1a1a2e !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #6c757d !important;
    }
    
    /* Filter Card */
    .filter-card {
        background: rgba(37, 99, 235, 0.05);
        border: 1px solid rgba(37, 99, 235, 0.15);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Divider */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(37, 99, 235, 0.3), transparent);
        margin: 1.5rem 0;
    }
    
    /* Badge */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-primary {
        background: rgba(37, 99, 235, 0.15);
        color: #2563eb;
        border: 1px solid rgba(37, 99, 235, 0.3);
    }
    
    .badge-success {
        background: rgba(34, 197, 94, 0.15);
        color: #16a34a;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: #d97706;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .badge-danger {
        background: rgba(239, 68, 68, 0.15);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Stat Box */
    .stat-box {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2563eb;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #6c757d;
        margin-top: 0.25rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.9);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #6c757d;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
    }
    
    /* Spec Table */
    .spec-table {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }
    
    .spec-row {
        display: flex;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .spec-row:last-child {
        border-bottom: none;
    }
    
    .spec-label {
        flex: 1;
        padding: 0.75rem 1rem;
        background: #f8f9fa;
        font-weight: 500;
        color: #6c757d;
        font-size: 0.85rem;
    }
    
    .spec-value {
        flex: 1;
        padding: 0.75rem 1rem;
        color: #1a1a2e;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ================================================================================
# DATA LOADING
# ================================================================================

@st.cache_data(ttl=3600)
def load_all_data():
    """Load all three datasets"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    datasets = {}
    
    filtered_dir = os.path.join(base_dir, "filtered_data")
    
    if os.path.exists(filtered_dir):
        enrol_file = os.path.join(filtered_dir, "consolidated_enrolment.csv")
        demo_file = os.path.join(filtered_dir, "consolidated_demographic.csv")
        bio_file = os.path.join(filtered_dir, "consolidated_biometric.csv")
        
        if os.path.exists(enrol_file):
            df = pd.read_csv(enrol_file)
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
            df['total_enrolment'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
            datasets['enrolment'] = df
        
        if os.path.exists(demo_file):
            df = pd.read_csv(demo_file)
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
            df['total_demo'] = df['demo_age_5_17'] + df['demo_age_17_']
            datasets['demographic'] = df
        
        if os.path.exists(bio_file):
            df = pd.read_csv(bio_file)
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
            df['total_bio'] = df['bio_age_5_17'] + df['bio_age_17_']
            datasets['biometric'] = df
    else:
        for folder, name, cols in [
            ("api_data_aadhar_enrolment", "enrolment", ['age_0_5', 'age_5_17', 'age_18_greater']),
            ("api_data_aadhar_demographic", "demographic", ['demo_age_5_17', 'demo_age_17_']),
            ("api_data_aadhar_biometric", "biometric", ['bio_age_5_17', 'bio_age_17_'])
        ]:
            data_dir = os.path.join(base_dir, folder)
            if os.path.exists(data_dir):
                dfs = []
                for f in sorted(os.listdir(data_dir)):
                    if f.endswith('.csv'):
                        dfs.append(pd.read_csv(os.path.join(data_dir, f)))
                if dfs:
                    df = pd.concat(dfs, ignore_index=True)
                    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
                    if name == 'enrolment':
                        df['total_enrolment'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
                    elif name == 'demographic':
                        df['total_demo'] = df['demo_age_5_17'] + df['demo_age_17_']
                    else:
                        df['total_bio'] = df['bio_age_5_17'] + df['bio_age_17_']
                    datasets[name] = df
    
    return datasets

with st.spinner('Loading datasets...'):
    data = load_all_data()
    df_enrol = data.get('enrolment', pd.DataFrame())
    df_demo = data.get('demographic', pd.DataFrame())
    df_bio = data.get('biometric', pd.DataFrame())

all_states = sorted(df_enrol['state'].unique().tolist()) if not df_enrol.empty else []

# ================================================================================
# SIDEBAR
# ================================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <span style="font-size: 3rem;">🇮🇳</span>
        <h2 style="color: #1a1a2e; margin: 0.5rem 0 0.25rem 0; font-weight: 700; font-size: 1.3rem;">UIDAI Analytics</h2>
        <p style="color: #2563eb; font-size: 0.8rem; margin: 0;">Data Hackathon 2026</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Navigation with styled buttons
    st.markdown('<p style="color: #6c757d; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.75rem;">📊 NAVIGATION</p>', unsafe_allow_html=True)
    
    # Initialize session state for page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Executive Summary"
    
    nav_items = [
        ("🏠", "Executive Summary"),
        ("📋", "Detailed Analysis"),
        ("🔮", "Predictive"),
        ("🔍", "Data Explorer"),
        ("⚖️", "EUMI Analysis")
    ]
    
    for icon, name in nav_items:
        is_active = st.session_state.current_page == name
        if is_active:
            # Show styled active indicator (non-clickable)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2563eb, #7c3aed); color: white; padding: 0.75rem 1rem; 
                        border-radius: 8px; margin-bottom: 0.5rem; font-weight: 500; font-size: 0.9rem; cursor: default;">
                {icon} {name}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show clickable button for inactive items
            if st.button(f"{icon} {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state.current_page = name
                st.rerun()
    
    page = st.session_state.current_page
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<p style="color: #6c757d; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">🎯 FILTERS</p>', unsafe_allow_html=True)
    
    selected_states = st.multiselect(
        "Filter by State(s)",
        options=all_states,
        default=[],
        placeholder="All States"
    )
    
    if selected_states:
        if not df_enrol.empty:
            df_enrol = df_enrol[df_enrol['state'].isin(selected_states)]
        if not df_demo.empty:
            df_demo = df_demo[df_demo['state'].isin(selected_states)]
        if not df_bio.empty:
            df_bio = df_bio[df_bio['state'].isin(selected_states)]
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<p style="color: #6c757d; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">📋 QUICK STATS</p>', unsafe_allow_html=True)
    
    if not df_enrol.empty:
        st.markdown(f"""
        <div class="glass-card" style="padding: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                <span style="color: #6c757d; font-size: 0.75rem;">Records</span>
                <span style="color: #1a1a2e; font-weight: 600;">{len(df_enrol):,}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                <span style="color: #6c757d; font-size: 0.75rem;">States</span>
                <span style="color: #1a1a2e; font-weight: 600;">{df_enrol['state'].nunique()}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #6c757d; font-size: 0.75rem;">Districts</span>
                <span style="color: #1a1a2e; font-weight: 600;">{df_enrol['district'].nunique()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================
# HELPER FUNCTION
# ================================================================================
def show_filter_indicator():
    if selected_states:
        states_text = ", ".join(selected_states[:3])
        if len(selected_states) > 3:
            states_text += f" +{len(selected_states)-3} more"
        st.markdown(f"""
        <div class="filter-card">
            <span style="color: #2563eb; font-size: 0.85rem;">🎯 Filtered: </span>
            <span style="color: #1a1a2e; font-size: 0.85rem;">{states_text}</span>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================
# PAGE: EXECUTIVE SUMMARY
# ================================================================================

if page == "Executive Summary":
    st.markdown("""
    <h1 class="main-title">UIDAI Aadhaar Analytics Platform</h1>
    <p class="sub-title">Comprehensive Intelligence Dashboard for India's Digital Identity Infrastructure</p>
    """, unsafe_allow_html=True)
    
    show_filter_indicator()
    
    if not df_enrol.empty:
        total_enrol = df_enrol['total_enrolment'].sum()
        total_states = df_enrol['state'].nunique()
        total_districts = df_enrol['district'].nunique()
        avg_daily = df_enrol.groupby('date')['total_enrolment'].sum().mean()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">Total Enrolments</p>
                <p class="kpi-value">{total_enrol/1e6:.2f}M</p>
                <p class="kpi-delta">↗ Active</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">States Covered</p>
                <p class="kpi-value">{total_states}</p>
                <p class="kpi-delta">↗ Coverage</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">Districts Active</p>
                <p class="kpi-value">{total_districts}</p>
                <p class="kpi-delta">↗ Nationwide</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">Daily Average</p>
                <p class="kpi-value">{avg_daily/1e3:.1f}K</p>
                <p class="kpi-delta">↗ Per Day</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">🎯 Key Strategic Insights</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not df_enrol.empty:
            age_0_5 = df_enrol['age_0_5'].sum()
            total = df_enrol['total_enrolment'].sum()
            pct = age_0_5 / total * 100 if total > 0 else 0
            
            st.markdown(f"""
            <div class="insight-card insight-card-warning">
                <p class="insight-title">⚠️ Age Cohort Misallocation</p>
                <p class="insight-text">
                    <strong>{pct:.1f}%</strong> of enrolments in 0-5 age group, 
                    consuming <strong>~84%</strong> of effort (4x weight factor).
                </p>
                <span class="badge badge-warning">HIGH PRIORITY</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="insight-card insight-card-success">
            <p class="insight-title">🏙️ Geographic Efficiency</p>
            <p class="insight-text">
                Tier-2 cities show higher processing efficiency than metros with better utilization.
            </p>
            <span class="badge badge-success">OPPORTUNITY</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-card insight-card-danger">
            <p class="insight-title">🔴 Biometric Backlog</p>
            <p class="insight-text">
                Biometric verification exceeds demographics, indicating batch processing or re-verification.
            </p>
            <span class="badge badge-danger">MONITOR</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="insight-card">
            <p class="insight-title">🔮 Predictive Model</p>
            <p class="insight-text">
                ML model achieves <strong>80.6%</strong> accuracy predicting high-backlog states.
            </p>
            <span class="badge badge-primary">ML POWERED</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">📈 Enrolment Trends</p>', unsafe_allow_html=True)
    
    if not df_enrol.empty:
        daily = df_enrol.groupby('date')['total_enrolment'].sum().reset_index()
        daily['rolling_7d'] = daily['total_enrolment'].rolling(7, min_periods=1).mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily['date'], y=daily['total_enrolment'],
            mode='lines', name='Daily Volume',
            line=dict(color='rgba(37, 99, 235, 0.3)', width=1),
            fill='tozeroy', fillcolor='rgba(37, 99, 235, 0.05)'
        ))
        
        fig.add_trace(go.Scatter(
            x=daily['date'], y=daily['rolling_7d'],
            mode='lines', name='7-Day Average',
            line=dict(color='#2563eb', width=3)
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=350, margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', title='Enrolments'),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ================================================================================
# PAGE: DETAILED ANALYSIS (Combined: Biometric, Demographics, Enrolment)
# ================================================================================

elif page == "Detailed Analysis":
    st.markdown("""
    <h1 class="main-title">Detailed Analysis</h1>
    <p class="sub-title">Comprehensive analysis of Biometric, Demographics, and Enrolment data</p>
    """, unsafe_allow_html=True)
    
    show_filter_indicator()
    
    # Three tabs for different analysis types
    tab1, tab2, tab3 = st.tabs(["Biometric vs Demographic", "Geographic Analysis", "Age Cohort"])
    
    # ==================== TAB 1: BIOMETRIC ANALYSIS ====================
    with tab1:
        # Help tooltip
        with st.expander("What is this chart about?", expanded=False):
            st.markdown("""
            This section compares **Demographic registrations** (initial identity data collection) with **Biometric verifications** 
            (fingerprint/iris scans). The gap between them indicates the backlog of pending biometric verifications.
            """)
        
        if not df_demo.empty and not df_bio.empty:
            demo_daily = df_demo.groupby('date')['total_demo'].sum().reset_index().sort_values('date')
            bio_daily = df_bio.groupby('date')['total_bio'].sum().reset_index().sort_values('date')
            
            demo_daily['cum'] = demo_daily['total_demo'].cumsum()
            bio_daily['cum'] = bio_daily['total_bio'].cumsum()
            
            total_demo = demo_daily['cum'].iloc[-1]
            total_bio = bio_daily['cum'].iloc[-1]
            ratio = total_bio / total_demo if total_demo > 0 else 0
            gap = total_bio - total_demo
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="kpi-card">
                    <p class="kpi-label">Total Demographic</p>
                    <p class="kpi-value">{total_demo/1e6:.1f}M</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="kpi-card">
                    <p class="kpi-label">Total Biometric</p>
                    <p class="kpi-value">{total_bio/1e6:.1f}M</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="kpi-card">
                    <p class="kpi-label">Bio/Demo Ratio</p>
                    <p class="kpi-value">{ratio:.2f}x</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Dynamic Insight Box
            if ratio > 1:
                insight_class = "insight-card-warning"
                insight_title = "Biometric Exceeds Demographic"
                insight_text = f"Biometric records ({total_bio/1e6:.1f}M) exceed demographic ({total_demo/1e6:.1f}M) by {abs(gap)/1e6:.2f}M. This suggests re-verification activity or batch processing of existing records."
                badge = "MONITOR"
                badge_class = "badge-warning"
            elif ratio < 0.9:
                insight_class = "insight-card-danger"
                insight_title = "Significant Biometric Backlog"
                insight_text = f"Only {ratio*100:.1f}% of demographic records have biometric verification. Backlog of approximately {abs(gap)/1e6:.2f}M pending verifications."
                badge = "HIGH PRIORITY"
                badge_class = "badge-danger"
            else:
                insight_class = "insight-card-success"
                insight_title = "Healthy Processing Rate"
                insight_text = f"Biometric verification is keeping pace with demographic registration at {ratio*100:.1f}% completion rate."
                badge = "ON TRACK"
                badge_class = "badge-success"
            
            st.markdown(f"""
            <div class="insight-card {insight_class}">
                <p class="insight-title">{insight_title}</p>
                <p class="insight-text">{insight_text}</p>
                <span class="badge {badge_class}">{badge}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
            
            st.markdown('<p class="section-header">Cumulative Comparison Over Time</p>', unsafe_allow_html=True)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=demo_daily['date'], y=demo_daily['cum'], mode='lines',
                                      name='Demographic', line=dict(color='#3b82f6', width=3),
                                      fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)'))
            fig.add_trace(go.Scatter(x=bio_daily['date'], y=bio_daily['cum'], mode='lines',
                                      name='Biometric', line=dict(color='#10b981', width=3),
                                      fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.1)'))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=350, margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                yaxis=dict(title='Cumulative Count', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<p class="section-header">State-wise Comparison</p>', unsafe_allow_html=True)
            
            state_demo = df_demo.groupby('state')['total_demo'].sum()
            state_bio = df_bio.groupby('state')['total_bio'].sum()
            comparison = pd.DataFrame({'Demographic': state_demo, 'Biometric': state_bio}).fillna(0)
            comparison['Ratio'] = comparison['Biometric'] / comparison['Demographic'].replace(0, 1)
            comparison = comparison.sort_values('Demographic', ascending=False)
            top_state = comparison.index[0]
            top_ratio = comparison.loc[top_state, 'Ratio']
            
            # Dynamic insight for state comparison
            states_with_backlog = len(comparison[comparison['Ratio'] < 0.9])
            st.markdown(f"""
            <div class="insight-card">
                <p class="insight-title">State Distribution</p>
                <p class="insight-text">
                    <strong>{top_state}</strong> leads with {comparison.loc[top_state, 'Demographic']/1e6:.2f}M demographic records.
                    {states_with_backlog} states have biometric backlog (less than 90% verification rate).
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            comparison_top = comparison.head(12)
            fig_state = px.bar(comparison_top.reset_index(), x='state', y=['Demographic', 'Biometric'],
                               barmode='group', color_discrete_sequence=['#3b82f6', '#10b981'])
            fig_state.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                    height=350, xaxis_tickangle=-45,
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(fig_state, use_container_width=True)
        else:
            st.info("Biometric or Demographic data not available")
    
    # ==================== TAB 2: GEOGRAPHIC ANALYSIS ====================
    with tab2:
        # Help tooltip
        with st.expander("What is this chart about?", expanded=False):
            st.markdown("""
            This section shows **geographic distribution** of Aadhaar enrolments across Indian states.
            The Pareto (80/20) analysis reveals how concentrated enrolments are among top states.
            """)
        
        if not df_enrol.empty:
            state_totals = df_enrol.groupby('state').agg({
                'total_enrolment': 'sum', 'district': 'nunique', 'pincode': 'nunique'
            }).reset_index()
            state_totals.columns = ['State', 'Enrolments', 'Districts', 'Pincodes']
            state_totals = state_totals.sort_values('Enrolments', ascending=False)
            
            # Calculate dynamic statistics
            total_states = len(state_totals)
            total_enrolments = state_totals['Enrolments'].sum()
            top_state = state_totals.iloc[0]['State']
            top_state_enrol = state_totals.iloc[0]['Enrolments']
            top_state_pct = top_state_enrol / total_enrolments * 100
            
            # Dynamic insight about geographic concentration
            top_3_pct = state_totals.head(3)['Enrolments'].sum() / total_enrolments * 100
            
            if top_3_pct > 50:
                insight_class = "insight-card-warning"
                insight_title = "High Geographic Concentration"
                insight_text = f"Top 3 states ({', '.join(state_totals.head(3)['State'].tolist())}) account for {top_3_pct:.1f}% of all enrolments. Consider expanding infrastructure in underserved regions."
                badge = "ACTION NEEDED"
                badge_class = "badge-warning"
            else:
                insight_class = "insight-card-success"
                insight_title = "Balanced Distribution"
                insight_text = f"Enrolments are relatively well-distributed. Top 3 states account for {top_3_pct:.1f}% of total volume."
                badge = "HEALTHY"
                badge_class = "badge-success"
            
            st.markdown(f"""
            <div class="insight-card {insight_class}">
                <p class="insight-title">{insight_title}</p>
                <p class="insight-text">{insight_text}</p>
                <span class="badge {badge_class}">{badge}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<p class="section-header">Top States by Enrolment</p>', unsafe_allow_html=True)
            
            top_15 = state_totals.head(15)
            fig = px.bar(top_15, x='State', y='Enrolments',
                         color='Enrolments', color_continuous_scale='Blues')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              height=350, xaxis_tickangle=-45, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
            
            # Help for Pareto
            with st.expander("What is Pareto Analysis?", expanded=False):
                st.markdown("""
                The **Pareto Principle (80/20 rule)** states that roughly 80% of effects come from 20% of causes.
                Here we analyze how many states contribute to 80% of total enrolments.
                """)
            
            st.markdown('<p class="section-header">Pareto Analysis (80/20)</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                sorted_df = state_totals.copy()
                sorted_df['CumPct'] = sorted_df['Enrolments'].cumsum() / sorted_df['Enrolments'].sum() * 100
                
                fig_p = make_subplots(specs=[[{"secondary_y": True}]])
                fig_p.add_trace(go.Bar(x=sorted_df['State'].head(15), y=sorted_df['Enrolments'].head(15),
                                       name='Enrolments', marker_color='#2563eb'), secondary_y=False)
                fig_p.add_trace(go.Scatter(x=sorted_df['State'].head(15), y=sorted_df['CumPct'].head(15),
                                           name='Cumulative %', line=dict(color='#f59e0b', width=3)), secondary_y=True)
                fig_p.add_hline(y=80, line_dash="dash", line_color="rgba(239, 68, 68, 0.5)",
                               annotation_text="80%", secondary_y=True)
                fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, xaxis_tickangle=-45)
                st.plotly_chart(fig_p, use_container_width=True)
            
            with col2:
                states_80 = len(sorted_df[sorted_df['CumPct'] <= 80])
                states_80_pct = states_80 / total_states * 100
                st.markdown(f"""
                <div class="glass-card" style="text-align: center; padding: 1.5rem;">
                    <p style="color: #6c757d; font-size: 0.8rem; margin-bottom: 0.5rem;">CONCENTRATION</p>
                    <p style="font-size: 2.5rem; font-weight: 800; color: #2563eb; margin: 0;">{states_80}</p>
                    <p style="color: #495057; margin-top: 0.5rem; font-size: 0.9rem;">states generate 80%</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Additional dynamic insight
                st.markdown(f"""
                <div class="insight-card" style="margin-top: 1rem;">
                    <p class="insight-text" style="font-size: 0.85rem;">
                        Only <strong>{states_80_pct:.0f}%</strong> of states ({states_80} of {total_states}) 
                        generate <strong>80%</strong> of enrolments.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Enrolment data not available")
    
    # ==================== TAB 3: ENROLMENT (Age Cohort) ====================
    with tab3:
        # Help tooltip
        with st.expander("What is this chart about?", expanded=False):
            st.markdown("""
            This section analyzes **age distribution** of Aadhaar enrolments. Different age groups require 
            different effort levels for biometric capture:
            - **0-5 years**: 4x effort (difficult biometrics, frequent updates needed)
            - **5-17 years**: 1.5x effort (growing individuals)
            - **18+ years**: 1x effort (stable biometrics)
            """)
        
        if not df_enrol.empty:
            age_0_5 = df_enrol['age_0_5'].sum()
            age_5_17 = df_enrol['age_5_17'].sum()
            age_18 = df_enrol['age_18_greater'].sum()
            total = age_0_5 + age_5_17 + age_18
            
            effort_0_5 = age_0_5 * 4.0
            effort_5_17 = age_5_17 * 1.5
            effort_18 = age_18 * 1.0
            total_effort = effort_0_5 + effort_5_17 + effort_18
            
            # Calculate percentages for dynamic insights
            pct_0_5 = age_0_5 / total * 100 if total > 0 else 0
            effort_pct_0_5 = effort_0_5 / total_effort * 100 if total_effort > 0 else 0
            
            # Dynamic insight based on calculated data
            if pct_0_5 > 50:
                insight_class = "insight-card-warning"
                insight_title = "Age Cohort Misallocation"
                insight_text = f"{pct_0_5:.1f}% of enrolments are in the 0-5 age group, consuming ~{effort_pct_0_5:.0f}% of effort (4x weight factor). This indicates resource-intensive processing for young children."
                badge = "HIGH PRIORITY"
                badge_class = "badge-warning"
            elif pct_0_5 > 30:
                insight_class = "insight-card"
                insight_title = "Moderate Child Enrolment"
                insight_text = f"{pct_0_5:.1f}% of enrolments are children (0-5), consuming {effort_pct_0_5:.0f}% of processing effort."
                badge = "MONITOR"
                badge_class = "badge-primary"
            else:
                insight_class = "insight-card-success"
                insight_title = "Balanced Age Distribution"
                insight_text = f"Age distribution is balanced with {pct_0_5:.1f}% in 0-5 age group, resulting in efficient resource utilization."
                badge = "OPTIMAL"
                badge_class = "badge-success"
            
            st.markdown(f"""
            <div class="insight-card {insight_class}">
                <p class="insight-title">{insight_title}</p>
                <p class="insight-text">{insight_text}</p>
                <span class="badge {badge_class}">{badge}</span>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="kpi-card" style="border-color: rgba(239, 68, 68, 0.3);">
                    <p class="kpi-label">Age 0-5 Years</p>
                    <p class="kpi-value" style="color: #dc2626;">{age_0_5/1e6:.2f}M</p>
                    <p class="kpi-delta" style="color: #dc2626;">{pct_0_5:.1f}% volume</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="kpi-card" style="border-color: rgba(245, 158, 11, 0.3);">
                    <p class="kpi-label">Age 5-17 Years</p>
                    <p class="kpi-value" style="color: #d97706;">{age_5_17/1e6:.2f}M</p>
                    <p class="kpi-delta" style="color: #d97706;">{age_5_17/total*100:.1f}% volume</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="kpi-card" style="border-color: rgba(34, 197, 94, 0.3);">
                    <p class="kpi-label">Age 18+ Years</p>
                    <p class="kpi-value" style="color: #16a34a;">{age_18/1e3:.0f}K</p>
                    <p class="kpi-delta">{age_18/total*100:.1f}% volume</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<p class="section-header">Volume Distribution</p>', unsafe_allow_html=True)
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['0-5 Years', '5-17 Years', '18+ Years'],
                    values=[age_0_5, age_5_17, age_18], hole=0.6,
                    marker=dict(colors=['#ef4444', '#f59e0b', '#22c55e']),
                    textinfo='percent', textfont=dict(size=14, color='#1a1a2e')
                )])
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', height=320,
                    showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
                    annotations=[dict(text=f'{total/1e6:.1f}M', x=0.5, y=0.5, font_size=22, font_color='#1a1a2e', showarrow=False)]
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown('<p class="section-header">Effort Distribution</p>', unsafe_allow_html=True)
                
                # Help for effort calculation
                with st.expander("How is effort calculated?", expanded=False):
                    st.markdown(f"""
                    - **0-5 Years**: {age_0_5/1e6:.2f}M × 4.0 = {effort_0_5/1e6:.2f}M effort
                    - **5-17 Years**: {age_5_17/1e6:.2f}M × 1.5 = {effort_5_17/1e6:.2f}M effort
                    - **18+ Years**: {age_18/1e3:.0f}K × 1.0 = {effort_18/1e3:.0f}K effort
                    """)
                
                fig_effort = go.Figure(data=[go.Bar(
                    x=['0-5 Years', '5-17 Years', '18+ Years'],
                    y=[effort_pct_0_5, effort_5_17/total_effort*100, effort_18/total_effort*100],
                    marker=dict(color=['#ef4444', '#f59e0b', '#22c55e']),
                    text=[f'{effort_pct_0_5:.1f}%', f'{effort_5_17/total_effort*100:.1f}%', f'{effort_18/total_effort*100:.1f}%'],
                    textposition='outside'
                )])
                fig_effort.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=320,
                    yaxis=dict(title='Effort Share (%)', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                    bargap=0.4
                )
                st.plotly_chart(fig_effort, use_container_width=True)
        else:
            st.info("Enrolment data not available")

# ================================================================================
# PAGE: PREDICTIVE ANALYTICS
# ================================================================================

elif page == "Predictive":
    st.markdown("""
    <h1 class="main-title">Predictive Analytics</h1>
    <p class="sub-title">ML-powered insights for proactive decision making</p>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">🔧 Model Specifications</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="spec-table">
            <div class="spec-row">
                <div class="spec-label">Algorithm</div>
                <div class="spec-value">Random Forest Classifier</div>
            </div>
            <div class="spec-row">
                <div class="spec-label">Number of Trees (n_estimators)</div>
                <div class="spec-value">100</div>
            </div>
            <div class="spec-row">
                <div class="spec-label">Maximum Depth (max_depth)</div>
                <div class="spec-value">10</div>
            </div>
            <div class="spec-row">
                <div class="spec-label">Splitting Criterion</div>
                <div class="spec-value">Gini Impurity</div>
            </div>
            <div class="spec-row">
                <div class="spec-label">Min Samples Split</div>
                <div class="spec-value">2 (default)</div>
            </div>
            <div class="spec-row">
                <div class="spec-label">Min Samples Leaf</div>
                <div class="spec-value">1 (default)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="spec-table">
            <div class="spec-row">
                <div class="spec-label">Target Variable</div>
                <div class="spec-value">High Backlog (Binary: 0/1)</div>
            </div>
            <div class="spec-row">
                <div class="spec-label">Backlog Threshold</div>
                <div class="spec-value">75th Percentile</div>
            </div>
            <div class="spec-row">
                <div class="spec-label">Feature Count</div>
                <div class="spec-value">9</div>
            </div>
            <div class="spec-row">
                <div class="spec-label">Train/Test Split</div>
                <div class="spec-value">80% / 20%</div>
            </div>
            <div class="spec-row">
                <div class="spec-label">Random State</div>
                <div class="spec-value">42</div>
            </div>
            <div class="spec-row">
                <div class="spec-label">Library</div>
                <div class="spec-value">scikit-learn</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">📊 Performance Metrics</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Accuracy", "80.63%")
    col2.metric("ROC-AUC", "0.7863")
    col3.metric("Gini Coefficient", "0.5726")
    col4.metric("Features Used", "9")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">📈 Feature Importance</p>', unsafe_allow_html=True)
    
    importance = pd.DataFrame({
        'Feature': ['backlog_lag_1', 'bio_lag_1', 'demo_lag_1', 'demo_lag_2', 
                   'bio_lag_2', 'pct_5_17', 'pct_0_5', 'pct_18_plus', 'tier'],
        'Importance': [0.2959, 0.1253, 0.1202, 0.1035, 0.0902, 0.0886, 0.0843, 0.0737, 0.0183],
        'Description': [
            'Previous week backlog', 'Previous week biometric volume', 'Previous week demographic volume',
            '2 weeks ago demographic', '2 weeks ago biometric', 'Percentage age 5-17',
            'Percentage age 0-5', 'Percentage age 18+', 'Geographic tier (1/2/3)'
        ]
    })
    
    fig = px.bar(importance, x='Importance', y='Feature', orientation='h',
                 color='Importance', color_continuous_scale='Blues')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                      height=350, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<p class="section-header">📋 Feature Descriptions</p>', unsafe_allow_html=True)
    st.dataframe(importance, hide_index=True, use_container_width=True)

# ================================================================================
# PAGE: DATA EXPLORER
# ================================================================================

elif page == "Data Explorer":
    st.markdown("""
    <h1 class="main-title">Data Explorer</h1>
    <p class="sub-title">Deep-dive analysis with anomaly detection and statistical insights</p>
    """, unsafe_allow_html=True)
    
    show_filter_indicator()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Statistical Summary", "🔴 Anomaly Detection", "📈 District Analysis", "📋 Raw Data"])
    
    with tab1:
        st.markdown('<p class="section-header">📊 Statistical Overview</p>', unsafe_allow_html=True)
        
        if not df_enrol.empty:
            daily_totals = df_enrol.groupby('date')['total_enrolment'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Daily Mean", f"{daily_totals.mean()/1e3:.1f}K")
            col2.metric("Daily Median", f"{daily_totals.median()/1e3:.1f}K")
            col3.metric("Std Deviation", f"{daily_totals.std()/1e3:.1f}K")
            cv = daily_totals.std() / daily_totals.mean() * 100
            col4.metric("CV (Volatility)", f"{cv:.1f}%")
            
            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
            
            st.markdown('<p class="section-header">📈 Daily Distribution</p>', unsafe_allow_html=True)
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=daily_totals, nbinsx=30, marker_color='#2563eb', opacity=0.7))
            fig.add_vline(x=daily_totals.mean(), line_dash="dash", line_color="#f59e0b", annotation_text="Mean")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300,
                              xaxis_title='Daily Enrolments', yaxis_title='Frequency')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown('<p class="section-header">🔴 Anomaly Detection</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="insight-card" style="margin-bottom: 1.5rem;">
            <p class="insight-title">📌 What is Anomaly Detection?</p>
            <p class="insight-text">
                This analysis identifies <strong>unusual spikes or drops</strong> in daily enrolment volumes using IQR method.
                Anomalies may indicate special campaigns, system issues, or seasonal patterns.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if not df_enrol.empty:
            daily = df_enrol.groupby('date')['total_enrolment'].sum().reset_index()
            q1, q3 = daily['total_enrolment'].quantile([0.25, 0.75])
            iqr = q3 - q1
            upper, lower = q3 + 1.5 * iqr, max(0, q1 - 1.5 * iqr)
            
            daily['anomaly'] = (daily['total_enrolment'] > upper) | (daily['total_enrolment'] < lower)
            anomalies = daily[daily['anomaly']]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=daily['date'], y=daily['total_enrolment'], mode='lines',
                                         name='Daily Volume', line=dict(color='#2563eb')))
                fig.add_trace(go.Scatter(x=anomalies['date'], y=anomalies['total_enrolment'], mode='markers',
                                         name='Anomalies', marker=dict(color='#ef4444', size=10, symbol='x')))
                fig.add_hline(y=upper, line_dash="dash", line_color="rgba(239, 68, 68, 0.5)", annotation_text="Upper")
                if lower > 0:
                    fig.add_hline(y=lower, line_dash="dash", line_color="rgba(34, 197, 94, 0.5)", annotation_text="Lower")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Anomalies Found", f"{len(anomalies)} of {len(daily)} days")
                st.metric("Upper Threshold", f"{upper/1e3:.1f}K")
                st.metric("Lower Threshold", f"{lower/1e3:.1f}K")
    
    with tab3:
        st.markdown('<p class="section-header">📈 District Performance</p>', unsafe_allow_html=True)
        
        if not df_enrol.empty:
            district_stats = df_enrol.groupby(['state', 'district']).agg({
                'total_enrolment': ['sum', 'mean', 'std', 'count'],
                'pincode': 'nunique'
            }).reset_index()
            district_stats.columns = ['State', 'District', 'Total', 'Daily Avg', 'Std Dev', 'Records', 'Pincodes']
            district_stats['Efficiency'] = district_stats['Total'] / district_stats['Pincodes']
            district_stats = district_stats.sort_values('Total', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top 10 by Volume**")
                top_10 = district_stats.head(10)[['State', 'District', 'Total', 'Efficiency']].copy()
                top_10['Total'] = top_10['Total'].apply(lambda x: f"{x/1e3:.1f}K")
                top_10['Efficiency'] = top_10['Efficiency'].apply(lambda x: f"{x:.0f}")
                st.dataframe(top_10, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("**Top 10 by Efficiency (per Pincode)**")
                efficient = district_stats.nlargest(10, 'Efficiency')[['State', 'District', 'Total', 'Efficiency']].copy()
                efficient['Total'] = efficient['Total'].apply(lambda x: f"{x/1e3:.1f}K")
                efficient['Efficiency'] = efficient['Efficiency'].apply(lambda x: f"{x:.0f}")
                st.dataframe(efficient, use_container_width=True, hide_index=True)
    
    with tab4:
        st.markdown('<p class="section-header">📋 Raw Data Sample</p>', unsafe_allow_html=True)
        
        dataset = st.selectbox("Select Dataset", ["Enrolment", "Demographic", "Biometric"])
        
        if dataset == "Enrolment" and not df_enrol.empty:
            st.dataframe(df_enrol.head(200), use_container_width=True)
        elif dataset == "Demographic" and not df_demo.empty:
            st.dataframe(df_demo.head(200), use_container_width=True)
        elif dataset == "Biometric" and not df_bio.empty:
            st.dataframe(df_bio.head(200), use_container_width=True)

# ================================================================================
# PAGE: EUMI ANALYSIS
# ================================================================================

elif page == "EUMI Analysis":
    # Modern EUMI Dashboard Header
    st.markdown("""
    <div style="margin-bottom: 2.5rem;">
        <h1 style="font-size: 2.5rem; font-weight: 700; color: #1a1a2e; margin: 0 0 0.5rem 0; letter-spacing: -0.5px;">
            Enrollment–Usage Mismatch Index
        </h1>
        <p style="font-size: 1rem; color: #6c757d; margin: 0; font-weight: 400;">
            Analyze district-level enrollment and biometric usage patterns
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    show_filter_indicator()
    
    # Load and compute EUMI data
    @st.cache_data(ttl=3600)
    def compute_eumi_data():
        """Compute EUMI from enrollment and biometric datasets"""
        try:
            # Aggregate enrollment at district level
            df_enrol_agg = df_enrol.groupby('district').agg({
                'total_enrolment': 'sum',
                'state': 'first'
            }).reset_index()
            
            # Aggregate biometric at district level
            df_bio_agg = df_bio.groupby('district').agg({
                'total_bio': 'sum',
                'state': 'first'
            }).reset_index() if not df_bio.empty else pd.DataFrame()
            
            if df_bio_agg.empty:
                st.warning("⚠️ Biometric data not available. Cannot compute EUMI.")
                return None
            
            # Merge datasets on district
            merged_df = pd.merge(df_enrol_agg, df_bio_agg[['district', 'total_bio']], on='district', how='outer')
            merged_df['total_enrolment'] = merged_df['total_enrolment'].fillna(0)
            merged_df['total_bio'] = merged_df['total_bio'].fillna(0)
            
            # Compute shares
            total_enrol = merged_df['total_enrolment'].sum()
            total_bio = merged_df['total_bio'].sum()
            
            merged_df['enroll_share'] = merged_df['total_enrolment'] / total_enrol if total_enrol > 0 else 0
            merged_df['usage_share'] = merged_df['total_bio'] / total_bio if total_bio > 0 else 0
            
            # Compute EUMI with safeguard against division by zero
            merged_df['EUMI'] = np.where(
                merged_df['enroll_share'] > 0, 
                merged_df['usage_share'] / merged_df['enroll_share'],
                np.nan
            )
            
            # Categorize districts based on EUMI
            conditions = [
                (merged_df['EUMI'] < 0.8),
                (merged_df['EUMI'] >= 0.8) & (merged_df['EUMI'] <= 1.2),
                (merged_df['EUMI'] > 1.2)
            ]
            choices = ["Over-enrolled, under-used", "Balanced", "Under-enrolled, high-usage"]
            merged_df['category'] = np.select(conditions, choices, default="Unknown")
            
            return merged_df
        except Exception as e:
            st.error(f"Error computing EUMI: {str(e)}")
            return None
    
    eumi_data = compute_eumi_data()
    
    if eumi_data is not None and not eumi_data.empty:
        # Modern KPI Cards with Professional Styling
        over_enrolled = (eumi_data['category'] == "Over-enrolled, under-used").sum()
        balanced = (eumi_data['category'] == "Balanced").sum()
        under_enrolled = (eumi_data['category'] == "Under-enrolled, high-usage").sum()
        
        col1, col2, col3 = st.columns(3, gap="medium")
        
        # Over-Enrolled Card (Red/Orange theme)
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%);
                border: 1px solid #fecaca;
                border-radius: 12px;
                padding: 1.75rem;
                text-align: center;
                box-shadow: 0 2px 8px rgba(239, 68, 68, 0.08);
                transition: all 0.3s ease;
            ">
                <div style="
                    font-size: 0.85rem;
                    color: #991b1b;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 0.75rem;
                ">
                    Over-Enrolled
                </div>
                <div style="
                    font-size: 3rem;
                    font-weight: 700;
                    color: #dc2626;
                    margin-bottom: 0.5rem;
                    line-height: 1;
                ">
                    {over_enrolled}
                </div>
                <div style="
                    font-size: 0.9rem;
                    color: #7f1d1d;
                    font-weight: 500;
                ">
                    Under-used Districts
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Balanced Card (Green theme)
        with col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                border: 1px solid #86efac;
                border-radius: 12px;
                padding: 1.75rem;
                text-align: center;
                box-shadow: 0 2px 8px rgba(34, 197, 94, 0.08);
                transition: all 0.3s ease;
            ">
                <div style="
                    font-size: 0.85rem;
                    color: #166534;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 0.75rem;
                ">
                    Balanced
                </div>
                <div style="
                    font-size: 3rem;
                    font-weight: 700;
                    color: #22c55e;
                    margin-bottom: 0.5rem;
                    line-height: 1;
                ">
                    {balanced}
                </div>
                <div style="
                    font-size: 0.9rem;
                    color: #15803d;
                    font-weight: 500;
                ">
                    Optimal Districts
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Under-Enrolled Card (Blue theme)
        with col3:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                border: 1px solid #93c5fd;
                border-radius: 12px;
                padding: 1.75rem;
                text-align: center;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.08);
                transition: all 0.3s ease;
            ">
                <div style="
                    font-size: 0.85rem;
                    color: #1e40af;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 0.75rem;
                ">
                    Under-Enrolled
                </div>
                <div style="
                    font-size: 3rem;
                    font-weight: 700;
                    color: #3b82f6;
                    margin-bottom: 0.5rem;
                    line-height: 1;
                ">
                    {under_enrolled}
                </div>
                <div style="
                    font-size: 0.9rem;
                    color: #1e3a8a;
                    font-weight: 500;
                ">
                    High-Usage Districts
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add spacing
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        
        # Modern Tab Navigation
        tab1, tab2, tab3 = st.tabs(["📊 Scatter Plot", "📈 Summary Statistics", "📋 District Breakdown"])
        
        with tab1:
            st.markdown("""
            <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.3rem; font-weight: 600; color: #1a1a2e; margin: 0;">
                    EUMI Scatter Plot
                </h3>
                <p style="font-size: 0.9rem; color: #6c757d; margin: 0.5rem 0 0 0;">
                    Visualize enrollment share vs biometric usage share by district
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            fig = px.scatter(
                eumi_data,
                x='enroll_share',
                y='usage_share',
                color='category',
                hover_data=['district', 'total_enrolment', 'total_bio', 'EUMI'],
                title=None,
                labels={
                    'enroll_share': 'Enrollment Share (%)',
                    'usage_share': 'Biometric Usage Share (%)',
                    'category': 'Category'
                },
                color_discrete_map={
                    "Over-enrolled, under-used": "#ef4444",
                    "Balanced": "#22c55e",
                    "Under-enrolled, high-usage": "#3b82f6"
                }
            )
            
            # Add diagonal line for perfect balance
            max_val = max(eumi_data['enroll_share'].max(), eumi_data['usage_share'].max())
            fig.add_shape(
                type="line",
                x0=0, y0=0,
                x1=max_val, y1=max_val,
                line=dict(dash="dash", color="rgba(100, 100, 100, 0.5)", width=2),
                name="Perfect Balance (1:1)"
            )
            
            fig.update_layout(
                height=550,
                hovermode='closest',
                plot_bgcolor='rgba(240, 242, 245, 0.5)',
                paper_bgcolor='white',
                font=dict(family="Inter, sans-serif", size=11),
                margin=dict(l=50, r=50, t=30, b=50)
            )
            fig.update_xaxes(gridcolor='rgba(200, 200, 200, 0.2)', showgrid=True)
            fig.update_yaxes(gridcolor='rgba(200, 200, 200, 0.2)', showgrid=True)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown("""
            <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.3rem; font-weight: 600; color: #1a1a2e; margin: 0;">
                    Summary Statistics
                </h3>
                <p style="font-size: 0.9rem; color: #6c757d; margin: 0.5rem 0 0 0;">
                    Top districts by enrollment and usage imbalance
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%);
                    border: 1px solid #fecaca;
                    border-radius: 10px;
                    padding: 1.25rem;
                    margin-bottom: 1rem;
                ">
                    <h4 style="
                        font-size: 1rem;
                        font-weight: 600;
                        color: #991b1b;
                        margin: 0 0 1rem 0;
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                    ">
                        🔴 Over-Enrolled Districts
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                over_used = eumi_data[eumi_data['category'] == "Over-enrolled, under-used"].nlargest(10, 'enroll_share')[
                    ['district', 'state', 'total_enrolment', 'EUMI']
                ].copy()
                over_used.columns = ['District', 'State', 'Enrollments', 'EUMI']
                over_used['Enrollments'] = over_used['Enrollments'].apply(lambda x: f"{int(x):,}")
                over_used['EUMI'] = over_used['EUMI'].apply(lambda x: f"{x:.2f}")
                
                st.dataframe(
                    over_used,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "District": st.column_config.TextColumn(width="medium"),
                        "State": st.column_config.TextColumn(width="small"),
                        "Enrollments": st.column_config.TextColumn(width="small"),
                        "EUMI": st.column_config.TextColumn(width="small")
                    }
                )
            
            with col2:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                    border: 1px solid #93c5fd;
                    border-radius: 10px;
                    padding: 1.25rem;
                    margin-bottom: 1rem;
                ">
                    <h4 style="
                        font-size: 1rem;
                        font-weight: 600;
                        color: #1e40af;
                        margin: 0 0 1rem 0;
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                    ">
                        🔵 Under-Enrolled Districts
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                under_used = eumi_data[eumi_data['category'] == "Under-enrolled, high-usage"].nlargest(10, 'usage_share')[
                    ['district', 'state', 'total_bio', 'EUMI']
                ].copy()
                under_used.columns = ['District', 'State', 'Biometric Usage', 'EUMI']
                under_used['Biometric Usage'] = under_used['Biometric Usage'].apply(lambda x: f"{int(x):,}")
                under_used['EUMI'] = under_used['EUMI'].apply(lambda x: f"{x:.2f}")
                
                st.dataframe(
                    under_used,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "District": st.column_config.TextColumn(width="medium"),
                        "State": st.column_config.TextColumn(width="small"),
                        "Biometric Usage": st.column_config.TextColumn(width="small"),
                        "EUMI": st.column_config.TextColumn(width="small")
                    }
                )
        
        with tab3:
            st.markdown("""
            <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.3rem; font-weight: 600; color: #1a1a2e; margin: 0;">
                    District Breakdown
                </h3>
                <p style="font-size: 0.9rem; color: #6c757d; margin: 0.5rem 0 0 0;">
                    Complete EUMI analysis for all districts
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            display_df = eumi_data[['district', 'state', 'total_enrolment', 'total_bio', 'enroll_share', 'usage_share', 'EUMI', 'category']].copy()
            display_df.columns = ['District', 'State', 'Enrollments', 'Biometric Usage', 'Enroll Share', 'Usage Share', 'EUMI', 'Category']
            display_df = display_df.sort_values('EUMI', ascending=False)
            
            # Format numbers for display
            display_df['Enrollments'] = display_df['Enrollments'].apply(lambda x: f"{int(x):,}")
            display_df['Biometric Usage'] = display_df['Biometric Usage'].apply(lambda x: f"{int(x):,}")
            display_df['Enroll Share'] = display_df['Enroll Share'].apply(lambda x: f"{x*100:.2f}%")
            display_df['Usage Share'] = display_df['Usage Share'].apply(lambda x: f"{x*100:.2f}%")
            display_df['EUMI'] = display_df['EUMI'].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "N/A")
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "District": st.column_config.TextColumn(width="medium"),
                    "State": st.column_config.TextColumn(width="small"),
                    "Enrollments": st.column_config.TextColumn(width="small"),
                    "Biometric Usage": st.column_config.TextColumn(width="small"),
                    "Enroll Share": st.column_config.TextColumn(width="small"),
                    "Usage Share": st.column_config.TextColumn(width="small"),
                    "EUMI": st.column_config.TextColumn(width="small"),
                    "Category": st.column_config.TextColumn(width="medium")
                }
            )
    else:
        st.error("Unable to compute EUMI. Please check that both enrollment and biometric datasets are available.")

# ================================================================================

# ================================================================================
# FOOTER
# ================================================================================

st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0; color: #6c757d;">
    <p style="margin: 0; font-size: 0.8rem;">
        🇮🇳 UIDAI Aadhaar Analytics Platform | Data Hackathon 2026 | Powered by Python & Streamlit
    </p>
</div>
""", unsafe_allow_html=True)
