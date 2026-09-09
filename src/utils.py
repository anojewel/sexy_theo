# Third Party
import streamlit as st
from streamlit_extras.mandatory_date_range import *
# Self
from . import macro_models as mm
def initialize(name:str, initial_value):
    """
    Sets a default value for a Streamlit session state key if it does 
    not already exist. Do not use for callable initial values.

    Args:
        name (str): The name of the session state key to initialize.
        initial_value: The starting value to assign to the key.
    """
    if name not in st.session_state:
        st.session_state[name] = initial_value   
def state_del(keys_list:list):
    """
    Safely removes a list of keys from the Streamlit session state.

    Args:
        keys_list (list): A list of strings representing the keys to be deleted.
    """
    for x in keys_list:
        if x in st.session_state:
            del st.session_state[x]
def goal_specificity_choose(target_date:date):
    goals_df = st.session_state.goals.df()
    
    # Guard clause: if there are no goals at all
    if goals_df.empty:
        raise ValueError("No goals exist in database.")

    contain_target_df = goals_df[
        (goals_df['start_date'] <= target_date) & 
        (target_date <= goals_df['end_date'])
    ].copy()
    
    # Guard clause: if no goals overlap with today
    if contain_target_df.empty:
        raise ValueError("No active goals for today.")
        
    contain_target_df['duration'] = contain_target_df['end_date'] - contain_target_df['start_date']
    return contain_target_df.sort_values(by='duration').iloc[0]
import pandas as pd
import streamlit as st
from . import macro_models as mm

def day_total(date, is_eaten, food_data, ingredient_list=None, recipe_list=None):
    """
    Calculates the true total sum of each macronutrient (base + ingredients) for a specific day.

    Args:
        date (datetime.date): The date to filter the food logs by.
        is_eaten (bool): True to sum logged food, False to sum projected (uneaten) food.
        food_data: The database object containing the food logs.
        ingredient_list (list): List of all ingredients (defaults to st.session_state).
        recipe_list (list): List of all recipes (defaults to st.session_state).

    Returns:
        pd.Series: A series containing the total calculated sums for the tracked macros.
    """
    # 1. Default to session state if not explicitly provided in the function call
    if ingredient_list is None:
        ingredient_list = st.session_state.ingredients_list
    if recipe_list is None:
        recipe_list = st.session_state.recipe_list
        
    # 2. Initialize a zeroed MacroVal
    total_macros = mm.MacroVal(0.0, 0.0, 0.0, 0.0)
    
    # 3. Iterate through objects instead of raw DataFrame rows
    for food in food_data.list():
        if food.date == date and food.eat_status == is_eaten:
            # Calculate true macros and add them to the running total
            food_true_macros = food.ingr_macroval_summed(ingredient_list, recipe_list)
            total_macros = total_macros + food_true_macros
            
    # 4. Convert the dictionary back to a Pandas Series before returning
    return pd.Series(total_macros.dict())
import streamlit as st

def ai_debug_panel():
    with st.expander("🛠️ Debug Panel", expanded=False):
        st.markdown("### 1. Environment & Database")
        st.write(f"**Active User:** `{st.session_state.get('selected_user', 'None')}`")
        
        # Database Row Counts
        c1, c2, c3, c4 = st.columns(4)
        food_list = st.session_state.get('food_data_list', [])
        ingr_list = st.session_state.get('ingredients_list', [])
        rcp_list = st.session_state.get('recipe_list', [])
        goal_list = st.session_state.get('goals_list', [])
        
        c1.metric("🍔 Food Logs", len(food_list))
        c2.metric("🧂 Ingredients", len(ingr_list))
        c3.metric("🔗 Recipes", len(rcp_list))
        c4.metric("🎯 Goals", len(goal_list))

        st.markdown("### 2. Active Session State (UI Memory)")
        # Filter out massive dataframes and only show UI/Payload keys
        tracked_keys = {}
        for key, val in st.session_state.items():
            if any(keyword in key for keyword in ['payload', 'edit_', 'new_', 'target', 'memo']):
                # Truncate long string representations for clean UI
                val_str = str(val)
                tracked_keys[key] = val_str[:150] + "..." if len(val_str) > 150 else val_str
                
        if tracked_keys:
            st.json(tracked_keys)
        else:
            st.info("No active UI payloads found.")

        st.markdown("### 3. Math Sanity Check")
        # Grab the most recently logged food (if any exist) to test the __add__ and __mul__ operators
        if food_list:
            test_food = food_list[-1]
            st.write(f"**Target Food:** `{test_food.food_name}` (ID: {test_food.id})")
            
            c_base, c_true = st.columns(2)
            with c_base:
                st.caption("Base Macros (DB Raw)")
                st.json(test_food.macros.dict())
                
            with c_true:
                st.caption("True Macros (Base + Ingredients)")
                try:
                    true_macros = test_food.ingr_macroval_summed(ingr_list, rcp_list)
                    st.json(true_macros.dict())
                except Exception as e:
                    st.error(f"Math Error: {e}")
            
            # Print associated recipes to verify links
            linked_recipes = test_food.recipes(rcp_list)
            st.write(f"**Attached Recipes:** `{len(linked_recipes)}`")
            for r in linked_recipes:
                linked_ingr = r.ingr(ingr_list)
                name = linked_ingr.display_name if linked_ingr else "Unknown/Ghost"
                st.markdown(f"- 🔸 **{name}**: {r.weight}g (Ingr ID: {r.ingr_id})")
        else:
            st.info("No food logged yet to test math.")

    