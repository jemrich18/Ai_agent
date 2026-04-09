import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    city: str = Field(description="The city name to get weather for")

class CalculateInput(BaseModel):
    expression: str = Field(description="A math expression to evaluate e.g. '2 + 2'")

class HuntingQueryInput(BaseModel):
    query: str = Field(description="A hunting question about tags, regulations, states, gear, or bow tuning")

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

HUNTING_KNOWLEDGE_BASE = {
    "otc_whitetail": {
        "description": "States offering over-the-counter whitetail deer tags for non-residents",
        "states": [
            {"state": "Kansas", "resident": "$27.50", "non_resident": "$442.50", "notes": "Limited draw units exist but most zones are OTC"},
            {"state": "Wisconsin", "resident": "$24", "non_resident": "$160", "notes": "OTC archery and gun tags available"},
            {"state": "Iowa", "resident": "$28", "non_resident": "Draw only", "notes": "Non-residents must draw — highly competitive"},
            {"state": "Illinois", "resident": "$15", "non_resident": "$257.75", "notes": "OTC archery, gun is draw for non-residents"},
            {"state": "Missouri", "resident": "$11", "non_resident": "$200", "notes": "OTC tags available for archery and firearms"},
            {"state": "Oklahoma", "resident": "$24", "non_resident": "$302", "notes": "OTC tags, good public land access"},
            {"state": "Arkansas", "resident": "$10.50", "non_resident": "$350", "notes": "OTC tags, high deer density"},
            {"state": "Texas", "resident": "$25", "non_resident": "$315", "notes": "OTC but most land is private — need lease or outfitter"},
            {"state": "Michigan", "resident": "$20", "non_resident": "$195", "notes": "OTC archery, good public land in UP"},
            {"state": "Pennsylvania", "resident": "$20.90", "non_resident": "$101.90", "notes": "OTC archery and antlerless tags"},
            {"state": "Kentucky", "resident": "$30", "non_resident": "$195", "notes": "OTC archery and gun, solid public land"},
            {"state": "Tennessee", "resident": "$34", "non_resident": "$150", "notes": "OTC tags, WMA hunting available"},
        ],
        "source": "State wildlife agency websites — verify current prices before purchasing"
    },
    "otc_elk": {
        "description": "States offering over-the-counter elk tags for non-residents",
        "states": [
            {"state": "Montana", "unit": "Various", "non_resident": "$1,020", "notes": "Limited OTC B licenses in some districts — most are draw"},
            {"state": "Idaho", "unit": "Most units", "non_resident": "$771.75", "notes": "Strong OTC elk hunting, good public land"},
            {"state": "Wyoming", "unit": "Limited zones", "non_resident": "$621 + license", "notes": "Some OTC antlerless tags, bulls mostly draw"},
            {"state": "Colorado", "unit": "Limited zones", "non_resident": "$761.96", "notes": "OTC tags available in select units — pressure is high"},
            {"state": "Oregon", "unit": "Select units", "non_resident": "$571.75", "notes": "OTC spike elk tags in some units"},
            {"state": "Arizona", "unit": "None OTC", "non_resident": "Draw only", "notes": "Highly coveted draw — takes many points"},
            {"state": "New Mexico", "unit": "Some units", "non_resident": "$845", "notes": "Limited OTC landowner tags available"},
        ],
        "source": "State wildlife agency websites — verify current prices before purchasing"
    },
    "otc_mule_deer": {
        "description": "States offering over-the-counter mule deer tags for non-residents",
        "states": [
            {"state": "Idaho", "non_resident": "$586.75", "notes": "Strong OTC mule deer in southern and eastern zones"},
            {"state": "Montana", "non_resident": "$627", "notes": "Some OTC B licenses available in select districts"},
            {"state": "Wyoming", "non_resident": "$365 + license", "notes": "Limited OTC antlerless, bucks mostly draw"},
            {"state": "Nevada", "non_resident": "Draw only", "notes": "All units are draw — premium tags"},
            {"state": "Utah", "non_resident": "Draw only", "notes": "All general units are draw — tough to draw"},
            {"state": "Colorado", "non_resident": "$761.96", "notes": "OTC available in select units"},
            {"state": "Oregon", "non_resident": "$571.75", "notes": "OTC in select eastern Oregon units"},
        ],
        "source": "State wildlife agency websites — verify current prices before purchasing"
    },
    "preference_points": {
        "description": "How preference points work for western big game draws",
        "info": [
            "Preference points accumulate each year you apply but do not draw a tag",
            "Colorado: Point system for deer, elk, pronghorn, moose — buy points for $35/species/year",
            "Wyoming: Preference points for deer, elk, antelope — $15 application fee per species",
            "Utah: Bonus points system — points double your odds each year",
            "Arizona: Bonus point system — buy points for $13/species/year",
            "Nevada: Bonus points — most competitive draw in the west",
            "New Mexico: Points available for most species — $15/species",
            "Idaho: No preference point system — pure random draw",
            "Montana: bonus point system for some species",
        ],
        "tip": "Start buying points NOW even if you are years away from hunting. Points are cheap and time is the most valuable resource in western hunting."
    },
    "bow_tuning": {
        "description": "Common bow tuning issues and fixes",
        "issues": [
            {
                "problem": "Broadheads hitting different than field points",
                "causes": ["Poor arrow spine", "Rest alignment off", "Nocking point too high or low", "Bow torque"],
                "fixes": [
                    "Walk back tune your rest — start at 20 yards, move back to 40, adjust rest until arrows stack",
                    "Paper tune first — bare shaft through paper at 6 feet to diagnose tear direction",
                    "Tear high means nocking point too low — move nocking point up 1/16 inch at a time",
                    "Tear low means nocking point too high — move down",
                    "Left tear on right-handed bow means rest too far right or arrow too stiff",
                    "Right tear means rest too far left or arrow too weak",
                    "Switch to a fixed blade with offset vanes — helical fletching corrects more flight error",
                ]
            },
            {
                "problem": "Arrows porpoising (fishtailing up and down)",
                "causes": ["Nocking point height wrong", "Arrow spine too weak or stiff"],
                "fixes": ["Paper tune to find nocking point — move up or down in small increments", "Try heavier or lighter spine"]
            },
            {
                "problem": "Peep sight rotating",
                "causes": ["String not properly served", "Peep installed incorrectly"],
                "fixes": ["Take to pro shop for re-serve", "Add string loop above and below peep to lock rotation"]
            },
            {
                "problem": "Inconsistent arrow groups",
                "causes": ["Grip torque", "Anchor point inconsistency", "Release aid trigger timing"],
                "fixes": ["Relax bow hand — death grip causes torque", "Use a consistent anchor — knuckle to cheekbone", "Back tension release for most consistent shot"]
            }
        ]
    },
    "kinetic_energy": {
        "description": "Minimum kinetic energy recommendations for ethical hunting",
        "thresholds": [
            {"animal": "Turkey / small game", "min_ke": "25 ft-lbs", "min_momentum": "0.25 slug-ft/s"},
            {"animal": "Whitetail deer / antelope", "min_ke": "42 ft-lbs", "min_momentum": "0.40 slug-ft/s"},
            {"animal": "Black bear / hog", "min_ke": "52 ft-lbs", "min_momentum": "0.50 slug-ft/s"},
            {"animal": "Elk / moose", "min_ke": "60 ft-lbs", "min_momentum": "0.55 slug-ft/s"},
            {"animal": "Grizzly / African plains game", "min_ke": "65+ ft-lbs", "min_momentum": "0.65 slug-ft/s"},
        ],
        "notes": "Momentum is often considered more important than KE for penetration on heavy-boned animals. Most experienced hunters shoot 400-500 grain arrows for whitetail and 500-650 grain for elk."
    },
    "arrow_spine": {
        "description": "Arrow spine selection guide",
        "info": [
            "Spine is the stiffness of the arrow shaft — measured in deflection (lower number = stiffer)",
            "Common spines: 340, 400, 500, 600 — lower number is stiffer",
            "General rule: heavier draw weight needs stiffer spine",
            "60-70 lbs draw weight with 27-29 inch arrow: 340 spine",
            "50-60 lbs draw weight: 400 spine",
            "40-50 lbs draw weight: 500 spine",
            "Longer arrows need stiffer spine — add one stiffness level per 2 inches over 28",
            "Heavier broadheads (125gr+) require stiffer spine than field points",
            "FOC (front of center) of 10-15% is ideal for hunting — heavier up front improves penetration",
        ]
    },
    "rut_phases": {
        "description": "Whitetail rut phases by time of year",
        "phases": [
            {"phase": "Pre-rut", "timing": "Late October", "notes": "Bucks cruising, scrapes and rubs appearing — good time for scent strategies"},
            {"phase": "Seeking", "timing": "Early November", "notes": "Bucks on their feet all day looking for does — rattle and grunt calls effective"},
            {"phase": "Peak rut", "timing": "Nov 5-15 (varies by latitude)", "notes": "Lockdown phase — bucks with does, hard to pattern but all-day sits worth it"},
            {"phase": "Post-rut", "timing": "Late November", "notes": "Bucks exhausted, feeding heavily — hunt food sources"},
            {"phase": "Second rut", "timing": "Mid December", "notes": "Unbred does cycle again — brief flurry of activity"},
        ],
        "note": "Rut timing shifts 1-2 weeks later as you move south. Kansas peaks around Nov 10-15. Texas can rut in December or January depending on region."
    }
}

def search_kb(query: str) -> str:
    query_lower = query.lower()
    results = []

    if any(word in query_lower for word in ["otc", "over the counter", "whitetail", "deer tag", "non-resident deer"]):
        if any(word in query_lower for word in ["elk"]):
            data = HUNTING_KNOWLEDGE_BASE["otc_elk"]
        elif any(word in query_lower for word in ["mule", "muley"]):
            data = HUNTING_KNOWLEDGE_BASE["otc_mule_deer"]
        else:
            data = HUNTING_KNOWLEDGE_BASE["otc_whitetail"]
        results.append(f"{data['description']}:\n")
        for s in data["states"]:
            results.append(f"- {s['state']}: Non-resident ${s.get('non_resident', 'N/A')} — {s['notes']}")
        results.append(f"\nSource: {data['source']}")

    if any(word in query_lower for word in ["elk tag", "elk hunt", "otc elk", "elk license"]):
        data = HUNTING_KNOWLEDGE_BASE["otc_elk"]
        results.append(f"\n{data['description']}:\n")
        for s in data["states"]:
            results.append(f"- {s['state']}: Non-resident {s['non_resident']} — {s['notes']}")

    if any(word in query_lower for word in ["preference point", "draw odds", "points", "western draw"]):
        data = HUNTING_KNOWLEDGE_BASE["preference_points"]
        results.append(f"\n{data['description']}:\n")
        for item in data["info"]:
            results.append(f"- {item}")
        results.append(f"\nTip: {data['tip']}")

    if any(word in query_lower for word in ["broadhead", "tune", "tuning", "paper tune", "walk back", "porpoise", "fishtail", "peep", "inconsistent"]):
        data = HUNTING_KNOWLEDGE_BASE["bow_tuning"]
        results.append(f"\n{data['description']}:\n")
        for issue in data["issues"]:
            results.append(f"\nProblem: {issue['problem']}")
            results.append("Fixes:")
            for fix in issue["fixes"]:
                results.append(f"  - {fix}")

    if any(word in query_lower for word in ["kinetic energy", "ke ", "momentum", "ethical", "enough energy", "minimum"]):
        data = HUNTING_KNOWLEDGE_BASE["kinetic_energy"]
        results.append(f"\n{data['description']}:\n")
        for t in data["thresholds"]:
            results.append(f"- {t['animal']}: min {t['min_ke']} / {t['min_momentum']}")
        results.append(f"\n{data['notes']}")

    if any(word in query_lower for word in ["spine", "arrow spine", "stiffness", "foc", "front of center", "arrow weight"]):
        data = HUNTING_KNOWLEDGE_BASE["arrow_spine"]
        results.append(f"\n{data['description']}:\n")
        for item in data["info"]:
            results.append(f"- {item}")

    if any(word in query_lower for word in ["rut", "rut phase", "breeding", "scrape", "lockdown", "seeking", "pre-rut"]):
        data = HUNTING_KNOWLEDGE_BASE["rut_phases"]
        results.append(f"\n{data['description']}:\n")
        for phase in data["phases"]:
            results.append(f"- {phase['phase']} ({phase['timing']}): {phase['notes']}")
        results.append(f"\n{data['note']}")

    if results:
        return "\n".join(results)
    return "No specific hunting data found for that query. I'll answer from general knowledge."


@tool(args_schema=HuntingQueryInput)
def search_hunting_knowledge(query: str) -> str:
    """Search a hunting knowledge base for information about OTC tags, state regulations, 
    draw odds, bow tuning, kinetic energy requirements, arrow spine selection, and rut phases."""
    return search_kb(query)

tools = [get_weather, calculate, search_hunting_knowledge]