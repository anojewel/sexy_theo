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
    # 1. Module to Save the FoodLog item to database
    def save(self, conn):
        payload = {
            'food_name': self.food_name,
            'calories': self.macros.calories,
            'carbs': self.macros.carbs,
            'protein': self.macros.protein,
            'fat': self.macros.fat,
            'date': str(self.date),
            'time': str(self.time),
            'username': self.username,
            'eat_status': self.eat_status
        }
        if self.id is None:
            # Save new
            conn.table("food_data").insert(payload).execute()
        else:
            # Save edits
            conn.table("food_data").update(payload).eq('id',int(self.id)).execute()
    # 2. Module to delete item from database
    def delete(self,conn):
        conn.table("food_data").delete().eq('id',int(self.id)).execute()
    # 3. Module to create a food card based on the given database
class MacroVal:
    '''
    Holds the values of a particular set of numbers representing the calories carbs and protein
    '''
    def __init__(self, calories, carbs, protein, fat):
        self.calories = calories
        self.carbs = carbs
        self.protein = protein
        self.fat = fat
        self.list = [calories,carbs,protein,fat]
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
