import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    city: str = Field(description="The city name to get weather for")

class CalculateInput(BaseModel):
    expression: str = Field(description="A math expression to evaluate e.g. '2 + 2'")

class KnowledgeBaseInput(BaseModel):
    query: str = Field(description="The topic to search for in the knowledge base")

@tool(args_schema=WeatherInput)
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_response = requests.get(geo_url, params={"name": city, "count": 1})
    geo_data = geo_response.json()

    if not geo_data.get("results"):
        return f"Could not find location: {city}"

    location = geo_data["results"][0]
    lat = location["latitude"]
    lon = location["longitude"]
    name = location["name"]

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_response = requests.get(weather_url, params={
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weathercode,windspeed_10m,relative_humidity_2m",
        "temperature_unit": "fahrenheit",
        "windspeed_unit": "mph",
        "forecast_days": 1
    })
    weather_data = weather_response.json()
    current = weather_data["current"]

    temp = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    wind = current["windspeed_10m"]

    return f"{name}: {temp}°F, humidity {humidity}%, wind {wind} mph"

@tool(args_schema=CalculateInput)
def calculate(expression: str) -> str:
    """Evaluate a basic math expression like '2 + 2' or '10 * 5'."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool(args_schema=KnowledgeBaseInput)
def search_knowledge_base(query: str) -> str:
    """Search an internal knowledge base for information."""
    kb = {
        "python": "Python is a high-level programming language known for readability.",
        "langgraph": "LangGraph is a framework for building stateful AI agent workflows.",
        "django": "Django is a high-level Python web framework for rapid development.",
    }
    for key, value in kb.items():
        if key in query.lower():
            return value
    return "No relevant information found in the knowledge base."