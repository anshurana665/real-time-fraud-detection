import time
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import pydeck as pdk
from sqlalchemy import create_engine
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sentinel AI | Global Intel",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. DARK CYBERPUNK CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;500;700&display=swap');
    
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }

    .glass-card {
        background: rgba(20, 20, 20, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00f2ff;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
    }
    
    .metric-label {
        color: #888;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.8rem;
    }
    
    /* Hide Streamlit elements */
    header, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADER (With Demo Mode) ---
def load_data():
    try:
        # Try connecting to Local DB
        engine = create_engine('postgresql://admin:password@localhost:6543/fraud_db')
        query = "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 1000"
        df = pd.read_sql(query, engine)
        return df
    except:
        # CLOUD MODE: Generate fake data if DB is unreachable
        dates = pd.date_range(end=pd.Timestamp.now(), periods=200, freq='s')
        data = {
            'amount': np.random.uniform(10, 5000, size=200),
            'is_fraud': np.random.choice([0, 1], size=200, p=[0.90, 0.10]),
            'merchant_id': np.random.choice([f'M{i}' for i in range(10, 20)], size=200),
            'user_id': np.random.randint(1000, 1050, size=200),
            'city': np.random.choice(['New York', 'London', 'Tokyo', 'Berlin', 'Mumbai'], size=200),
            'latitude': np.random.uniform(40.6, 40.9, size=200),
            'longitude': np.random.uniform(-74.1, -73.8, size=200),
            'timestamp': [d.timestamp() for d in dates] # Store as unix timestamp to match DB
        }
        return pd.DataFrame(data)

# --- 4. HEADER ---
c1, c2 = st.columns([8, 2])
with c1:
    st.markdown("<h1 style='margin:0; font-size: 3rem; color: white;'>SENTINEL <span style='color:#ff2a6d'>// GLOBAL</span></h1>", unsafe_allow_html=True)
with c2:
    st.markdown("<div style='text-align:right; padding-top:15px; color:#00f2ff; font-weight:bold;'>● SYSTEM LIVE</div>", unsafe_allow_html=True)
    # Download Button
    df_download = load_data()
    if not df_download.empty:
        csv = df_download.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Log", csv, "fraud_log.csv", "text/csv")

st.markdown("---")

# --- 5. DASHBOARD LOOP ---
placeholder = st.empty()

while True:
    df = load_data()
    
    with placeholder.container():
        if not df.empty:
            # FIX TIMESTAMP: Convert Unix float to datetime object
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            
            total_txns = len(df)
            fraud_txns = df[df['is_fraud'] == 1]
            fraud_count = len(fraud_txns)
            total_vol = df['amount'].sum()
            
            # --- METRICS ---
            m1, m2, m3, m4 = st.columns(4)
            def metric_html(label, value, color="#00f2ff"):
                return f"""
                <div class="glass-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color:{color}; text-shadow: 0 0 15px {color}40;">{value}</div>
                </div>
                """
            with m1: st.markdown(metric_html("Live Traffic", total_txns), unsafe_allow_html=True)
            with m2: st.markdown(metric_html("Threats Detected", fraud_count, "#ff2a6d"), unsafe_allow_html=True)
            with m3: st.markdown(metric_html("Volume Scanned", f"${total_vol/1000000:.2f}M"), unsafe_allow_html=True)
            with m4: st.markdown(metric_html("Active Nodes", "5"), unsafe_allow_html=True)

            # --- MAP ---
            st.markdown('<div class="glass-card" style="padding:0; overflow:hidden;">', unsafe_allow_html=True)
            view_state = pdk.ViewState(latitude=39.82, longitude=-98.57, zoom=3, pitch=0)
            
            # Layer 1: All Transactions (Faint Blue Dots) - Added back for context
            layer_all = pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position='[longitude, latitude]',
                get_color='[0, 242, 255, 30]', # Faint Cyan
                get_radius=30000,
            )

            layer_fraud = pdk.Layer(
                "ScatterplotLayer",
                data=fraud_txns,
                get_position='[longitude, latitude]',
                get_color='[255, 42, 109, 200]',
                get_radius=50000,
                pickable=True,
                stroked=True,
                filled=True,
                get_line_color=[255, 255, 255],
                line_width_min_pixels=1,
            )
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/dark-v10',
                initial_view_state=view_state,
                layers=[layer_all, layer_fraud],
                tooltip={"html": "<b>ALERT:</b> {city}<br/><b>Amt:</b> ${amount}"}
            ))
            st.markdown('</div>', unsafe_allow_html=True)

            # --- LOGS & CHART ---
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader("🛑 Threat Feed")
                # Show clean DateTime instead of raw timestamp
                st.dataframe(
                    df[['datetime', 'city', 'amount', 'is_fraud']].head(8),
                    column_config={
                        "datetime": st.column_config.DatetimeColumn("Time", format="D MMM, HH:mm:ss"),
                        "city": "Location",
                        "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                        "is_fraud": st.column_config.CheckboxColumn("Blocked?", disabled=True)
                    },
                    use_container_width=True,
                    hide_index=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader("🧊 Vector Anomaly")
                fig_3d = px.scatter_3d(
                    df, x='user_id', y='merchant_id', z='amount',
                    color='is_fraud',
                    color_discrete_map={0: 'rgba(0, 242, 255, 0.1)', 1: '#ff2a6d'},
                    opacity=0.9, height=300
                )
                fig_3d.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', scene=dict(bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)), showlegend=False, margin=dict(l=0, r=0, b=0, t=0))
                st.plotly_chart(fig_3d, use_container_width=True)

    time.sleep(2)