import streamlit as st
import matplotlib.pyplot as plt
import requests
import pandas as pd
from model import TomatoModel
from agents import TomatoAgent, MarigoldAgent, ThripAgent

# ==========================================
# 1. HYPERLOCAL GEOCODING (NOMINATIM)
# ==========================================
def get_coordinates(location_query):
    """
    Uses OpenStreetMap (Nominatim) to find specific villages/streets.
    """
    try:
        # User-Agent header is required by OpenStreetMap policy
        headers = {'User-Agent': 'PestSimStudentProject/1.0'}
        url = f"https://nominatim.openstreetmap.org/search?q={location_query}&format=json&limit=1"
        response = requests.get(url, headers=headers).json()
        
        if response:
            data = response[0]
            lat = float(data['lat'])
            lon = float(data['lon'])
            display_name = data['display_name']
            return lat, lon, display_name
        else:
            return None, None, None
    except Exception as e:
        print(f"Geocoding Error: {e}")
        return None, None, None

# ==========================================
# 2. PAGE CONFIG & SIDEBAR
# ==========================================
st.set_page_config(page_title="AgriTwin: Pest Manager", page_icon="🍅", layout="wide")
st.title("Interactive Digital Twin for Pest Management 🌱")

st.sidebar.title("🍅 Control Panel")

# --- HYPERLOCAL SEARCH ---
st.sidebar.markdown("### 📍 Location")
location_input = st.sidebar.text_input(
    "Search Area / Village", 
    value="GKVK, Bengaluru", 
    help="Enter a specific village, campus, or landmark."
)

if 'coords' not in st.session_state: 
    st.session_state.coords = (12.97, 77.59) # Default
    st.session_state.loc_name = "Bengaluru (Default)"

if st.sidebar.button("🔎 Find Location"):
    lat, lon, full_name = get_coordinates(location_input)
    if lat: 
        st.session_state.coords = (lat, lon)
        st.session_state.loc_name = full_name
        st.sidebar.success("Location Found!")
    else:
        st.sidebar.error("Location not found. Try adding the district/state.")

# Show selected details
lat, lon = st.session_state.coords
st.sidebar.caption(f"**Selected:** {st.session_state.loc_name[:40]}...")
st.sidebar.caption(f"**Lat/Lon:** {lat:.4f}, {lon:.4f}")

# Map Verification Link
map_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=14/{lat}/{lon}"
st.sidebar.markdown(f"[🗺️ Verify on Map]({map_url})", unsafe_allow_html=True)

st.sidebar.divider()

# --- FARM SETTINGS ---
st.sidebar.markdown("### 🚜 Simulation Settings")
farm_size = st.sidebar.slider("Size (Acres)", 10, 100, 20)
# ... inside the Sidebar ...


# --- NEW: DYNAMIC LEGEND ---
# Calculate roughly how many plants are in one 'Green Square' based on size
# Assumption: ~4000 plants per acre
total_real_plants = farm_size * 4000 
# Your grid cap logic (simplified estimation for display)
grid_side = min(40, int((farm_size * 3)**0.5) + 10)
total_cells = grid_side * grid_side
plants_per_cell = int(total_real_plants / total_cells)

st.sidebar.info(f"""
**Scale Indicator:**
At {farm_size} acres:
🟩 1 Square ≈ **{plants_per_cell}** Plants
❌ 1 Pest Agent ≈ **{plants_per_cell * 10}** Thrips
""")
# ---------------------------
trap_ratio = st.sidebar.slider("Marigold Ratio", 0.0, 0.5, 0.2)
layout_type = st.sidebar.selectbox("Layout", ["intercropping", "perimeter"])

st.sidebar.divider()

# --- SCENARIO CONTROL ---
st.sidebar.markdown("### 🧪 Scenario")
scenario_mode = st.sidebar.radio(
    "Data Source:", 
    ["Real Data (API)", "Force Outbreak"],
    help="Use 'Force Outbreak' to simulate ideal pest weather."
)

if 'model' not in st.session_state: st.session_state.model = None

# --- ACTION BUTTONS ---
c1, c2 = st.sidebar.columns(2)
if c1.button("🌱 Initialize", type="primary"):
    st.session_state.model = TomatoModel(
        farm_size_acres=farm_size, 
        trap_crop_ratio=trap_ratio, 
        layout=layout_type, 
        lat=lat, lon=lon
    )

if c2.button("▶️ Next Day"):
    if st.session_state.model: st.session_state.model.step()

# ==========================================
# 3. VISUALIZATION HELPERS
# ==========================================
def render_static_grid(width, height, tomatoes, marigolds, pests, title):
    # Compact Figure
    fig, ax = plt.subplots(figsize=(5, 5)) 
    ax.set_xlim(-1, width)
    ax.set_ylim(-1, height)
    ax.axis('off')
    # Background
    ax.fill([0, width, width, 0], [0, 0, height, height], '#f0f2f6')
    
    if tomatoes:
        tx, ty = zip(*tomatoes)
        ax.scatter(tx, ty, s=70, c="#2ecc71", marker="s", label="Tomato")
    if marigolds:
        mx, my = zip(*marigolds)
        ax.scatter(mx, my, s=70, c="#f1c40f", marker="H", label="Marigold")
    if pests:
        px, py = zip(*pests)
        ax.scatter(px, py, s=60, c="#e74c3c", marker="x", linewidths=2, label="Pest")

    ax.set_title(title, fontsize=10, fontweight='bold', color='#333')
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
# 4. DASHBOARD MAIN VIEW
# ==========================================
if st.session_state.model is None:
    st.info("👈 Enter a Location and click 'Initialize' to start the Digital Twin.")
else:
    model = st.session_state.model
    
    # --- Top Stats ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Day", model.current_step_tracker)
    m2.metric("Temp (Max)", f"{model.current_weather['temp']}°C")
    m3.metric("Humidity (Min)", f"{model.current_weather['humidity']}%")
    
    status_label = "🚨 OUTBREAK" if model.is_outbreak_mode else "✅ SAFE"
    m4.metric("Risk Level", status_label, delta_color="inverse")

    # --- Split View (Grid vs Stats) ---
    col_viz, col_data = st.columns([1.5, 1])
    
    with col_viz:
        # If outbreak, show side-by-side comparison
        if model.is_outbreak_mode and model.last_safe_state:
            st.warning("⚠️ Comparison Mode Active")
            sub1, sub2 = st.columns(2)
            
            with sub1:
                safe = model.last_safe_state
                fig_safe = render_static_grid(
                    model.width, model.height, 
                    safe['tomatoes'], safe['marigolds'], safe['pests'], 
                    "Last Safe State"
                )
                st.pyplot(fig_safe)
            
            with sub2:
                t, m, p = get_agent_positions(model)
                fig_curr = render_static_grid(
                    model.width, model.height, t, m, p, 
                    "Current Outbreak"
                )
                st.pyplot(fig_curr)
        else:
            # Normal View
            st.subheader("Farm Digital Twin")
            t, m, p = get_agent_positions(model)
            fig = render_static_grid(model.width, model.height, t, m, p, "Live Simulation")
            st.pyplot(fig)

    with col_data:
        st.subheader("📊 Analytics")
        
        # Pest Growth Chart
        chart_data = model.datacollector.get_model_vars_dataframe()
        st.line_chart(chart_data["Thrips"], height=150)
        
        # Outbreak Report Panel
        if model.is_outbreak_mode:
            with st.container(border=True):
                st.markdown("### 📄 Outbreak Report")
                st.error(f"**Cause:** {model.outbreak_cause}")
                st.write(f"**Pest Population:** {model.schedule.get_agent_count()}")
                
                loss_color = "red" if model.yield_loss_pct > 10 else "orange"
                st.markdown(f"**Yield Loss:** :{loss_color}[{model.yield_loss_pct:.1f}%]")
                
                #st.info("Recommendation: Apply localized pesticide in red zones.")
        else:
            st.success("Crop status is currently optimal.")
            with st.expander("See Weather Log"):
                st.dataframe(pd.DataFrame(model.weather_history).head(10), height=150)