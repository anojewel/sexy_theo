# Third Party
import streamlit as st
import datetime 
from plotly.subplots import make_subplots
from streamlit_extras.floating_button import floating_button
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo
# Self
from . import hashmap

# 1. Name matcher: fills past data with same name to the sesssion state
def fill_matching_data():
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
        for macro in hashmap.macros_config:
        # Dynamically update the session state
            st.session_state[macro.lower()] = newest_same_name_df[macro.lower() ]
# 2. Initializer function to initialize stuff.
def initialize(name:str, initial_value):
    if name not in st.session_state:
        st.session_state[name] = initial_value
# 3. Function that reset the session_state values for the username change
def username_change_reset():
    # List the direct keys to delete
    keys_to_delete = ["food_data", "targets_dict_recent"]

    # Add the macro keys from your config
    for config in hashmap.macros_config.values():
        keys_to_delete.append(config["max_key"])
        
    # Safely delete them only if they exist in the session state
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
# 5. Used to use two keys of date and time, so have to convert the input fields into date and time in the session state.
def sync_datetime_to_split_keys(datetime_key:str, date_key:str, time_key:str):
    # Safety check (the widget can technically return None if cleared by the user)
    if st.session_state[datetime_key] is not None:
        # Push the extracted values into the existing date and time keys!
        st.session_state[date_key] = st.session_state[datetime_key].date()
        st.session_state[time_key] = st.session_state[datetime_key].time()
# 6. DONUT VIEW MODE FORCE SELECT
def donut_store_memory():
    if st.session_state.view_mode == 'Day':
        st.session_state.view_memory = 'Day'
    elif st.session_state.view_mode == 'Week':
        st.session_state.view_memory = 'Week'

        
# 8. Label for the donut currently showing
def donut_label():
    if st.session_state.selected_date == datetime.datetime.now(ZoneInfo("Asia/Taipei")).date():
        date_label = 'today.'
    elif st.session_state.selected_date == datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()-datetime.timedelta(days=1):
        date_label = 'yesterday.'
    else:
        date_label = f"{st.session_state.selected_date:%d %B %Y}."
    if st.session_state.view_mode == 'Average' or st.session_state.view_memory == 'Average':
        return f"Showing daily average from {st.session_state.date_range[0]:%d %B %Y} ~ {st.session_state.date_range[1]:%d %B %Y}."
    elif st.session_state.view_mode == 'Day' or st.session_state.view_memory == 'Day':
        return f"Showing data for {date_label}"
# 9. Action that resets the input session_state variables
def reset_input_field():
    for x in hashmap.inputs_config.values():
        st.session_state[x['norm']] = x['initial']
# 10. Filtering for initialization of bucket_values
def initial_bucket_filter():
    # Filter out the goals that contain today
    goals_df = st.session_state.goals.df()
    contain_today_df = goals_df[(goals_df['start_date'] <= datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()) & (datetime.datetime.now(ZoneInfo("Asia/Taipei")).date() <= goals_df['end_date'])].copy()
    # Create duration column:
    contain_today_df['duration'] = contain_today_df['end_date']-contain_today_df['start_date']
    # Sort by duration and select the first row
    return contain_today_df.sort_values(by = 'duration').iloc[0]
# 11. Create sum series
def macro_totals(date, is_eaten):
    food_df = st.session_state.food_data.df()
    # Filter out same day df
    filter_df = food_df[(food_df['date'] == date) & (food_df['eat_status']== is_eaten)]
    # Make a series of the sum of these stuff
    sum_the_macro = filter_df[[x.lower() for x in hashmap.macros_config]].sum()
    return sum_the_macro