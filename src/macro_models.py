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
    def recipes(self, recipe_list):
        payload_list = []
        for x in recipe_list:
            if x not in payload_list:
                if (x.food_id is not None) and (self.id is not None):
                    if int(x.food_id) == int(self.id):
                        payload_list.append(x)
        return payload_list
    # 1. Add recipe_list to the method parameters
    def ingridients(self, ingr_list, recipe_list):
        recipe_id_list = []
        # 2. Pass recipe_list into the method call
        for x in self.recipes(recipe_list):
            if not isinstance(x,int):
                recipe_id_list.append(int(x.ingr_id))
            
        matching_ingr_list = []
        for x in ingr_list:
            if x.id is not None:
                if int(x.id) in recipe_id_list:
                    matching_ingr_list.append(x)
                
        # 3. Add the missing return statement
        return matching_ingr_list
    def ingr_macroval_summed(self, ingr_list, recipe_list):
        # 1. Start with the base food macros
        total = self.macros
        
        # 2. Add scaled macros for each ingredient
        for recipe in self.recipes(recipe_list):
            base_ingr = recipe.ingr(ingr_list)
            
            # Guard against zero-division
            if base_ingr and base_ingr.weight > 0:
                multiplier = float(recipe.weight) / float(base_ingr.weight)
                
                # Scale the ingredient and add it to the running total
                total = total + (base_ingr.macros * multiplier)
                
        return total
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
    def __add__(self, other):
        if isinstance(other, MacroVal):
            return MacroVal(
                self.calories + other.calories,
                self.carbs + other.carbs,
                self.protein + other.protein,
                self.fat + other.fat
            )
        return NotImplemented
    def __mul__(self, multiplier):
        if isinstance(multiplier, (int, float)):
            return MacroVal(
                self.calories * multiplier,
                self.carbs * multiplier,
                self.protein * multiplier,
                self.fat * multiplier
            )
        return NotImplemented
class GoalsLog:
    def __init__(self,username,range_type,start_date,end_date,macros:MacroVal,id=None):
        self.username = username    
        self.range_type = range_type
        self.start_date = start_date
        self.end_date = end_date
        self.macros= macros
        self.id = id
class Ingr:
    def __init__(self,username,display_name,macros:MacroVal,weight,id=None):
        self.username = username
        self.display_name = display_name
        self.macros = macros
        self.weight = weight
        self.id = id
        
    # Streamlit needs these to match default multiselect values!
    def __eq__(self, other):
        if isinstance(other, Ingr):
            return self.id == other.id and self.display_name == other.display_name
        # Allows matching against new custom string inputs
        if isinstance(other, str):
            return self.display_name == other
        return False
        
    def __hash__(self):
        return hash((self.id, self.display_name))

    def recipe(self, food:FoodLog, recipe_list):
        for x in food.recipes(recipe_list):
            if (x.ingr_id is not None) and (self.id is not None):
                if int(x.ingr_id) == int(self.id):
                    return x
class Recipe:
    def __init__(self,food_id,ingr_id,weight,username,id=None):
        self.food_id = food_id
        self.ingr_id = ingr_id
        self.weight = weight
        self.username = username
        self.id=id
    def food(self, food_list):
        for x in food_list:
            # Check that neither ID is missing before comparing
            if (x.id is not None) and (self.food_id is not None):
                # Force both IDs into integers to ensure they match
                if int(x.id) == int(self.food_id):
                    return x
                    
    def ingr(self, ingr_list):
        for x in ingr_list:
            # Check that neither ID is missing before comparing
            if (x.id is not None) and (self.ingr_id is not None):
                # Force both IDs into integers to ensure they match
                if int(x.id) == int(self.ingr_id):
                    return x
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
