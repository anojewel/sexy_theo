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
from . import macro_models as mm

# CONNECT FIRST
conn = st.connection("supabase", type=SupabaseConnection)
class FromSupabase:
    def __init__(self,username,table):
        self.username = username
        self.table = table
        # This is the line that directly downloads
        self.list_of_dict = conn.table(table).select("*").eq("username", self.username).execute().data

    # 1. Helps convert to dataframe
    def df(self):
        if self.table == 'food_data':
            food_columns = ['food_name','calories','carbs','protein','fat','date','time','username','eat_status','id']
            # Line if empty data frame  
            if not self.list_of_dict:
                return pd.DataFrame(columns = food_columns)
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
                goals_df = pd.DataFrame(
                    columns = goals_columns, 
                    data = [[None, self.username, 'custom', datetime.datetime.now(ZoneInfo('Asia/Taipei')).date(), datetime.datetime.now(ZoneInfo('Asia/Taipei')).date()+datetime.timedelta(days = 365*100)] + [x['max_val'] for x in hashmap.macros_config.values()]]
                    )
                return goals_df
            else:
                goals_df = pd.DataFrame(self.list_of_dict)
                # Convert the datetimes into date and time objects
                goals_df = goals_df.assign(
                        date=lambda df: pd.to_datetime(df["start_date"]).dt.date,
                        time=lambda df: pd.to_datetime(df["end_date"]).dt.date,
                    )
                return goals_df
    # 2. Helps convert into list of FoodLog objects
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
                goals_log = "later create goals log"
                payload_list.append(goals_log)
        return payload_list