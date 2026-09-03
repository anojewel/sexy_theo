# Third Party
import streamlit as st
import datetime 
import pandas as pd
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo
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
        on_change=_callback,
        width='stretch'
    )
    
    # 3. Main Script Flow: Execute the action safely
    if pending_key in st.session_state:
        action_str = st.session_state[pending_key]
        del st.session_state[pending_key]
        
        # Execute the mapped function in the main flow (st.rerun() works perfectly here!)
        actions[action_str]()
def macros_input_field(initial_macroval: mm.MacroVal, target_macroval_key, show_macroval = False):
    # A. Use the input values to initial keys
    initialize(target_macroval_key, initial_macroval)
    
    # B. Create pill option labels
    options_map = {f"{x.key}": f"{x.emoji}" for x in mm.macro_ui_rules}
    
    # --- MEMORY INITIALIZATION ---
    initialize("pill_input_mode_memo", 'calories')
    # C1 Draw badges
    macros_number_label=""  
    for x in mm.macro_ui_rules:
        macros_number_label = macros_number_label + f"{getattr(st.session_state[target_macroval_key],x.key)} ({x.unit})‎ ‎ ‎ ‎ ‎ " 
    if show_macroval == True:
        st.button(
            width='stretch',
            type="tertiary",
            label=macros_number_label,
            disabled=True
        ) 
    # C2. Draw the pills
    st.pills(
        label="",
        label_visibility="collapsed",
        width='stretch',
        key="pill_input_mode",
        options=[f"{x.key}" for x in mm.macro_ui_rules],
        format_func=lambda option: options_map[option]
    )
    
    # --- MEMORY CAPTURE ---
    # If the pill is actively selected, commit it to memory. 
    # If it resets to None during a date change, this ignores the None and keeps the old memory.
    if st.session_state.pill_input_mode is not None:
        st.session_state.pill_input_mode_memo = st.session_state.pill_input_mode
        
    # Lock in the active mode using the memory variable
    active_mode = st.session_state.pill_input_mode_memo

    # D. Replace target macro key action using entered value 
    def _change_target():
        for x in mm.macro_ui_rules:
            if active_mode == x.key:
                setattr(st.session_state[target_macroval_key], x.key, st.session_state[f"macros_number_input_{x.key}"])
                
    # E. Sync four session state variables with the four keys for the number input below
    for x in mm.macro_ui_rules:
        st.session_state[f"macros_number_input_{x.key}"] = getattr(st.session_state[target_macroval_key], x.key)
        
    # G. Draw number input
    step_map = {x.key: x.step_val for x in mm.macro_ui_rules}
    st.number_input(
        label="",
        label_visibility="collapsed",
        width='stretch',
        key=f"macros_number_input_{active_mode}",
        on_change=_change_target,
        step=step_map[active_mode],
        format="%.1f",
        min_value=0.0
    )

    
    