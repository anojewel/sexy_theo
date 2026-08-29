# Third Party
import streamlit as st
import datetime 
import pandas as pd
from plotly.subplots import make_subplots
from st_supabase_connection import SupabaseConnection
from streamlit_extras.floating_button import floating_button
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo
# Self
from . import hashmap
from . import utils

#CONNECT FIRST
conn = st.connection("supabase", type=SupabaseConnection)
# 1. LOAD FOOD DATA
@st.cache_data
def load_food_data(username_input):
    # Assign variable to the food_data table that has equal user name values
    response = conn.table("food_data").select("*").eq("username", username_input).execute()
    # List of appropriate column names:
    column_name = [x["norm"] for x in hashmap.inputs_config.values()] + ["id"] + ["username"] + ["eat_status"] #<-- add the id column
    # Check if the table is empty
    if not response.data:
        return pd.DataFrame(columns = column_name)
    food_df = (
    pd.DataFrame(response.data)
    .assign(
        date=lambda df: pd.to_datetime(df["date"]).dt.date,
        time=lambda df: pd.to_datetime(df["time"]).dt.time,
    ))
    return food_df[column_name]
# 2. LOAD GOALS
@st.cache_data
def load_goals_data(username_input):
    # Assign variable to the food_data table that has equal user name values
    response = conn.table("goals").select("*").eq("username", username_input).execute()
    # List of appropriate column names:
    column_name = ['id','username', 'range_type', 'start_date', 'end_date', 'calories', 'carbs', 'protein', 'fat']
    # Check if the table is empty
    if not response.data:
        goals_df = pd.DataFrame(
            columns = column_name, 
            data = [[None, username_input, 'custom', datetime.datetime.now(ZoneInfo('Asia/Taipei')).date(), datetime.datetime.now(ZoneInfo('Asia/Taipei')).date()+datetime.timedelta(days = 365*100)] + [x['max_val'] for x in hashmap.macros_config.values()]]
            )
        return goals_df
    goals_df = (
    pd.DataFrame(response.data)
    .assign(
        start_date=lambda df: pd.to_datetime(df["start_date"]).dt.date,
        end_date=lambda df: pd.to_datetime(df["end_date"]).dt.date,
    ))
    
    return goals_df[column_name]
# 3. Log food function for the log food button
def log_food():
    utils.sync_datetime_to_split_keys('datetime','date','time')
    valid_input = st.session_state.food_name and all(st.session_state[x.lower()]>= 0 for x in hashmap.macros_config)
    # Check if fields are empty, zero values are accepted, name is mandatory.
    if valid_input:
        # Put the stuff in input field into payload
        payload={
            config["norm"]:st.session_state[config["norm"]] for config in hashmap.inputs_config.values()
        }
        # Mark the username into the payload
        payload["username"] = st.session_state.selected_user
        # Mark the eating status based on before/after
        payload["eat_status"] = (True if st.session_state.datetime.replace(tzinfo = ZoneInfo("Asia/Taipei")) <= datetime.datetime.now(ZoneInfo("Asia/Taipei")) else False)
        # Change the datetime value in the payload (AFTER PUSHING TO FOOD DF) to strinsg
        payload["date"] = payload["date"].isoformat()
        payload["time"] = payload["time"].isoformat()
        # Delete the id column before pushing to supabase
        # PUSH THE DATA TO SUPABASE
        conn.table("food_data").insert(payload).execute()
        # Clear input fields after adding ingredient
        for x in hashmap.inputs_config.values():
                st.session_state[x["norm"]] = x["initial"]
        # MANUALLY clear the new UI-only datetime widget
        st.session_state["datetime"] = datetime.datetime.now(ZoneInfo("Asia/Taipei"))
        # Rerun the whoel script
        #Clear cache
        st.cache_data.clear()
        st.session_state.food_df = load_food_data(st.session_state.selected_user)
        
    else:
        st.error("Please fill in all fields with valid values.")
# 4. SAVING MAX VALUES
def save_max():
    # Define the dictionary payload as the data from session_state
    payload = {x["max_key"] : st.session_state[x["max_key"]] for x in hashmap.macros_config.values()}
    payload["username"] = st.session_state.selected_user
    # Push to database
    conn.table("macro_goals").insert(payload, count=None).execute()
    # Clear cache
    st.cache_data.clear()

# 5. DELETE FOOD
def delete_selected_food(row):
   # Delete the data in the supabase
    conn.table("food_data").delete().eq('id',int(row['id'])).execute()
    #Clear cache
    st.cache_data.clear()
    st.session_state.food_df = load_food_data(st.session_state.selected_user)
# 6. SAVE EDITS TO DATABASE
def save_edit(row):
    utils.sync_datetime_to_split_keys('edit_datetime','edit_date','edit_time')
    valid_input = st.session_state['edit_'+'food_name'] and all(st.session_state['edit_'+ x.lower()]>= 0 for x in hashmap.macros_config)
    # Check if fields are empty, zero values are accepted, name is mandatory.
    if valid_input:
        # Put the stuff in input field into payload
        payload={
            config["norm"]:st.session_state['edit_'+ config["norm"]] for config in hashmap.inputs_config.values()
        }
        # Mark the username into the payload
        payload["username"] = st.session_state.selected_user
        # Mark the eating status based on the value in the pill button
        payload["eat_status"] = st.session_state.edit_eat_status
        # Change the datetime value in the payload (AFTER PUSHING TO FOOD DF) to strinsg
        payload["date"] = payload["date"].isoformat()
        payload["time"] = payload["time"].isoformat()
        # PUSH THE DATA TO SUPABASE
        conn.table("food_data").update(payload).eq('id',int(row['id'])).execute()
        # Clear input fields after adding ingredient
        for x in hashmap.inputs_config.values():
                st.session_state[x["norm"]] = x["initial"]
        # MANUALLY clear the new UI-only datetime widget
        st.session_state["datetime"] = datetime.datetime.now(ZoneInfo("Asia/Taipei"))
        # clear the cache
        st.cache_data.clear()
        # Reload the food df with supabase
        st.session_state.food_df = load_food_data(st.session_state.selected_user)
    else:
        st.error("Please fill in all fields with valid values.")
    # CLEAR CACHE
