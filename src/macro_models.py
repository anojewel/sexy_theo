class FoodLog:
    '''
    Holds the values of the columns in the food_data table   
    '''
    def __init__(self, food_name, macros: MacroVal, date, time, username, eat_status, id=None):
        self.id = id
        self.food_name = food_name
        self.macros = macros
        self.date = date
        self.time = time
        self.username = username
        self.eat_status = eat_status
class MacroVal:
    '''
    Holds the values of a particular set of numbers representing the calories carbs and protein
    '''
    def __init__(self, calories, carbs, protein, fat):
        self.calories = calories
        self.carbs = carbs
        self.protein = protein
        self.fat = fat
    def dict(self):
        return {
            "calories": self.calories,
            "carbs": self.carbs,
            "protein": self.protein,
            "fat": self.fat
        }
class GoalsLog:
    def __init__(self,username,range_type,start_date,end_date,macros:MacroVal,id=None):
        self.username = username    
        self.range_type = range_type
        self.start_date = start_date
        self.end_date = end_date
        self.macros= macros
        self.id = id
class MacroUI:
    """
    Holds the UI rules and display settings for drawing a macro input field or progress bar.
    """
    def __init__(self, title, key, max_val, rgb, emoji, unit, step_val):
        self.title = title
        self.key = key          
        self.max_val = max_val
        self.rgb = rgb
        self.emoji = emoji
        self.unit = unit
        self.step_val = step_val
# FOR UI CONFIGURATIONS:
macro_ui_rules = [
    MacroUI(
        title="Calories", 
        key="calories", 
        max_val=1700, 
        rgb="255, 111, 97", 
        emoji="🔥", 
        unit="kcal",
        step_val=50.0
    ),
    MacroUI(
        title="Carbs", 
        key="carbs", 
        max_val=220, 
        rgb="106, 90, 205", 
        emoji="🍞", 
        unit="g",
        step_val=5.0
    ),
    MacroUI(
        title="Protein", 
        key="protein", 
        max_val=95, 
        rgb="60, 179, 113", 
        emoji="🥩", 
        unit="g",
        step_val=5.0
    ),
    MacroUI(
        title="Fat", 
        key="fat", 
        max_val=50, 
        rgb="255, 165, 0", 
        emoji="🧈", 
        unit="g",
        step_val=5.0
    )
]
