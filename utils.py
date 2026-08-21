# Third Party
import streamlit as st
import datetime 
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from st_supabase_connection import SupabaseConnection
from streamlit_extras.floating_button import floating_button
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo
from PIL import Image
# Self
import hashmap
import visuals
import database
import components


# 6. (Name Matcher) Fills key values with most recent past data with the same name
def fill_matching_data():
    # Create filtered df with the same name as the search bar
    same_name_df = st.session_state.food_df[st.session_state.food_df["food_name"] == st.session_state.food_name]
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
# 7. Initializer function to initialize stuff.
def simple_initializer(name:str, initial_value):
    if name not in st.session_state:
        st.session_state[name] = initial_value
# 8. Function that reset the session_state values for the username change
def username_change_reset():
    # List the direct keys to delete
    keys_to_delete = ["food_df", "targets_dict_recent"]

    # Add the macro keys from your config
    for config in hashmap.macros_config.values():
        keys_to_delete.append(config["max_key"])
        
    # Safely delete them only if they exist in the session state
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]



# 11. The numbers of the charts display on top of the INPUT FIELDS labels
def number_if_overflow(current_val, projected_val, max_val):
    if current_val + projected_val > max_val:
        return f": :red[{current_val:.0f}/{max_val:.0f} | + {(current_val + projected_val - max_val):.0f} ({(current_val + projected_val - max_val) / max_val * 100:.0f}% Overflow)]"
    else:
        return f": {current_val:.0f}/{max_val:.0f} | + {projected_val:.0f}"

# 12. Used to use two keys of date and time, so have to convert the input fields into date and time in the session state.
def sync_datetime_to_split_keys(datetime_key:str, date_key:str, time_key:str):
    # Safety check (the widget can technically return None if cleared by the user)
    if st.session_state[datetime_key] is not None:
        # Push the extracted values into the existing date and time keys!
        st.session_state[date_key] = st.session_state[datetime_key].date()
        st.session_state[time_key] = st.session_state[datetime_key].time()





# 21. DONUT VIEW MODE FORCE SELECT
def donut_store_memory():
    if st.session_state.donut_view == 'Day':
        st.session_state.donut_memory = 'Day'
    elif st.session_state.donut_view == 'Average':
        st.session_state.donut_memory = 'Average'
# 22 CHANGE for donut df when average is clicked
def segment_donut_change(date_range,food_df):
    if st.session_state.donut_view == 'Average' or st.session_state.donut_memory == 'Average':
        if len(date_range) == 2:
            st.session_state.for_plot_df = food_df[food_df['date'].between(date_range[0],date_range[1])]
    elif st.session_state.donut_view == 'Day' or st.session_state.donut_memory == 'Day':
        same_date_df = food_df[food_df['date']==st.session_state.selected_date] 
        st.session_state.for_plot_df = same_date_df
        
# 24. Action that changes donut_view key to 'Date'
def donut_view_to_date():
    st.session_state.donut_view = 'Day'
# 25. Label for the donut currently showing
def donut_label():
    if st.session_state.selected_date == datetime.datetime.now(ZoneInfo("Asia/Taipei")).date():
        date_label = 'today.'
    elif st.session_state.selected_date == datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()-datetime.timedelta(days=1):
        date_label = 'yesterday.'
    else:
        date_label = f"{st.session_state.selected_date:%d %B %Y}."
    if st.session_state.donut_view == 'Average' or st.session_state.donut_memory == 'Average':
        return f"Showing daily average from {st.session_state.date_range[0]:%d %B %Y} ~ {st.session_state.date_range[1]:%d %B %Y}."
    elif st.session_state.donut_view == 'Day' or st.session_state.donut_memory == 'Day':
        return f"Showing data for {date_label}"
# 26. Action that resets the input session_state variables
def reset_input_field():
    for x in hashmap.inputs_config.values():
        st.session_state[x['norm']] = x['initial']