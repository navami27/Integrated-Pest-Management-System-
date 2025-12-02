import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# 1. Load the .env file immediately
load_dotenv()

def get_ai_advice(location, weather, pest_count, risk_level, yield_loss, api_key=None):
    """
    Generates advice using Gemini 2.5 Pro. 
    Prioritizes the passed 'api_key', otherwise looks for 'GOOGLE_API_KEY' in environment.
    """
    # 2. Smart Key Logic
    final_key = api_key or os.getenv("API_KEY")

    if not final_key:
        return "⚠️ Error: API Key missing. Please set GOOGLE_API_KEY in your .env file."

    try:
        # 3. Initialize Gemini 2.5 Pro
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", # Or "gemini-1.5-pro"
            google_api_key=final_key,
            temperature=0.4,
            convert_system_message_to_human=True
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Agricultural Entomologist and Digital Twin Advisor."),
            ("human", """
            Analyze this Farm Digital Twin status:
            
            - **Location:** {location}
            - **Current Weather:** {temp}°C, {humidity}% Humidity
            - **Pest Status:** {risk_level} (Count: {pest_count})
            - **Estimated Yield Loss:** {yield_loss}%
            
            Provide a concise 3-point IPM action plan (Immediate, Biological, Economic).
            """)
        ])

        chain = prompt | llm
        
        response = chain.invoke({
            "location": location,
            "temp": weather['temp'],
            "humidity": weather['humidity'],
            "risk_level": risk_level,
            "pest_count": pest_count,
            "yield_loss": yield_loss
        })

        return response.content

    except Exception as e:
        return f"Error connecting to AI: {e}"