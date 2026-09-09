# Third Party
import streamlit as st
import datetime 
import pandas as pd
from st_supabase_connection import SupabaseConnection
from streamlit_extras.mandatory_date_range import *
# Self
from . import macro_models as mm
from . import utils
 

# CONNECT FIRST
conn = st.connection("supabase", type=SupabaseConnection)
class Table:
    def __init__(self, username, name, mm_class:str, columns, date_columns:list=[], time_columns:list=[]):
        self.username = username
        self.name = name
        self.mm_class = mm_class
        self.columns = [col for col in columns if col not in [x.key for x in mm.macro_ui_rules]]
        self.date_columns = date_columns
        self.time_columns = time_columns
        self.list_of_dict = conn.table(name).select("*").eq("username", self.username).execute().data
    def df(self):
        cache_key = f"{self.name}_df"
        
        # 1. Check cache FIRST before doing any math
        if cache_key not in st.session_state:
            if not self.list_of_dict:
                st.session_state[cache_key] = pd.DataFrame(columns=self.columns)
            else:
                payload_df = pd.DataFrame(self.list_of_dict)
                for col in self.date_columns:
                    payload_df[col] = pd.to_datetime(payload_df[col]).dt.date
                for col in self.time_columns:
                    payload_df[col] = pd.to_datetime(payload_df[col]).dt.time
                st.session_state[cache_key] = payload_df
                
        return st.session_state[cache_key]

    def list(self):
        cache_key = f"{self.name}_list"
        
        if cache_key not in st.session_state:
            payload_list = []
            for row in self.list_of_dict:
                row_data = {}
                for col in self.columns:
                    val = row[col]
                    if val is not None:
                        if col in self.date_columns:
                            val = pd.to_datetime(val).date()
                        elif col in self.time_columns:
                            val = pd.to_datetime(val).time()
                    row_data[col] = val

                if all(k in row for k in [x.key for x in mm.macro_ui_rules]):
                    row_data['macros'] = mm.MacroVal(
                        row['calories'], row['carbs'], row['protein'], row['fat']
                    )
                obj = getattr(mm, self.mm_class)(**row_data)
                payload_list.append(obj)
            st.session_state[cache_key] = payload_list
            
        return st.session_state[cache_key]
def save(data:list, database: Table):
    update_list = []
    insert_list = []
    
    # 2. Convert class objects to dictionaries
    for obj in data:
        payload = {}
        for col in database.columns:
            if col != 'id':
                val = getattr(obj, col)
                if val is not None and (col in database.date_columns or col in database.time_columns):
                    val = str(val)
                payload[col] = val
                
        if hasattr(obj, 'macros') and obj.macros is not None:
            for x in mm.macro_ui_rules:
                payload[x.key] = getattr(obj.macros, x.key)
                
        # 3. Split based on ID presence to avoid Supabase null-injection
        if obj.id is not None:
            payload['id'] = int(obj.id)
            update_list.append(payload)
        else:
            insert_list.append(payload)

    # 4. Upsert/Insert separately and handle errors
    returned_data = []
    try:
        # Update existing records
        if update_list:
            res_up = conn.table(database.name).upsert(update_list).execute()
            returned_data.extend(res_up.data)
            
        # Insert brand new records
        if insert_list:
            res_in = conn.table(database.name).upsert(insert_list).execute()
            returned_data.extend(res_in.data)
            
        # Update the 'ghost data' list with the returned data
        for returned_row in returned_data:
            existing = False
            for i, ghost_row in enumerate(database.list_of_dict):
                if ghost_row.get('id') == returned_row['id']:
                    database.list_of_dict[i].update(returned_row)
                    existing = True
                    break
            if not existing:
                database.list_of_dict.append(returned_row)
                
        # Clear cached views
        utils.state_del([f"{database.name}_df", f"{database.name}_list"])
        return returned_data
        
    except Exception as e:
        st.error(f"Could not save your data. Error : {type(e).__name__}", icon="⚠️")
        st.exception(e)
            
def delete(data, database:Table):
    id_list = []
    for x in data:
        id_list.append(x.id)
    try:
        conn.table(database.name).delete().in_('id', id_list).execute()
        # Delete the ghost food log for display
        database.list_of_dict = [x for x in database.list_of_dict if x['id'] not in id_list]
        # Clear the cached views so the next UI draw fetches the updated data
        utils.state_del([f"{database.name}_df", f"{database.name}_list"])
    except Exception as e:
        st.error("Could not delete your data. Check your connection and try again.", icon="⚠️")
def initialize(target_username):
    if 'food_data' not in st.session_state:
        st.session_state.food_data = Table(
            username=target_username,
            name='food_data',
            mm_class='FoodLog',
            columns=['food_name', 'calories', 'carbs', 'protein', 'fat', 'date', 'time', 'username', 'eat_status', 'id'],
            date_columns=['date'],
            time_columns=['time']
        )

    if 'goals' not in st.session_state:
        st.session_state.goals = Table(
            username=target_username,
            name='goals',
            mm_class='GoalsLog',
            columns=['range_type', 'calories', 'carbs', 'protein', 'fat', 'start_date', 'end_date', 'username', 'id'],
            date_columns=['start_date', 'end_date']
        )
    
    if 'ingredients' not in st.session_state:
        st.session_state.ingredients = Table(
            username=target_username,
            name='ingredients',
            mm_class='Ingr',
            columns=['display_name', 'calories', 'carbs', 'protein', 'fat', 'weight', 'username', 'id']
        )
    st.session_state.ingredients.df()
    st.session_state.ingredients.list()
    
    if 'recipe' not in st.session_state:
        st.session_state.recipe = Table(
            username= target_username,
            name='recipe',
            mm_class='Recipe',
            columns=['food_id', 'ingr_id', 'weight', 'id', 'username']
        )
    st.session_state.recipe.df()           
    st.session_state.recipe.list()      