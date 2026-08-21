import datetime 
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo
macros_config = {
    "Calories": {
        "max_key": "max_cal", 
        "max_val": 2500, 
        "rgb": "255, 111, 97", 
        "emoji": "🔥",
        "unit" : "kcal"
    },
    "Carbs": {
        "max_key": "max_carbs", 
        "max_val": 300,  
        "rgb": '106, 90, 205',
        "emoji": "🍞",
        "unit" : "g"
    },
    "Protein": {
        "max_key": "max_protein", 
        "max_val": 100,  
        "rgb": "60, 179, 113", 
        "emoji": "🥩",
        "unit" : "g"
    },
    "Fat": {
        "max_key": "max_fat", 
        "max_val": 75,   
        "rgb": "255, 165, 0", 
        "emoji": "🧈",
        "unit" : "g"
    }
}
inputs_config = {
    "Food":     {"norm": "food_name", "initial": ""},
    "Calories": {"norm": "calories",  "initial": 0.0},
    "Carbs":    {"norm": "carbs",     "initial": 0.0},
    "Protein":  {"norm": "protein",   "initial": 0.0},
    "Fat":      {"norm": "fat",       "initial": 0.0},
    "Time":     {"norm": "time",      "initial":  datetime.datetime.now(ZoneInfo("Asia/Taipei")).time()},
    "Date":     {"norm": "date",      "initial":  datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()}
}