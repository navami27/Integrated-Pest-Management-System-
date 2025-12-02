import mesa
import random

class CropAgent(mesa.Agent):
    """
    Base class for crops. 
    """
    def __init__(self, model, crop_type):
        # FIX: Do not pass unique_id to super().__init__
        super().__init__(model)
        self.crop_type = crop_type
        self.health = 100 

class TomatoAgent(CropAgent):
    def __init__(self, model):
        super().__init__(model, "Tomato")

class MarigoldAgent(CropAgent):
    def __init__(self, model):
        super().__init__(model, "Marigold")

class ThripAgent(mesa.Agent):
    """
    The Pest. Implements biological rules from CSV.
    """
    def __init__(self, model):
        # FIX: Do not pass unique_id to super().__init__
        super().__init__(model)
        self.type = "Thrip" # Essential for the UI to recognize it
        self.age = 0

    def move(self):
        """
        Rule: Thrips attracted to marigold trap crops.
        """
        # Get neighbors
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius=1
        )
        
        # Check for Marigold in neighbors
        marigold_cells = [a.pos for a in neighbors if isinstance(a, MarigoldAgent)]

        if marigold_cells and random.random() < 0.8:
            # 80% chance to move to Trap Crop (Attraction Rule)
            new_pos = random.choice(marigold_cells)
        else:
            # Random movement
            possible_steps = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
            new_pos = random.choice(possible_steps)

        self.model.grid.move_agent(self, new_pos)

    def biological_lifecycle(self):
        """
        Handles Reproduction and Mortality based on Weather.
        """
        temp = self.model.current_weather['temp']
        rh = self.model.current_weather['humidity']
        rain = self.model.current_weather['rain']

        # --- CSV Rule: Mortality increased with RH > 60% or rain ---
        death_prob = 0.05
        if rh > 60 or rain:
            death_prob = 0.45  # High mortality

        if random.random() < death_prob:
            self.remove() # FIX: Use self.remove() in Mesa 3.0
            return

        # --- CSV Rule: Reproduction maximized at 25–30°C, RH < 60% ---
        repro_prob = 0.02
        if 25 <= temp <= 30 and rh < 60:
            repro_prob = 0.15 # Optimal
        
        # --- CSV Rule: Outbreak triggered by sustained optimal weather ---
        if self.model.is_outbreak_mode:
            repro_prob += 0.20 # Massive spike during outbreak

        if random.random() < repro_prob:
            # FIX: No unique_id passed here
            offspring = ThripAgent(self.model)
            self.model.grid.place_agent(offspring, self.pos)
            # Note: In Mesa 3.0, agents are auto-added to scheduler/agent list usually, 
            # but if using explicit scheduler:
            if hasattr(self.model, 'schedule'):
                self.model.schedule.add(offspring)

    def feed(self):
        """
        Rule: Feeding damage and yield loss on tomato.
        
        SCIENTIFIC BASIS:
        1. YIELD LOSS: Recent studies (IJISRT, 2023) show thrips infestation causes 
           40-80% yield loss in tomatoes due to flower abscission and fruit scarring.
        2. VIRUS VECTOR: Thrips transmit TSWV, causing systemic necrosis and 
           total marketable yield loss (UF/IFAS, 2024).
           
        MODELING DECISION:
        We simulate this 'Viral Shock' + 'Colony Feeding' as a high damage rate (25%).
        """
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for agent in cell_contents:
            if isinstance(agent, TomatoAgent):
                agent.health -= 25 
                if agent.health < 0: agent.health = 0

    def step(self):
        self.move()
        self.feed()
        self.biological_lifecycle()