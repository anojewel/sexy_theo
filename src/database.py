# Third Party
import streamlit as st
import datetime 
import pandas as pd
from st_supabase_connection import SupabaseConnection
from streamlit_extras.mandatory_date_range import *
# Self
from . import macro_models as mm


# CONNECT FIRST
conn = st.connection("supabase", type=SupabaseConnection)
class FromSupabase:
    def __init__(self, username, table):
        self.username = username
        self.table = table
        # This is the line that directly downloads
        self.list_of_dict = conn.table(table).select("*").eq("username", self.username).execute().data
    def df(self):
        if self.table == 'food_data':
            food_columns = ['food_name','calories','carbs','protein','fat','date','time','username','eat_status','id']
            # Line if empty data frame  
            if not self.list_of_dict:
                return pd.DataFrame(columns=food_columns)
            # Turn the response into data frame
            else:
                food_df = pd.DataFrame(self.list_of_dict)
                # Convert the datetimes into date and time objects
                food_df = food_df.assign(
                        date=lambda df: pd.to_datetime(df["date"]).dt.date,
                        time=lambda df: pd.to_datetime(df["time"]).dt.time,
                    )
                return food_df
                
        elif self.table == 'goals':
            goals_columns = ['id','username', 'range_type', 'start_date', 'end_date', 'calories', 'carbs', 'protein', 'fat']
            # Check if the table is empty
            if not self.list_of_dict:
                return pd.DataFrame(columns=goals_columns)
            else:
                goals_df = pd.DataFrame(self.list_of_dict)
                # Convert the datetimes back into date objects since we reverted to start_date/end_date
                goals_df = goals_df.assign(
                        start_date=lambda df: pd.to_datetime(df["start_date"]).dt.date,
                        end_date=lambda df: pd.to_datetime(df["end_date"]).dt.date,
                    )
                return goals_df
    def list(self):
        payload_list = []
        if self.table == 'food_data':
            for row in self.list_of_dict:
                food_log = mm.FoodLog(
                    food_name=row['food_name'],
                    macros=mm.MacroVal(row['calories'],row['carbs'],row['protein'],row['fat']),
                    date=datetime.date.fromisoformat(row['date']),
                    time=datetime.time.fromisoformat(row['time']),
                    username=row['username'],
                    eat_status=row['eat_status'],
                    id=row['id']
                    )
                payload_list.append(food_log)
                
        elif self.table == 'goals':
            for row in self.list_of_dict:
                goals_log = mm.GoalsLog(
                    username=row['username'],
                    range_type=row['range_type'],
                    start_date=datetime.date.fromisoformat(row['start_date']),
                    end_date=datetime.date.fromisoformat(row['end_date']),
                    macros=mm.MacroVal(row['calories'],row['carbs'],row['protein'],row['fat']),
                    id=row['id']
                )
                payload_list.append(goals_log)
        return payload_list
def save_food(food_log, food_data):
    payload = {
        'food_name': food_log.food_name,
        'calories': food_log.macros.calories,
        'carbs': food_log.macros.carbs,
        'protein': food_log.macros.protein,
        'fat': food_log.macros.fat,
        'date': str(food_log.date),
        'time': str(food_log.time),
        'username': food_log.username,
        'eat_status': food_log.eat_status
    }
    try:
        if food_log.id is None:
            # Save new
            new_dict = conn.table("food_data").insert(payload).execute()
            # Append to ghost food log for display
            food_data.list_of_dict.extend(new_dict.data)
        else:
            # Save edits
            edited_dict = conn.table("food_data").update(payload).eq('id',int(food_log.id)).execute()
            # Edit the ghost food log for display
            for x in food_data.list_of_dict:
                if x['id'] == int(food_log.id):
                    x.update(edited_dict.data[0])
    except Exception as e:
        st.error("Could not save your food log. Check your connection and try again.", icon="⚠️")       
def delete_food(food_log, food_data):
    try:
        conn.table("food_data").delete().eq('id',int(food_log.id)).execute()
        # Delete the ghost food log for display
        for x in food_data.list_of_dict:
            if x['id'] == int(food_log.id):
                food_data.list_of_dict.remove(x)
                break
    except Exception as e:
        st.error("Could not delete your food log. Check your connection and try again.", icon="⚠️")      
def save_goal(goal_log, goals_data):
    # Reverted payload mapping to start_date and end_date
    payload = {
        'username': goal_log.username,
        'range_type': goal_log.range_type,
        'calories': goal_log.macros.calories,
        'carbs': goal_log.macros.carbs,
        'protein': goal_log.macros.protein,
        'fat': goal_log.macros.fat,
        'start_date': str(goal_log.start_date),
        'end_date': str(goal_log.end_date)
    }
    try:
        if goal_log.id is None:
            # Save new
            new_dict = conn.table("goals").insert(payload).execute()
            goals_data.list_of_dict.extend(new_dict.data)
        else:
            # Save edits
            edited_dict = conn.table("goals").update(payload).eq('id', int(goal_log.id)).execute()
            for x in goals_data.list_of_dict:
                if x['id'] == int(goal_log.id):
                    x.update(edited_dict.data[0])
    except Exception as e:
        st.error("Could not save your goal. Check your connection.", icon="⚠️")
def delete_goal(goal_log, goals_data):
    try:
        conn.table("goals").delete().eq('id', int(goal_log.id)).execute()
        for x in goals_data.list_of_dict:
            if x['id'] == int(goal_log.id):
                goals_data.list_of_dict.remove(x)
                break
    except Exception as e:
        st.error("Could not delete your goal.", icon="⚠️")