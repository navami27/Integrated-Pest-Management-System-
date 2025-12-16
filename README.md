---

🍅 AgriTwin: Neuro-Symbolic Pest Management Digital Twin**AgriTwin** is an advanced decision support system designed for large commercial tomato farms and Farmer Producer Organizations (FPOs). It integrates **Agent-Based Modeling (ABM)** with **Generative AI** to predict, visualize, and manage pest outbreaks (*Thrips tabaci*) based on hyperlocal weather conditions.

Unlike traditional reactive tools, this project uses a **Neuro-Symbolic Architecture**: combining the mathematical rigor of biological simulation (Symbolic) with the reasoning capabilities of Large Language Models (Neural).

---

##🌟 Key Features###1. 🚜 Agent-Based Biological Simulation* **Predictive Modeling:** Simulates the lifecycle of *Thrips* (pests) based on temperature and humidity thresholds.
* **Behavioral Rules:** Implements real-world biological behaviors:
* **Edge Effect:** Pests aggregate at farm boundaries.
* **Trap Cropping:** Pests are attracted to Marigold plants (Push-Pull strategy).
* **Viral Vector Risk:** Simulates *Tomato Spotted Wilt Virus* (TSWV) transmission risk.



###2. 🌍 Hyperlocal Weather Integration* **Geocoding:** Uses **OpenStreetMap (Nominatim)** to locate specific villages or farms.
* **Live Forecasting:** Fetches real-time weather data via **Open-Meteo API**.
* **Stochastic Extension:** Mathematically extrapolates short-term forecasts to simulate 100-day cropping seasons.

###3. 🤖 AI Agronomist (Neuro-Symbolic Layer)* **Powered by Google Gemini 2.5 Pro:** The system sends live simulation telemetry (Yield Loss %, Pest Count) to an LLM.
* **Actionable Advisory:** Generates context-aware IPM (Integrated Pest Management) reports, suggesting specific chemical or organic interventions based on the current risk level.

###4. 📊 Comparative Analytics* **Side-by-Side View:** Visualizes the "Last Safe State" vs. "Current Outbreak" to highlight the spread pattern.
* **Economic Impact:** Calculates estimated yield loss percentages based on pest density and viral shock models.

---

##🛠️ Technology Stack* **Language:** Python 3.x
* **Simulation Engine:** [Mesa](https://mesa.readthedocs.io/) (Agent-Based Modeling)
* **Frontend/Dashboard:** [Streamlit](https://streamlit.io/)
* **AI/Orchestration:** [LangChain](https://www.langchain.com/) + Google Gemini API
* **Data Sources:** Open-Meteo (Weather), OpenStreetMap (Location)
* **Visualization:** Matplotlib, Pandas

---

##⚙️ Installation & Setup###1. Clone the Repository```bash
git clone https://github.com/YOUR_USERNAME/pest-management-digital-twin.git
cd pest-management-digital-twin

```

###2. Create a Virtual Environment (Optional but Recommended)```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

```

###3. Install Dependencies```bash
pip install -r requirements.txt

```

*(Note: If `requirements.txt` is missing, install manually: `pip install mesa streamlit langchain-google-genai python-dotenv matplotlib requests pandas`)*

###4. Configure API Keys1. Get a **Free API Key** from [Google AI Studio](https://aistudio.google.com/).
2. Create a file named `.env` in the root directory.
3. Add your key:
```env
GOOGLE_API_KEY=your_actual_api_key_here

```



---

##🚀 Usage1. **Run the Dashboard:**
```bash
streamlit run app.py

```


2. **Simulation Workflow:**
* **Select Location:** Enter a village name (e.g., *"Hessarghatta, Bangalore"*) in the sidebar.
* **Choose Scenario:** Select **"Real Data"** to test live conditions or **"Force Outbreak"** to demonstrate the alarm system.
* **Initialize:** Click "🌱 Initialize".
* **Simulate:** Click "▶️ Next Day" repeatedly to watch the outbreak spread.
* **Get Advice:** Switch to the **"🤖 AI Agronomist"** tab and generate a report.



---

##🧪 Scientific Validation & MethodologyTo ensure the simulation is realistic, this project uses **"Super-Individual Modeling"** (Scheffer et al., 1995) to handle computational constraints.

| Parameter | Value | Scientific Basis |
| --- | --- | --- |
| **Simulation Unit** | 20 Acres | Represents a standard Commercial FPO Cluster in India. |
| **Grid Resolution** | 40x40 Cells | **Abstract Scaling:** 1 Cell \approx 50 Plants (25m^2). |
| **Agent Ratio** | 1:500 | **Super-Individual:** 1 Agent represents a high-density cluster of ~500 pests. |
| **Damage Logic** | 25% / Step | Simulates systemic **Viral Shock (TSWV)** rather than just leaf feeding (Ref: *IJISRT, 2023*). |
| **Outbreak Trigger** | 25-32°C, <65% RH | Optimal breeding conditions for *Thrips tabaci* (Ref: *Kagezi et al., 2001*). |

---

##📂 Project Structure```text
pest_simulation/
│
├── app.py              # Main Streamlit Dashboard (UI Layer)
├── model.py            # Mesa Simulation Logic (Symbolic Layer)
├── agents.py           # Biological Rules for Pests/Crops
├── advisor.py          # LangChain AI Advisory System (Neural Layer)
├── .env                # API Keys (Not uploaded to GitHub)
├── .gitignore          # Security rules
└── requirements.txt    # Project dependencies

```

---

##🔮 Future Scope* **MCP Integration:** Implementing the Model Context Protocol to allow autonomous AI agents (like Claude) to manage the farm in the background.
* **Multimodal Input:** Allowing farmers to upload photos of leaves for computer-vision-based diagnosis using Gemini Vision.
* **IoT Connection:** Connecting the simulation to physical soil moisture sensors for real-time telemetry.



**Developed by:** [Your Name]
**Contact:** [Your Email]
