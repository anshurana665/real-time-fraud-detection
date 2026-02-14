import time
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import pydeck as pdk
from sqlalchemy import create_engine

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sentinel AI | Command Node",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ADVANCED CSS (Glass/Clay Hybrid) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Global Reset */
    .stApp {
        background-color: #eef2f6;
        color: #2d3436;
        font-family: 'Outfit', sans-serif;
    }

    /* The Pro Clay Card */
    .clay-card {
        background: #eef2f6;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 
            12px 12px 24px #d1d9e6, 
            -12px -12px 24px #ffffff;
        border: 1px solid rgba(255,255,255,0.6);
        transition: transform 0.3s ease;
    }
    .clay-card:hover {
        transform: translateY(-2px);
        box-shadow: 15px 15px 30px #d1d9e6, -15px -15px 30px #ffffff;
    }

    /* Typography & Gradients */
    h1, h2, h3 { font-family: 'Outfit', sans-serif; font-weight: 800; }
    
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #636e72;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(120deg, #2d3436, #636e72);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Status Badges */
    .badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        vertical-align: middle;
        margin-left: 10px;
    }
    .badge-live { background: #dff9fb; color: #00b894; box-shadow: inset 2px 2px 5px rgba(0,0,0,0.05); }
    .badge-alert { background: #ff7675; color: #fff; box-shadow: 3px 3px 10px rgba(214, 48, 49, 0.4); }

    /* Streamlit UI Cleanup */
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & CONFIG (Now with Cloud Demo Mode) ---
def load_data():
    try:
        # 1. Try connecting to Local Database
        engine = create_engine('postgresql://admin:password@localhost:6543/fraud_db')
        query = "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 2000"
        df = pd.read_sql(query, engine)
        
        # Mock Geo-data if missing
        if 'latitude' not in df.columns:
            df['latitude'] = np.random.uniform(40.6, 40.9, size=len(df))
            df['longitude'] = np.random.uniform(-74.1, -73.8, size=len(df))
        return df

    except Exception as e:
        # 2. DEMO MODE: If DB is missing (Cloud Deployment), generate fake data
        dates = pd.date_range(end=pd.Timestamp.now(), periods=200, freq='S')
        data = {
            'amount': np.random.uniform(10, 5000, size=200),
            'is_fraud': np.random.choice([0, 1], size=200, p=[0.95, 0.05]),
            'merchant_id': np.random.choice([f'M{i}' for i in range(10, 20)], size=200),
            'user_id': np.random.randint(1000, 1050, size=200),
            'latitude': np.random.uniform(40.70, 40.75, size=200),
            'longitude': np.random.uniform(-74.02, -73.95, size=200),
            'timestamp': dates
        }
        return pd.DataFrame(data)

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9206/9206332.png", width=80)
    st.markdown("### Control Node")
    refresh_rate = st.slider("Refresh Rate (sec)", 1, 10, 2)
    is_paused = st.checkbox("Pause Stream", False)
    
    st.markdown("---")
    
    # NEW FEATURE: Download Button
    df_download = load_data() # Load once for download
    csv = df_download.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Report",
        data=csv,
        file_name="fraud_report.csv",
        mime="text/csv",
    )
    
    st.markdown("---")
    st.markdown("Status: **Online** 🟢")

# --- 5. HEADER ---
c1, c2 = st.columns([6, 1])
with c1:
    st.markdown("<h1 style='margin:0; font-size: 3rem;'>Sentinel AI <span style='font-size:1.2rem; color:#a29bfe; vertical-align:middle'>// PRO</span></h1>", unsafe_allow_html=True)
    st.markdown("**Real-Time Financial Anomaly Detection System**")
with c2:
    st.markdown("""
        <div style="text-align:center; padding:10px; background:#dff9fb; border-radius:15px; color:#00b894; font-weight:bold;">
        SYSTEM<br>OPTIMAL
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

# --- 6. DASHBOARD LOOP ---
placeholder = st.empty()

while not is_paused:
    df = load_data()
    
    with placeholder.container():
        if not df.empty:
            # Metrics
            total_vol = df['amount'].sum()
            fraud_df = df[df['is_fraud'] == 1]
            fraud_count = len(fraud_df)
            saved_val = fraud_df['amount'].sum()
            
            # --- ROW 1: METRICS ---
            m1, m2, m3, m4 = st.columns(4)

            def metric_card(label, value, badge_text=None, is_alert=False):
                badge_class = "badge-alert" if is_alert else "badge-live"
                badge_html = f'<span class="badge {badge_class}">{badge_text}</span>' if badge_text else ""
                return f"""
                <div class="clay-card">
                    <div class="metric-label">{label}</div>
                    <div style="display:flex; align-items:center;">
                        <span class="metric-value">{value}</span>
                        {badge_html}
                    </div>
                </div>
                """

            with m1: st.markdown(metric_card("Total Volume", f"${total_vol/1000000:.1f}M", "Live"), unsafe_allow_html=True)
            with m2: st.markdown(metric_card("Fraud Blocked", f"{fraud_count}", "Action Req", True), unsafe_allow_html=True)
            with m3: st.markdown(metric_card("Value Secured", f"${saved_val/1000:,.0f}k", "+14%"), unsafe_allow_html=True)
            with m4: st.markdown(metric_card("Active Nodes", "4", "Stable"), unsafe_allow_html=True)

            # --- ROW 2: CHARTS ---
            c1, c2 = st.columns([1, 1])

            with c1:
                st.markdown('<div class="clay-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">⚠️ Top Risk Merchants</div>', unsafe_allow_html=True)
                
                merchant_fraud = df[df['is_fraud']==1].groupby('merchant_id').size().reset_index(name='count')
                merchant_fraud = merchant_fraud.sort_values('count', ascending=False).head(8)
                
                fig_bar = px.bar(
                    merchant_fraud, x='merchant_id', y='count',
                    color='count',
                    color_continuous_scale=['#ffb8b8', '#ff7675', '#d63031'],
                    text='count'
                )
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=250,
                    xaxis=dict(showgrid=False, type='category', title=''),
                    yaxis=dict(showgrid=False, visible=False),
                    showlegend=False,
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_bar, use_container_width=True, key=f"bar_{time.time()}")
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="clay-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">📈 Transaction Velocity</div>', unsafe_allow_html=True)
                
                df_time = df.iloc[::-1].tail(60) 
                fig_area = px.area(
                    df_time, y='amount',
                    color_discrete_sequence=['#74b9ff']
                )
                fig_area.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=250,
                    xaxis=dict(visible=False),
                    yaxis=dict(showgrid=True, gridcolor='#dfe6e9', title=''),
                    showlegend=False
                )
                st.plotly_chart(fig_area, use_container_width=True, key=f"area_{time.time()}")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- ROW 3: MAPS ---
            m_col1, m_col2 = st.columns([2, 1])

            with m_col1:
                st.markdown('<div class="clay-card" style="padding:0; overflow:hidden;">', unsafe_allow_html=True)
                st.pydeck_chart(pdk.Deck(
                    map_style='mapbox://styles/mapbox/light-v10',
                    initial_view_state=pdk.ViewState(
                        latitude=40.73, longitude=-73.95, zoom=10.5, pitch=50, bearing=20
                    ),
                    layers=[
                        pdk.Layer(
                            "HeatmapLayer",
                            data=df,
                            get_position='[longitude, latitude]',
                            opacity=0.8,
                            get_weight="is_fraud * 5",
                            radius_pixels=50,
                        ),
                        pdk.Layer(
                            'ScatterplotLayer',
                            data=df[df['is_fraud']==1],
                            get_position='[longitude, latitude]',
                            get_color=[255, 118, 117, 200],
                            get_radius=100,
                            pickable=True,
                        ),
                    ],
                ))
                st.markdown('</div>', unsafe_allow_html=True)

            with m_col2:
                st.markdown('<div class="clay-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">🧊 Vector Space</div>', unsafe_allow_html=True)
                fig_3d = px.scatter_3d(
                    df, x='user_id', y='merchant_id', z='amount',
                    color='is_fraud',
                    color_discrete_map={0: '#55efc4', 1: '#ff7675'},
                    size_max=10, opacity=0.8
                )
                fig_3d.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, b=0, t=0),
                    height=300,
                    scene=dict(bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
                    showlegend=False
                )
                st.plotly_chart(fig_3d, use_container_width=True, key=f"3d_{time.time()}")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- NEW FEATURE: LIVE ALERT LOG ---
            st.markdown('<div class="clay-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">📜 Recent Fraud Alerts</div>', unsafe_allow_html=True)
            
            # Show the last 5 fraud transactions in a clean table
            alerts = df[df['is_fraud'] == 1].head(5)[['timestamp', 'user_id', 'amount', 'merchant_id']]
            st.table(alerts)
            st.markdown('</div>', unsafe_allow_html=True)

    if is_paused:
        time.sleep(1)
    else:
        time.sleep(refresh_rate)