# 🍅 AgriTwin: Neuro-Symbolic Pest Management Digital Twin

**AgriTwin** is an advanced decision support system designed for large commercial tomato farms and Farmer Producer Organizations (FPOs). It integrates **Agent-Based Modeling (ABM)** with **Generative AI** to predict, visualize, and manage pest outbreaks (*Thrips tabaci*) based on hyperlocal weather conditions.

Unlike traditional reactive tools, this project uses a **Neuro-Symbolic Architecture**: combining the mathematical rigor of biological simulation (Symbolic) with the reasoning capabilities of Large Language Models (Neural).

---

## 🌟 Key Features

### 1. 🚜 Agent-Based Biological Simulation
* **Predictive Modeling:** Simulates the lifecycle of *Thrips* (pests) based on temperature and humidity thresholds.
* **Behavioral Rules:** Implements real-world biological behaviors:
    * **Edge Effect:** Pests aggregate at farm boundaries.
    * **Trap Cropping:** Pests are attracted to Marigold plants (Push-Pull strategy).
    * **Viral Vector Risk:** Simulates *Tomato Spotted Wilt Virus* (TSWV) transmission risk.

### 2. 🌍 Hyperlocal Weather Integration
* **Geocoding:** Uses **OpenStreetMap (Nominatim)** to locate specific villages or farms.
* **Live Forecasting:** Fetches real-time weather data via **Open-Meteo API**.
* **Stochastic Extension:** Mathematically extrapolates short-term forecasts to simulate 100-day cropping seasons.

### 3. 🤖 AI Agronomist (Neuro-Symbolic Layer)
* **Powered by Google Gemini 2.5 Pro:** The system sends live simulation telemetry (Yield Loss %, Pest Count) to an LLM.
* **Actionable Advisory:** Generates context-aware IPM (Integrated Pest Management) reports, suggesting specific chemical or organic interventions based on the current risk level.

### 4. 📊 Comparative Analytics
* **Side-by-Side View:** Visualizes the "Last Safe State" vs. "Current Outbreak" to highlight the spread pattern.
* **Economic Impact:** Calculates estimated yield loss percentages based on pest density and viral shock models.

---

## 🛠️ Technology Stack

* **Language:** Python 3.x
* **Simulation Engine:** [Mesa](https://mesa.readthedocs.io/) (Agent-Based Modeling)
* **Frontend/Dashboard:** [Streamlit](https://streamlit.io/)
* **AI/Orchestration:** [LangChain](https://www.langchain.com/) + Google Gemini API
* **Data Sources:** Open-Meteo (Weather), OpenStreetMap (Location)
* **Visualization:** Matplotlib, Pandas

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/pest-management-digital-twin.git](https://github.com/YOUR_USERNAME/pest-management-digital-twin.git)
cd pest-management-digital-twin
