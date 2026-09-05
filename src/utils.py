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
def day_total(date, is_eaten,food_data):
    """
    Calculates the total sum of each macronutrient for a specific day.

    Args:
        date (datetime.date): The date to filter the food logs by.
        is_eaten (bool): True to sum logged food, False to sum projected (uneaten) food.

    Returns:
        pd.Series: A series containing the total calculated sums for the tracked macros.
    """
    food_df = food_data.df()
    # Filter out same day df
    filter_df = food_df[(food_df['date'] == date) & (food_df['eat_status']== is_eaten)]
    # Make a series of the sum of these stuff
    sum_the_macro = filter_df[[x.key for x in mm.macro_ui_rules]].sum()
    return sum_the_macro


    