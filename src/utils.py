# Third Party
import streamlit as st
import datetime 
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo
# Self
from . import macro_models as mm
def fill_matching_data():
    """
    Searches past food logs for the current food name and updates the 
    session state with its most recent macro values.
    """
    # Create filtered df with the same name as the search bar
    same_name_df = st.session_state.food_data.df()[st.session_state.food_data.df()["food_name"] == st.session_state.food_name]
        # Sort by new
    timesort_same_name_df = same_name_df.sort_values(
        by = ["date", "time"],
        ascending = False
    )
    if not same_name_df.empty:
    # Single row data frame of the newest same name
        newest_same_name_df = timesort_same_name_df.iloc[0]
        for x in mm.macro_ui_rules:
        # Dynamically update the session state
            st.session_state[x.key] = newest_same_name_df[x.key]
def initialize(name:str, initial_value):
    """
    Sets a default value for a Streamlit session state key if it does 
    not already exist.

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

def segment_memorize(key:str, memo_key:str, value):
    """
    Stores the current value of a Streamlit segmented control into a 
    memory variable to persist user navigation.

    Args:
        key (str): The session state key of the widget being observed.
        memo_key (str): The session state key where the memory will be stored.
        value (any): The target value to check and memorize.
    """
    if st.session_state[key] == value:
        st.session_state[memo_key] = value
def initial_bucket_filter():
    """
    Retrieves the active macro target goals for the current date. 
    If multiple goals overlap today, it returns the one with the shortest duration.

    Returns:
        pd.Series: A single data frame row containing the target maximums for each macro.
    """
    # Filter out the goals that contain today
    goals_df = st.session_state.goals.df()
    contain_today_df = goals_df[(goals_df['start_date'] <= datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()) & (datetime.datetime.now(ZoneInfo("Asia/Taipei")).date() <= goals_df['end_date'])].copy()
    # Create duration column:
    contain_today_df['duration'] = contain_today_df['end_date']-contain_today_df['start_date']
    # Sort by duration and select the first row
    return contain_today_df.sort_values(by = 'duration').iloc[0]
def day_total(date, is_eaten):
    """
    Calculates the total sum of each macronutrient for a specific day.

    Args:
        date (datetime.date): The date to filter the food logs by.
        is_eaten (bool): True to sum logged food, False to sum projected (uneaten) food.

    Returns:
        pd.Series: A series containing the total calculated sums for the tracked macros.
    """
    food_df = st.session_state.food_data.df()
    # Filter out same day df
    filter_df = food_df[(food_df['date'] == date) & (food_df['eat_status']== is_eaten)]
    # Make a series of the sum of these stuff
    sum_the_macro = filter_df[[x.key for x in mm.macro_ui_rules]].sum()
    return sum_the_macro
# 12. Generic Pill Buttons with Actions
def pill_buttons(actions: dict, key: str):
    """
    Creates a row of pills that execute assigned functions when clicked.
    Uses a pending state proxy to allow st.rerun() in the mapped functions.
    """
    initialize(key, None)
    pending_key = f"{key}_pending"
    
    # 1. Callback: ONLY manages state, no actions or reruns here!
    def _callback():
        selected = st.session_state[key]
        if selected:
            # Save the choice to the pending flag and visually un-click the pill
            st.session_state[pending_key] = selected
            st.session_state[key] = None 
            
    # 2. Draw the Widget
    st.pills(
        label="hidden_label", 
        label_visibility="collapsed",
        options=list(actions.keys()),
        key=key,
        on_change=_callback
    )
    
    # 3. Main Script Flow: Execute the action safely
    if pending_key in st.session_state:
        action_str = st.session_state[pending_key]
        del st.session_state[pending_key]
        
        # Execute the mapped function in the main flow (st.rerun() works perfectly here!)
        actions[action_str]()