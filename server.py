import streamlit as st
import matplotlib.pyplot as plt
import requests
import pandas as pd
import os
import numpy as np
from dotenv import load_dotenv

# Import local modules
from model import TomatoModel
from agents import TomatoAgent, MarigoldAgent, ThripAgent
from advisor import get_ai_advice

# ==========================================
# 0. CONFIG & SECRETS
# ==========================================
st.set_page_config(page_title="AgriTwin: Pest Manager", page_icon="🍅", layout="wide")

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================
@st.cache_data(show_spinner=False)
def get_coordinates(location_query):
    try:
        headers = {'User-Agent': 'PestSimStudentProject/1.0'}
        url = f"https://nominatim.openstreetmap.org/search?q={location_query}&format=json&limit=1"
        response = requests.get(url, headers=headers).json()
        if response:
            data = response[0]
            return float(data['lat']), float(data['lon']), data['display_name']
        return None, None, None
    except Exception as e:
        print(f"Geocoding Error: {e}")
        return None, None, None

def render_static_grid(width, height, tomatoes, marigolds, pests, title):
    # Close previous plots to prevent lag
    plt.close('all')
    
    # 1. Setup Compact Figure
    fig, ax = plt.subplots(figsize=(3.5, 3.5)) 
    ax.set_xlim(-1, width)
    ax.set_ylim(-1, height)
    ax.axis('off')
    
    # 2. Dynamic Marker Sizing
    # Prevents "Green Block" effect by shrinking dots if grid is dense (40x40)
    max_dim = max(width, height)
    # Calibrated Size Formula
    dynamic_s = (180 / max_dim) ** 2  
    
    # 3. Background
    ax.fill([0, width, width, 0], [0, 0, height, height], '#f8f9fa')
    
    # 4. Draw Crops (With White Edges for separation)
    if tomatoes:
        tx, ty = zip(*tomatoes)
        # Green Squares ('s') with white border
        ax.scatter(tx, ty, s=dynamic_s, c="#4CAF50", marker="s", 
                   label="Tomato", edgecolors='white', linewidths=0.5)
                   
    if marigolds:
        mx, my = zip(*marigolds)
        # Yellow Hexagons ('h') with white border
        ax.scatter(mx, my, s=dynamic_s, c="#FFD700", marker="h", 
                   label="Marigold", edgecolors='white', linewidths=0.5)
    
    # 5. Draw Pests (On Top)
    if pests:
        px, py = zip(*pests)
        px = np.array(px, dtype=float)
        py = np.array(py, dtype=float)
        
        # Jitter: Random offset so pests don't overlap perfectly
        jitter_strength = 0.3 
        noise_x = np.random.uniform(-jitter_strength, jitter_strength, size=len(px))
        noise_y = np.random.uniform(-jitter_strength, jitter_strength, size=len(py))
        
        # Red Crosses ('x')
        ax.scatter(px + noise_x, py + noise_y, s=dynamic_s * 0.7, c="#D32F2F", 
                   marker="x", linewidths=1.2, label="Pest")

    ax.set_title(title, fontsize=9, fontweight='bold', color='#333')
    return fig

def get_agent_positions(model):
    t, m, p = [], [], []
    for content, (x, y) in model.grid.coord_iter():
        for agent in content:
            if isinstance(agent, TomatoAgent): t.append((x, y))
            elif isinstance(agent, MarigoldAgent): m.append((x, y))
            elif isinstance(agent, ThripAgent): p.append((x, y))
    return t, m, p

# ==========================================
# 2. SIDEBAR
# ==========================================
st.sidebar.title("🍅 Control Panel")

st.sidebar.markdown("### 📍 Location")
location_input = st.sidebar.text_input("Search Area / Village", value="GKVK, Bengaluru")

if 'coords' not in st.session_state: 
    st.session_state.coords = (12.97, 77.59) 
    st.session_state.loc_name = "Bengaluru (Default)"

if st.sidebar.button("🔎 Find Location"):
    lat, lon, full_name = get_coordinates(location_input)
    if lat: 
        st.session_state.coords = (lat, lon)
        st.session_state.loc_name = full_name
        st.sidebar.success("Location Found!")
    else:
        st.sidebar.error("Not found.")

lat, lon = st.session_state.coords
st.sidebar.caption(f"**Selected:** {st.session_state.loc_name[:35]}...")

st.sidebar.divider()
st.sidebar.markdown("### 🚜 Simulation Settings")
farm_size = st.sidebar.slider("Size (Acres)", 10, 100, 20)

# Scale Indicator Math
total_real_plants = farm_size * 4000 
# Logic must match model.py side_length formula
grid_side = min(100, int(9 * (farm_size ** 0.5)))
total_cells = grid_side * grid_side
plants_per_cell = int(total_real_plants / total_cells)

st.sidebar.info(f"""
**Scale Indicator:**
At {farm_size} acres:
🟩 1 Cell ≈ **{plants_per_cell}** Plants
❌ 1 Agent ≈ **{plants_per_cell * 10}** Pests
""")

trap_ratio = st.sidebar.slider("Marigold Ratio", 0.0, 0.5, 0.2)
layout_type = st.sidebar.selectbox("Layout", ["intercropping", "perimeter"])

st.sidebar.divider()
st.sidebar.markdown("### 🧪 Scenario")
scenario_mode = st.sidebar.radio("Data Source:", ["Real Data (API)", "Force Outbreak"])

if 'model' not in st.session_state: st.session_state.model = None

# Init Button
c1, c2 = st.sidebar.columns(2)
if c1.button("🌱 Initialize", type="primary"):
    st.session_state.model = TomatoModel(
        farm_size_acres=farm_size, 
        trap_crop_ratio=trap_ratio, 
        layout=layout_type, 
        lat=lat, lon=lon,
        scenario=scenario_mode
    )

if c2.button("▶️ Next Day"):
    if st.session_state.model: st.session_state.model.step()

# ==========================================
# 3. DASHBOARD
# ==========================================
st.title("Interactive Digital Twin for Pest Management 🌱")

if st.session_state.model is None:
    st.info("👈 Enter a Location and click 'Initialize' to start.")
else:
    model = st.session_state.model
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Day", model.current_step_tracker)
    m2.metric("Temp (Max)", f"{model.current_weather['temp']}°C")
    m3.metric("Humidity (Min)", f"{model.current_weather['humidity']}%")
    status_label = "🚨 OUTBREAK" if model.is_outbreak_mode else "✅ SAFE"
    m4.metric("Risk Level", status_label, delta_color="inverse")

    st.divider()

    # Split: Visuals (Left) | Analytics (Right)
    col_viz, col_stats = st.columns([1.3, 1])
    
    with col_viz:
        st.subheader("🗺️ Farm View")
        
        if model.is_outbreak_mode and model.last_safe_state:
            st.caption("Comparison Mode: Safe State (Left) vs Current Outbreak (Right)")
            sub1, sub2 = st.columns(2)
            with sub1:
                safe = model.last_safe_state
                fig_safe = render_static_grid(
                    model.width, model.height, 
                    safe['tomatoes'], safe['marigolds'], safe['pests'], "Last Safe State"
                )
                st.pyplot(fig_safe, use_container_width=False)
            with sub2:
                t, m, p = get_agent_positions(model)
                fig_curr = render_static_grid(
                    model.width, model.height, t, m, p, "Current Outbreak"
                )
                st.pyplot(fig_curr, use_container_width=False)
        else:
            t, m, p = get_agent_positions(model)
            fig = render_static_grid(model.width, model.height, t, m, p, "Live Simulation")
            # Centering
            c1, c2, c3 = st.columns([0.1, 2, 0.1])
            with c2:
                st.pyplot(fig, use_container_width=False)

    with col_stats:
        st.subheader("📊 Live Analytics")
        stat1, stat2 = st.columns(2)
        stat1.metric("Pest Count", model.schedule.get_agent_count())
        
        loss_val = model.yield_loss_pct
        loss_color = "normal"
        if loss_val > 5: loss_color = "off"
        stat2.metric("Yield Loss", f"{loss_val:.1f}%", delta_color=loss_color)
        
        if model.is_outbreak_mode:
            st.error(f"**Cause:** {model.outbreak_cause}")

        st.markdown("**Population Volume**")
        chart_data = model.datacollector.get_model_vars_dataframe()
        st.area_chart(chart_data["Thrips"], height=200, color="#ff4b4b") 

        st.divider()
        # Inside app.py, under the 'with col_stats:' block:

        st.markdown("**Damage Correlation**")
        df = model.datacollector.get_model_vars_dataframe()

        if len(df) > 1:
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot(df["Thrips"], color='red', label='Pest Population')
            ax.set_xlabel('Days')
            ax.set_ylabel('Count')
            ax.set_title('Pest Growth Curve')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig, use_container_width=True)

        st.subheader("🧠 AI Agronomist")
        if st.button("Generate Strategy Report ✨", type="primary"):
            if not api_key:
                st.error("❌ Google API Key not found. Check your .env file.")
            else:
                with st.spinner("Consulting Gemini 2.5 Pro..."):
                    risk_status = "CRITICAL OUTBREAK" if model.is_outbreak_mode else "Safe/Monitor"
                    advice = get_ai_advice(
                        location=st.session_state.get('loc_name', 'Unknown'),
                        weather=model.current_weather,
                        pest_count=model.schedule.get_agent_count(),
                        risk_level=risk_status,
                        yield_loss=model.yield_loss_pct,
                        trap_ratio=trap_ratio,
                        api_key=api_key 
                    )
                    with st.expander("View Report", expanded=True):
                        st.markdown(advice)