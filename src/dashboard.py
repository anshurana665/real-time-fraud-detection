import streamlit as st
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
import requests
from streamlit_lottie import st_lottie
from db_utils import get_engine

# --- CONFIGURATION ---
st.set_page_config(
    page_title="SENTINEL // FRAUD DETECTION",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ASSETS & STYLING ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load a "Robot/AI" animation for the Avatar
lottie_avatar = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_w51pcehl.json")
# Load a "Scanning" animation
lottie_scan = load_lottieurl("https://assets7.lottiefiles.com/packages/lf20_x62chJ.json")

# INJECT CUSTOM CSS FOR CYBERPUNK LOOK
st.markdown("""
    <style>
    /* Force Dark Background */
    .stApp {
        background-color: #0e1117;
    }
    /* Neon Text */
    h1, h2, h3 {
        color: #00ff41 !important;
        font-family: 'Courier New', Courier, monospace;
        text-shadow: 0 0 10px #00ff41;
    }
    /* Metrics Styling */
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #00ff41;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px #00ff41;
    }
    label {
        color: #ff0055 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FUNCTIONS ---
def load_data():
    engine = get_engine()
    # Fetch recent transactions with 3D coordinates (Amount, Merchant, User)
    query = "SELECT amount, merchant_id, user_id, is_fraud FROM transactions ORDER BY timestamp DESC LIMIT 200"
    return pd.read_sql(query, engine)

def get_kpis():
    engine = get_engine()
    query = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as fraud_count
    FROM transactions
    """
    df = pd.read_sql(query, engine)
    return df.iloc[0]['total'], df.iloc[0]['fraud_count']

# --- LAYOUT ---

# Header Section
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    # THE AVATAR
    if lottie_avatar:
        st_lottie(lottie_avatar, height=150, key="avatar")
with col2:
    st.title("SENTINEL // AI CORE")
    st.markdown("### SYSTEM STATUS: **ONLINE** | THREAT LEVEL: **ANALYZING**")
with col3:
    if lottie_scan:
        st_lottie(lottie_scan, height=100, key="scan")

st.divider()

# Live Loop
placeholder = st.empty()

while True:
    with placeholder.container():
        # A. Fetch Data
        df = load_data()
        total, frauds = get_kpis()
        
        # B. Metrics Row
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("TOTAL SCANNED", f"{total}", delta="Live Feed")
        k2.metric("THREATS DETECTED", f"{frauds}", delta_color="inverse")
        k3.metric("SYSTEM LOAD", "14ms", "Optimal")
        k4.metric("ACTIVE NODE", "Docker-01", "Connected")

        # C. 3D VISUALIZATION
        fig_3d = px.scatter_3d(
            df, x='user_id', y='merchant_id', z='amount',
            color='is_fraud',
            color_continuous_scale=[(0, "#00ff41"), (1, "#ff0055")],
            title="3D TRANSACTION VECTORS SPACE", opacity=0.8
        )
        fig_3d.update_layout(
            scene=dict(
                xaxis=dict(backgroundcolor="rgb(0, 0, 0)", gridcolor="gray", showbackground=True),
                yaxis=dict(backgroundcolor="rgb(0, 0, 0)", gridcolor="gray", showbackground=True),
                zaxis=dict(backgroundcolor="rgb(0, 0, 0)", gridcolor="gray", showbackground=True),
            ),
            paper_bgcolor="#0e1117", font=dict(color="#00ff41")
        )
        # We add a unique key using the current timestamp so Streamlit knows it's a new frame
        st.plotly_chart(fig_3d, use_container_width=True, key=f"3d_plot_{time.time()}")
        
        # D. Raw Feed
        st.subheader(">> INCOMING DATA STREAM")
        st.dataframe(df.head(5), use_container_width=True)

    time.sleep(1)