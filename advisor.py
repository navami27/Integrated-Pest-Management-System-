import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# 1. Load Environment Variables
load_dotenv()

def get_ai_advice(location, weather, pest_count, risk_level, yield_loss, trap_ratio=0.2, api_key=None):
    """
    Generates advice using Gemini 2.5 Pro with a specific "White Thrips & Marigold" persona.
    """
    final_key = api_key or os.getenv("GOOGLE_API_KEY")

    if not final_key:
        return "⚠️ Error: API Key missing. Please set GOOGLE_API_KEY in your .env file."

    try:
        # 2. Initialize Gemini 2.5 Pro (Reasoning Model)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=final_key,
            temperature=0.3, # Low temperature for factual, analytical advice
            convert_system_message_to_human=True
        )

        # 3. The "Neuro-Symbolic" System Prompt
        # This injects the biological rules and strategy context into the AI's brain.
        system_prompt = """
        You are a Senior Agricultural Entomologist and Precision Farming Advisor. 
        You are analyzing telemetry from a 'Digital Twin' simulation of a commercial Tomato Farm.

        DOMAIN KNOWLEDGE:
        - **Main Crop:** Tomato (Solanum lycopersicum).
        - **Trap Crop:** Marigold (Tagetes erecta) used in a 'Push-Pull' strategy.
        - **Target Pest:** White Thrips (*Thrips tabaci*).
        - **Pest Behavior:** You know that White Thrips aggregate at field edges, thrive in hot/dry conditions (25-32°C, <65% RH), and act as vectors for Tomato Spotted Wilt Virus (TSWV).

        YOUR GOAL:
        Analyze the simulation data and provide a critical evaluation of the current strategy in one paragraph, followed by 3-5 actionable recommendations to optimize pest management and yield outcomes.

        OUTPUT REQUIREMENTS:
        1. **Situation Analysis:** Assess if the current weather favors the pest or the crop.
        2. **Strategy Effectiveness:** Evaluate if the current Marigold Ratio ({ratio}) is effective. Is it successfully diverting pests, or is the outbreak overwhelming the trap crops?
        3. **Productivity vs. Protection:** Analyze the economic trade-off. Does the current ratio of Marigold justify the loss of tomato growing space? Should they plant more Marigolds for safety or fewer to maximize yield?
        4. **Intervention:** Specific Chemical (e.g., Spinosad) or Biological actions if risk is high.
        5. **Recommendations:** Provide 3 actionable recommendations to optimize pest management and yield outcomes in 3-5 bullet points.
        """

        human_prompt = """
        **FARM TELEMETRY:**
        - **Location:** {location}
        - **Weather:** {temp}°C | Humidity: {humidity}%
        - **Current Strategy:** Marigold Ratio = {ratio} (Approx 1 Marigold per {inv_ratio} Tomatoes)
        - **Pest Count:** {pest_count} Agents (approx {real_pests} thrips)
        - **Status:** {risk_level}
        - **Est. Yield Loss:** {yield_loss}%

        Provide your strategic assessment now.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])

        # 4. Create Chain
        chain = prompt | llm
        
        # Calculate approximate real ratio for the prompt context
        inv_ratio = round(1/trap_ratio) if trap_ratio > 0 else "N/A"
        real_pests = pest_count * 500 # The scaling factor logic

        response = chain.invoke({
            "location": location,
            "temp": weather['temp'],
            "humidity": weather['humidity'],
            "ratio": trap_ratio,
            "inv_ratio": inv_ratio,
            "pest_count": pest_count,
            "real_pests": real_pests,
            "risk_level": risk_level,
            "yield_loss": yield_loss
        })

        return response.content

    except Exception as e:
        return f"Error connecting to AI Advisor: {e}"