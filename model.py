import mesa
import requests
import random
import numpy as np
from agents import TomatoAgent, MarigoldAgent, ThripAgent

class TomatoModel(mesa.Model):
    def __init__(self, farm_size_acres=50, trap_crop_ratio=0.2, layout="intercropping", lat=12.97, lon=77.59, scenario="Real Data"):
        super().__init__()
        
        # --- FIXED GRID ARCHITECTURE ---
        # We lock the resolution to 40x40 for consistent visualization and performance.
        # This means 1 Cell represents a variable number of plants depending on farm size.
        # (See app.py sidebar for the real-time math display).
        self.width = 40
        self.height = 40
        
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)
        self.schedule = mesa.time.RandomActivation(self)
        
        # Weather & Stats
        self.weather_history = []
        self.current_step_tracker = 0
        self.is_outbreak_mode = False
        self.optimal_weather_streak = 0
        self.outbreak_cause = "N/A"
        self.yield_loss_pct = 0.0
        
        # Snapshot for Comparison
        self.last_safe_state = None 
        
        # Weather Setup
        if scenario == "Force Outbreak":
            # Synthetic "Ideal Pest Weather" (Hot & Dry)
            self.weather_history = [{'temp': 29, 'humidity': 55, 'rain': False} for _ in range(50)]
        else:
            self.fetch_weather_data(lat, lon)
            if not self.weather_history:
                 self.weather_history = [{'temp': 25, 'humidity': 50, 'rain': False}]
            self.extend_weather_data(days_needed=100)

        self.current_weather = self.weather_history[0]

        # Setup Farm
        self.generate_layout(layout, trap_crop_ratio)
        self.initialize_pests()
        self.capture_safe_state()

        self.datacollector = mesa.DataCollector(
            {"Thrips": lambda m: m.schedule.get_agent_count()}
        )

    def capture_safe_state(self):
        """Snapshots the positions of agents for comparison later."""
        snapshot = {'tomatoes': [], 'marigolds': [], 'pests': []}
        for content, (x, y) in self.grid.coord_iter():
            for agent in content:
                if isinstance(agent, TomatoAgent):
                    snapshot['tomatoes'].append((x, y))
                elif isinstance(agent, MarigoldAgent):
                    snapshot['marigolds'].append((x, y))
                elif isinstance(agent, ThripAgent):
                    snapshot['pests'].append((x, y))
        self.last_safe_state = snapshot

    def calculate_yield_loss(self):
        """
        Calculates total yield loss based on Tomato Health.
        Iterates over physical grid to ensure stationary plants are counted.
        """
        total_potential = 0
        current_health = 0
        for content, (x, y) in self.grid.coord_iter():
            for agent in content:
                if isinstance(agent, TomatoAgent):
                    total_potential += 100
                    current_health += agent.health
        
        if total_potential > 0:
            loss = total_potential - current_health
            self.yield_loss_pct = (loss / total_potential) * 100
        else:
            self.yield_loss_pct = 0.0

    def fetch_weather_data(self, lat, lon):
        try:
            # Fetching Relative Humidity Min (Afternoon) as it affects thrips most
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,relative_humidity_2m_min,rain_sum&timezone=auto"
            response = requests.get(url, timeout=5).json()
            if 'daily' in response:
                daily = response['daily']
                for i in range(len(daily['time'])):
                    self.weather_history.append({
                        'temp': daily['temperature_2m_max'][i],
                        'humidity': daily['relative_humidity_2m_min'][i],
                        'rain': daily['rain_sum'][i] > 1.0
                    })
        except Exception as e:
            print(f"API Error: {e}")

    def extend_weather_data(self, days_needed):
        """Generates realistic random weather for days beyond the API forecast."""
        current_len = len(self.weather_history)
        if current_len == 0: 
            last_temp, last_hum = 28, 50
        else:
            last_temp = self.weather_history[-1]['temp']
            last_hum = self.weather_history[-1]['humidity']

        for _ in range(days_needed - current_len):
            last_temp += random.uniform(-1.5, 1.5)
            last_hum += random.uniform(-5, 5)
            # Clamp to realistic semi-arid values
            last_temp = max(15, min(38, last_temp))
            last_hum = max(20, min(95, last_hum))
            rain = random.random() < 0.1
            self.weather_history.append({'temp': round(last_temp, 1), 'humidity': int(last_hum), 'rain': rain})

    def generate_layout(self, layout, ratio):
        for x in range(self.width):
            for y in range(self.height):
                is_trap = False
                if layout == "intercropping":
                    # Simple modulo logic for rows
                    freq = int(1/ratio) if ratio > 0 else 100
                    if y % freq == 0: is_trap = True
                elif layout == "perimeter":
                    # Outer boundary
                    if x < 2 or x >= self.width-2 or y < 2 or y >= self.height-2: is_trap = True
                
                a = MarigoldAgent(self) if is_trap else TomatoAgent(self)
                self.grid.place_agent(a, (x, y))

    def initialize_pests(self):
        center_x, center_y = self.width // 2, self.height // 2
        max_dist = np.sqrt(center_x**2 + center_y**2)
        for x in range(self.width):
            for y in range(self.height):
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                # Edge Effect: Probability increases as we move away from center
                spawn_prob = 0.08 * (dist / max_dist)
                if random.random() < spawn_prob:
                    pest = ThripAgent(self)
                    self.grid.place_agent(pest, (x, y))
                    self.schedule.add(pest)

    def step(self):
        day_idx = self.current_step_tracker % len(self.weather_history)
        self.current_weather = self.weather_history[day_idx]
        
        temp = self.current_weather['temp']
        rh = self.current_weather['humidity']
        
        # Biological Rule: Outbreak if 25-32C and Dry (<65%)
        if 25 <= temp <= 32 and rh < 65:
            self.optimal_weather_streak += 1
            self.outbreak_cause = f"Opt. Temp ({temp}°C) & Dry Air ({rh}%)"
        else:
            self.optimal_weather_streak = 0
            if not self.is_outbreak_mode:
                self.capture_safe_state()
            
        self.is_outbreak_mode = (self.optimal_weather_streak >= 2)
        self.calculate_yield_loss()
        self.datacollector.collect(self)
        self.schedule.step()
        self.current_step_tracker += 1