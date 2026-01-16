"""
================================================================================
UIDAI AADHAAR ANALYTICS PLATFORM
A Professional, Executive-Grade Dashboard for the UIDAI Data Hackathon
================================================================================
Features:
- Dark theme with glassmorphism effects
- State-wise filtering on all graphs
- Enhanced navigation with icons and tooltips
- Interactive Data Explorer with anomaly detection
- Executive insights and KPIs
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
# CUSTOM CSS - MODERN DARK THEME WITH GLASSMORPHISM
# ================================================================================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(26, 26, 46, 0.98) 0%, rgba(22, 33, 62, 0.98) 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Main Title */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .sub-title {
        font-size: 1rem;
        color: #a0a0a0;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* Glass Card Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        margin: 0.75rem 0;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(102, 126, 234, 0.4);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
    }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        font-size: 0.8rem;
        color: #a0a0a0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-delta {
        font-size: 0.85rem;
        color: #4ade80;
        font-weight: 500;
    }
    
    /* Insight Cards */
    .insight-card {
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.1) 0%, rgba(56, 189, 248, 0.1) 100%);
        border: 1px solid rgba(34, 211, 238, 0.3);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.5rem 0;
    }
    
    .insight-card-warning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    
    .insight-card-success {
        background: linear-gradient(135deg, rgba(74, 222, 128, 0.1) 0%, rgba(34, 197, 94, 0.1) 100%);
        border: 1px solid rgba(74, 222, 128, 0.3);
    }
    
    .insight-card-danger {
        background: linear-gradient(135deg, rgba(248, 113, 113, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%);
        border: 1px solid rgba(248, 113, 113, 0.3);
    }
    
    .insight-title {
        font-size: 1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .insight-text {
        font-size: 0.9rem;
        color: #d0d0d0;
        line-height: 1.5;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-header::after {
        content: '';
        flex-grow: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.5), transparent);
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0a0a0 !important;
    }
    
    /* Navigation Pills */
    .nav-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        padding: 0.5rem 0;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        padding: 0.85rem 1rem;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #a0a0a0;
        text-decoration: none;
        font-size: 0.95rem;
    }
    
    .nav-item:hover {
        background: rgba(102, 126, 234, 0.15);
        color: #ffffff;
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
        color: #ffffff;
        border: 1px solid rgba(102, 126, 234, 0.4);
    }
    
    .nav-icon {
        font-size: 1.2rem;
        margin-right: 0.75rem;
        width: 24px;
        text-align: center;
    }
    
    /* Filter Section */
    .filter-card {
        background: rgba(102, 126, 234, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .filter-label {
        color: #a0a0a0;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    /* Divider */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent);
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
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
        border: 1px solid rgba(102, 126, 234, 0.4);
    }
    
    .badge-success {
        background: rgba(74, 222, 128, 0.2);
        color: #4ade80;
        border: 1px solid rgba(74, 222, 128, 0.4);
    }
    
    .badge-warning {
        background: rgba(251, 191, 36, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.4);
    }
    
    .badge-danger {
        background: rgba(248, 113, 113, 0.2);
        color: #f87171;
        border: 1px solid rgba(248, 113, 113, 0.4);
    }
    
    /* Stat Box */
    .stat-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #888;
        margin-top: 0.25rem;
    }
    
    /* Anomaly indicator */
    .anomaly-high {
        background: rgba(248, 113, 113, 0.2);
        color: #f87171;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    .anomaly-low {
        background: rgba(74, 222, 128, 0.2);
        color: #4ade80;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.03);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #a0a0a0;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
        color: white;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ================================================================================
# DATA LOADING
# ================================================================================

@st.cache_data(ttl=3600)
def load_all_data():
    """Load all three datasets: demographic, enrolment, biometric"""
    # CSV folders are in the same directory as this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    datasets = {}
    
    # Load Enrolment Data
    enrol_dir = os.path.join(base_dir, "api_data_aadhar_enrolment")
    if os.path.exists(enrol_dir):
        dfs = []
        for f in sorted(os.listdir(enrol_dir)):
            if f.endswith('.csv'):
                dfs.append(pd.read_csv(os.path.join(enrol_dir, f)))
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df['total_enrolment'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
            datasets['enrolment'] = df
    
    # Load Demographic Data
    demo_dir = os.path.join(base_dir, "api_data_aadhar_demographic")
    if os.path.exists(demo_dir):
        dfs = []
        for f in sorted(os.listdir(demo_dir)):
            if f.endswith('.csv'):
                dfs.append(pd.read_csv(os.path.join(demo_dir, f)))
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df['total_demo'] = df['demo_age_5_17'] + df['demo_age_17_']
            datasets['demographic'] = df
    
    # Load Biometric Data
    bio_dir = os.path.join(base_dir, "api_data_aadhar_biometric")
    if os.path.exists(bio_dir):
        dfs = []
        for f in sorted(os.listdir(bio_dir)):
            if f.endswith('.csv'):
                dfs.append(pd.read_csv(os.path.join(bio_dir, f)))
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df['total_bio'] = df['bio_age_5_17'] + df['bio_age_17_']
            datasets['biometric'] = df
    
    return datasets

# Load data
with st.spinner('Loading UIDAI datasets...'):
    data = load_all_data()
    df_enrol = data.get('enrolment', pd.DataFrame())
    df_demo = data.get('demographic', pd.DataFrame())
    df_bio = data.get('biometric', pd.DataFrame())

# Get list of states for filtering
all_states = sorted(df_enrol['state'].unique().tolist()) if not df_enrol.empty else []

# ================================================================================
# SIDEBAR - ENHANCED NAVIGATION
# ================================================================================

with st.sidebar:
    # Logo and Title
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <span style="font-size: 3rem;">🇮🇳</span>
        <h2 style="color: #ffffff; margin: 0.5rem 0 0.25rem 0; font-weight: 700; font-size: 1.3rem;">UIDAI Analytics</h2>
        <p style="color: #667eea; font-size: 0.8rem; margin: 0;">Data Hackathon 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Navigation
    st.markdown('<p style="color: #888; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">📊 ANALYTICS</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigation",
        [
            "🏠 Executive Summary",
            "📈 Biometric Lag Analysis",
            "👶 Age Cohort Efficiency",
            "🗺️ Geographic Intelligence",
            "🔮 Predictive Analytics",
            "🔍 Data Explorer"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Global State Filter
    st.markdown('<p style="color: #888; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">🎯 FILTERS</p>', unsafe_allow_html=True)
    
    selected_states = st.multiselect(
        "Filter by State(s)",
        options=all_states,
        default=[],
        placeholder="All States",
        help="Select one or more states to filter all visualizations"
    )
    
    # Apply filter
    if selected_states:
        if not df_enrol.empty:
            df_enrol = df_enrol[df_enrol['state'].isin(selected_states)]
        if not df_demo.empty:
            df_demo = df_demo[df_demo['state'].isin(selected_states)]
        if not df_bio.empty:
            df_bio = df_bio[df_bio['state'].isin(selected_states)]
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Quick Stats
    st.markdown('<p style="color: #888; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">📋 QUICK STATS</p>', unsafe_allow_html=True)
    
    if not df_enrol.empty:
        st.markdown(f"""
        <div class="glass-card" style="padding: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                <span style="color: #888; font-size: 0.75rem;">Records</span>
                <span style="color: #fff; font-weight: 600;">{len(df_enrol):,}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                <span style="color: #888; font-size: 0.75rem;">States</span>
                <span style="color: #fff; font-weight: 600;">{df_enrol['state'].nunique()}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #888; font-size: 0.75rem;">Districts</span>
                <span style="color: #fff; font-weight: 600;">{df_enrol['district'].nunique()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================
# HELPER FUNCTION: Apply state filter indicator
# ================================================================================
def show_filter_indicator():
    if selected_states:
        states_text = ", ".join(selected_states[:3])
        if len(selected_states) > 3:
            states_text += f" +{len(selected_states)-3} more"
        st.markdown(f"""
        <div class="filter-card">
            <span style="color: #667eea; font-size: 0.85rem;">🎯 Filtered: </span>
            <span style="color: #fff; font-size: 0.85rem;">{states_text}</span>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================
# PAGE: EXECUTIVE SUMMARY
# ================================================================================

if page == "🏠 Executive Summary":
    st.markdown("""
    <h1 class="main-title">UIDAI Aadhaar Analytics Platform</h1>
    <p class="sub-title">Comprehensive Intelligence Dashboard for India's Digital Identity Infrastructure</p>
    """, unsafe_allow_html=True)
    
    show_filter_indicator()
    
    # Key Metrics Row
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
    
    # Key Insights Grid
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
    
    # Trend Chart
    st.markdown('<p class="section-header">📈 Enrolment Trends</p>', unsafe_allow_html=True)
    
    if not df_enrol.empty:
        daily = df_enrol.groupby('date')['total_enrolment'].sum().reset_index()
        daily['rolling_7d'] = daily['total_enrolment'].rolling(7, min_periods=1).mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily['date'], y=daily['total_enrolment'],
            mode='lines', name='Daily Volume',
            line=dict(color='rgba(102, 126, 234, 0.3)', width=1),
            fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        
        fig.add_trace(go.Scatter(
            x=daily['date'], y=daily['rolling_7d'],
            mode='lines', name='7-Day Average',
            line=dict(color='#667eea', width=3)
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=350, margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='Enrolments'),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ================================================================================
# PAGE: BIOMETRIC LAG ANALYSIS
# ================================================================================

elif page == "📈 Biometric Lag Analysis":
    st.markdown("""
    <h1 class="main-title">Biometric Deployment Analysis</h1>
    <p class="sub-title">Gap between demographic registration and biometric verification</p>
    """, unsafe_allow_html=True)
    
    show_filter_indicator()
    
    if not df_demo.empty and not df_bio.empty:
        # Compute cumulative
        demo_daily = df_demo.groupby('date')['total_demo'].sum().reset_index().sort_values('date')
        bio_daily = df_bio.groupby('date')['total_bio'].sum().reset_index().sort_values('date')
        
        demo_daily['cum'] = demo_daily['total_demo'].cumsum()
        bio_daily['cum'] = bio_daily['total_bio'].cumsum()
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">Total Demographic</p>
                <p class="kpi-value">{demo_daily['cum'].iloc[-1]/1e6:.1f}M</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">Total Biometric</p>
                <p class="kpi-value">{bio_daily['cum'].iloc[-1]/1e6:.1f}M</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            ratio = bio_daily['cum'].iloc[-1] / demo_daily['cum'].iloc[-1] if demo_daily['cum'].iloc[-1] > 0 else 0
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">Bio/Demo Ratio</p>
                <p class="kpi-value">{ratio:.2f}x</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        # Chart
        st.markdown('<p class="section-header">📊 Cumulative Comparison</p>', unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=demo_daily['date'], y=demo_daily['cum'], mode='lines',
                                  name='Demographic', line=dict(color='#3b82f6', width=3),
                                  fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)'))
        fig.add_trace(go.Scatter(x=bio_daily['date'], y=bio_daily['cum'], mode='lines',
                                  name='Biometric', line=dict(color='#10b981', width=3),
                                  fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.1)'))
        
        fig.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=400, margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            yaxis=dict(title='Cumulative Count', showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # State comparison
        st.markdown('<p class="section-header">🗺️ State-wise Comparison</p>', unsafe_allow_html=True)
        
        state_demo = df_demo.groupby('state')['total_demo'].sum()
        state_bio = df_bio.groupby('state')['total_bio'].sum()
        comparison = pd.DataFrame({'Demographic': state_demo, 'Biometric': state_bio}).fillna(0)
        comparison = comparison.sort_values('Demographic', ascending=False).head(12)
        
        fig_state = px.bar(comparison.reset_index(), x='state', y=['Demographic', 'Biometric'],
                           barmode='group', template='plotly_dark',
                           color_discrete_sequence=['#3b82f6', '#10b981'])
        fig_state.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                height=350, xaxis_tickangle=-45,
                                legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_state, use_container_width=True)

# ================================================================================
# PAGE: AGE COHORT EFFICIENCY
# ================================================================================

elif page == "👶 Age Cohort Efficiency":
    st.markdown("""
    <h1 class="main-title">Age Cohort Analysis</h1>
    <p class="sub-title">Enrolment patterns and efficiency across age groups</p>
    """, unsafe_allow_html=True)
    
    show_filter_indicator()
    
    if not df_enrol.empty:
        age_0_5 = df_enrol['age_0_5'].sum()
        age_5_17 = df_enrol['age_5_17'].sum()
        age_18 = df_enrol['age_18_greater'].sum()
        total = age_0_5 + age_5_17 + age_18
        
        effort_0_5 = age_0_5 * 4.0
        effort_5_17 = age_5_17 * 1.5
        effort_18 = age_18 * 1.0
        total_effort = effort_0_5 + effort_5_17 + effort_18
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="kpi-card" style="border-color: rgba(248, 113, 113, 0.5);">
                <p class="kpi-label">Age 0-5 Years</p>
                <p class="kpi-value" style="color: #f87171;">{age_0_5/1e6:.2f}M</p>
                <p class="kpi-delta" style="color: #f87171;">{age_0_5/total*100:.1f}% volume</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="kpi-card" style="border-color: rgba(251, 191, 36, 0.5);">
                <p class="kpi-label">Age 5-17 Years</p>
                <p class="kpi-value" style="color: #fbbf24;">{age_5_17/1e6:.2f}M</p>
                <p class="kpi-delta" style="color: #fbbf24;">{age_5_17/total*100:.1f}% volume</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="kpi-card" style="border-color: rgba(74, 222, 128, 0.5);">
                <p class="kpi-label">Age 18+ Years</p>
                <p class="kpi-value" style="color: #4ade80;">{age_18/1e3:.0f}K</p>
                <p class="kpi-delta">{age_18/total*100:.1f}% volume</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<p class="section-header">📊 Volume Distribution</p>', unsafe_allow_html=True)
            fig_pie = go.Figure(data=[go.Pie(
                labels=['0-5 Years', '5-17 Years', '18+ Years'],
                values=[age_0_5, age_5_17, age_18], hole=0.6,
                marker=dict(colors=['#f87171', '#fbbf24', '#4ade80']),
                textinfo='percent', textfont=dict(size=14, color='white')
            )])
            fig_pie.update_layout(
                template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=320,
                showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
                annotations=[dict(text=f'{total/1e6:.1f}M', x=0.5, y=0.5, font_size=22, font_color='white', showarrow=False)]
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown('<p class="section-header">⚡ Effort Distribution</p>', unsafe_allow_html=True)
            fig_effort = go.Figure(data=[go.Bar(
                x=['0-5 Years', '5-17 Years', '18+ Years'],
                y=[effort_0_5/total_effort*100, effort_5_17/total_effort*100, effort_18/total_effort*100],
                marker=dict(color=['#f87171', '#fbbf24', '#4ade80']),
                text=[f'{effort_0_5/total_effort*100:.1f}%', f'{effort_5_17/total_effort*100:.1f}%', f'{effort_18/total_effort*100:.1f}%'],
                textposition='outside'
            )])
            fig_effort.update_layout(
                template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=320,
                yaxis=dict(title='Effort Share (%)', showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                bargap=0.4
            )
            st.plotly_chart(fig_effort, use_container_width=True)

# ================================================================================
# PAGE: GEOGRAPHIC INTELLIGENCE
# ================================================================================

elif page == "🗺️ Geographic Intelligence":
    st.markdown("""
    <h1 class="main-title">Geographic Intelligence</h1>
    <p class="sub-title">Tier-wise analysis of enrolment infrastructure</p>
    """, unsafe_allow_html=True)
    
    show_filter_indicator()
    
    if not df_enrol.empty:
        state_totals = df_enrol.groupby('state').agg({
            'total_enrolment': 'sum', 'district': 'nunique', 'pincode': 'nunique'
        }).reset_index()
        state_totals.columns = ['State', 'Enrolments', 'Districts', 'Pincodes']
        state_totals = state_totals.sort_values('Enrolments', ascending=False)
        
        st.markdown('<p class="section-header">🏆 Top States by Enrolment</p>', unsafe_allow_html=True)
        
        top_15 = state_totals.head(15)
        fig = px.bar(top_15, x='State', y='Enrolments', template='plotly_dark',
                     color='Enrolments', color_continuous_scale='Viridis')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          height=350, xaxis_tickangle=-45, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        # Pareto
        st.markdown('<p class="section-header">📊 Pareto Analysis (80/20)</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            sorted_df = state_totals.copy()
            sorted_df['CumPct'] = sorted_df['Enrolments'].cumsum() / sorted_df['Enrolments'].sum() * 100
            
            fig_p = make_subplots(specs=[[{"secondary_y": True}]])
            fig_p.add_trace(go.Bar(x=sorted_df['State'].head(15), y=sorted_df['Enrolments'].head(15),
                                   name='Enrolments', marker_color='#667eea'), secondary_y=False)
            fig_p.add_trace(go.Scatter(x=sorted_df['State'].head(15), y=sorted_df['CumPct'].head(15),
                                       name='Cumulative %', line=dict(color='#f59e0b', width=3)), secondary_y=True)
            fig_p.add_hline(y=80, line_dash="dash", line_color="rgba(248, 113, 113, 0.5)",
                           annotation_text="80%", secondary_y=True)
            fig_p.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=350, xaxis_tickangle=-45)
            st.plotly_chart(fig_p, use_container_width=True)
        
        with col2:
            states_80 = len(sorted_df[sorted_df['CumPct'] <= 80])
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; padding: 2rem;">
                <p style="color: #888; font-size: 0.8rem; margin-bottom: 1rem;">CONCENTRATION</p>
                <p style="font-size: 3rem; font-weight: 800; color: #667eea; margin: 0;">{states_80}</p>
                <p style="color: #aaa; margin-top: 0.5rem;">states generate 80%</p>
            </div>
            """, unsafe_allow_html=True)

# ================================================================================
# PAGE: PREDICTIVE ANALYTICS
# ================================================================================

elif page == "🔮 Predictive Analytics":
    st.markdown("""
    <h1 class="main-title">Predictive Analytics</h1>
    <p class="sub-title">ML-powered insights for proactive decision making</p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <p class="kpi-label">Model Accuracy</p>
            <p class="kpi-value">80.6%</p>
            <p class="kpi-delta">Random Forest</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <p class="kpi-label">ROC-AUC</p>
            <p class="kpi-value">0.786</p>
            <p class="kpi-delta">Good</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <p class="kpi-label">Gini Coefficient</p>
            <p class="kpi-value">0.572</p>
            <p class="kpi-delta">Moderate</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">📊 Feature Importance</p>', unsafe_allow_html=True)
    
    importance = pd.DataFrame({
        'Feature': ['Backlog (Lag 1)', 'Biometric (Lag 1)', 'Demographic (Lag 1)', 
                   'Demographic (Lag 2)', 'Biometric (Lag 2)', '% Age 5-17', '% Age 0-5', '% Age 18+', 'Tier'],
        'Importance': [0.2959, 0.1253, 0.1202, 0.1035, 0.0902, 0.0886, 0.0843, 0.0737, 0.0183]
    })
    
    fig = px.bar(importance, x='Importance', y='Feature', orientation='h',
                 template='plotly_dark', color='Importance', color_continuous_scale='Viridis')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=350, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="insight-card">
            <p class="insight-title">🔑 Key Predictor: Backlog</p>
            <p class="insight-text">Previous week's backlog accounts for <strong>30%</strong> of predictive power.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="insight-card">
            <p class="insight-title">📈 Early Warning</p>
            <p class="insight-text">2-week historical data enables proactive intervention.</p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================
# PAGE: DATA EXPLORER (ENHANCED)
# ================================================================================

elif page == "🔍 Data Explorer":
    st.markdown("""
    <h1 class="main-title">Data Explorer</h1>
    <p class="sub-title">Deep-dive analysis with anomaly detection and statistical insights</p>
    """, unsafe_allow_html=True)
    
    show_filter_indicator()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Statistical Summary", "🔴 Anomaly Detection", "📈 District Analysis", "📋 Raw Data"])
    
    with tab1:
        st.markdown('<p class="section-header">📊 Statistical Overview</p>', unsafe_allow_html=True)
        
        if not df_enrol.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            daily_totals = df_enrol.groupby('date')['total_enrolment'].sum()
            
            with col1:
                st.markdown(f"""
                <div class="stat-box">
                    <p class="stat-value">{daily_totals.mean()/1e3:.1f}K</p>
                    <p class="stat-label">Daily Mean</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stat-box">
                    <p class="stat-value">{daily_totals.median()/1e3:.1f}K</p>
                    <p class="stat-label">Daily Median</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="stat-box">
                    <p class="stat-value">{daily_totals.std()/1e3:.1f}K</p>
                    <p class="stat-label">Std Deviation</p>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                cv = daily_totals.std() / daily_totals.mean() * 100
                st.markdown(f"""
                <div class="stat-box">
                    <p class="stat-value">{cv:.1f}%</p>
                    <p class="stat-label">CV (Volatility)</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
            
            # Distribution chart
            st.markdown('<p class="section-header">📈 Daily Distribution</p>', unsafe_allow_html=True)
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=daily_totals, nbinsx=30, marker_color='#667eea', opacity=0.7))
            fig.add_vline(x=daily_totals.mean(), line_dash="dash", line_color="#f59e0b", annotation_text="Mean")
            fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=300,
                              xaxis_title='Daily Enrolments', yaxis_title='Frequency')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown('<p class="section-header">🔴 Anomaly Detection</p>', unsafe_allow_html=True)
        
        # Explanation for first-time visitors
        st.markdown("""
        <div class="insight-card" style="margin-bottom: 1.5rem;">
            <p class="insight-title">📌 What is Anomaly Detection?</p>
            <p class="insight-text">
                This analysis identifies <strong>unusual spikes or drops</strong> in daily enrolment volumes. 
                Anomalies may indicate:
                <br>• <strong>Special campaigns</strong> (government drives, school enrolments)
                <br>• <strong>System issues</strong> (downtime, data entry backlogs)
                <br>• <strong>Seasonal patterns</strong> (festivals, holidays)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if not df_enrol.empty:
            # Detect anomalies using IQR
            daily = df_enrol.groupby('date')['total_enrolment'].sum().reset_index()
            q1 = daily['total_enrolment'].quantile(0.25)
            q3 = daily['total_enrolment'].quantile(0.75)
            iqr = q3 - q1
            upper = q3 + 1.5 * iqr
            lower = max(0, q1 - 1.5 * iqr)  # Don't show negative threshold
            
            daily['anomaly'] = (daily['total_enrolment'] > upper) | (daily['total_enrolment'] < lower)
            anomalies = daily[daily['anomaly']]
            high_anomalies = anomalies[anomalies['total_enrolment'] > upper]
            low_anomalies = anomalies[anomalies['total_enrolment'] < lower]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=daily['date'], y=daily['total_enrolment'], mode='lines',
                                         name='Daily Volume', line=dict(color='#667eea')))
                fig.add_trace(go.Scatter(x=anomalies['date'], y=anomalies['total_enrolment'], mode='markers',
                                         name='Anomalies', marker=dict(color='#f87171', size=12, symbol='x')))
                fig.add_hline(y=upper, line_dash="dash", line_color="rgba(248, 113, 113, 0.5)", 
                             annotation_text="Upper Bound (Spike)")
                if lower > 0:
                    fig.add_hline(y=lower, line_dash="dash", line_color="rgba(74, 222, 128, 0.5)", 
                                 annotation_text="Lower Bound (Drop)")
                fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=350,
                                 xaxis_title='Date', yaxis_title='Daily Enrolments',
                                 legend=dict(orientation="h", yanchor="bottom", y=1.02))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(f"""
                <div class="glass-card">
                    <p style="color: #888; font-size: 0.75rem; margin-bottom: 0.5rem;">TOTAL ANOMALIES</p>
                    <p style="font-size: 2.5rem; font-weight: 700; color: #f87171; margin: 0;">{len(anomalies)}</p>
                    <p style="color: #aaa; font-size: 0.8rem;">out of {len(daily)} days ({len(anomalies)/len(daily)*100:.1f}%)</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="glass-card" style="margin-top: 0.75rem;">
                    <p style="color: #888; font-size: 0.7rem;">🔺 HIGH SPIKES</p>
                    <p style="color: #f87171; font-size: 1.5rem; font-weight: 600; margin: 0.25rem 0;">{len(high_anomalies)}</p>
                    <p style="color: #888; font-size: 0.7rem; margin-top: 0.75rem;">🔻 LOW DROPS</p>
                    <p style="color: #4ade80; font-size: 1.5rem; font-weight: 600; margin: 0.25rem 0;">{len(low_anomalies)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="glass-card" style="margin-top: 0.75rem;">
                    <p style="color: #888; font-size: 0.7rem;">DETECTION METHOD</p>
                    <p style="color: #fff; font-size: 0.85rem; margin-top: 0.25rem;">IQR (Interquartile Range)</p>
                    <p style="color: #667eea; font-size: 0.75rem; margin-top: 0.5rem;">Values beyond 1.5×IQR from Q1/Q3</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Show anomaly details
            if len(anomalies) > 0:
                st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
                st.markdown('<p class="section-header">📋 Anomaly Details</p>', unsafe_allow_html=True)
                
                anomaly_details = anomalies.copy()
                anomaly_details['type'] = anomaly_details['total_enrolment'].apply(
                    lambda x: '🔺 High Spike' if x > upper else '🔻 Low Drop'
                )
                anomaly_details['deviation'] = anomaly_details['total_enrolment'].apply(
                    lambda x: f"+{(x-upper)/1e3:.1f}K above" if x > upper else f"{(x-lower)/1e3:.1f}K below"
                )
                anomaly_details['date'] = anomaly_details['date'].dt.strftime('%Y-%m-%d')
                anomaly_details['total_enrolment'] = anomaly_details['total_enrolment'].apply(lambda x: f"{x/1e3:.1f}K")
                
                display_df = anomaly_details[['date', 'total_enrolment', 'type', 'deviation']].rename(columns={
                    'date': 'Date', 'total_enrolment': 'Enrolments', 'type': 'Type', 'deviation': 'Deviation'
                })
                st.dataframe(display_df, use_container_width=True, hide_index=True)
    
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
                top_10 = district_stats.head(10)[['State', 'District', 'Total', 'Efficiency']]
                top_10['Total'] = top_10['Total'].apply(lambda x: f"{x/1e3:.1f}K")
                top_10['Efficiency'] = top_10['Efficiency'].apply(lambda x: f"{x:.0f}")
                st.dataframe(top_10, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("**Top 10 by Efficiency (per Pincode)**")
                efficient = district_stats.nlargest(10, 'Efficiency')[['State', 'District', 'Total', 'Efficiency']]
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
# FOOTER
# ================================================================================

st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0; color: #555;">
    <p style="margin: 0; font-size: 0.8rem;">
        🇮🇳 UIDAI Aadhaar Analytics Platform | Data Hackathon 2025 | Powered by Python & Streamlit
    </p>
</div>
""", unsafe_allow_html=True)
