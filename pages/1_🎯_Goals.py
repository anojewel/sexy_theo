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
from src import visuals
from src import database as db
from src import utils
from src import macro_models as mm
import ui

class GoalCards:
    @staticmethod
    def single_goal_card(goals_log: mm.GoalsLog, food_data):
        # Process numbers:
        food_df = food_data.df()
        
        # Filter for the specific goal's date range
        range_filtered_df = food_df[(goals_log.start_date <= food_df['date']) & (food_df['date'] <= goals_log.end_date)]
        
        # Calculate daily averages
        if range_filtered_df.empty:
            avg_series = {key: 0.0 for key in ['calories', 'carbs', 'protein', 'fat']}
        else:
            # 1. Sum the macros for each individual day
            daily_totals = range_filtered_df.groupby('date')[['calories', 'carbs', 'protein', 'fat']].sum()
            # 2. Find the mean of those daily totals
            avg_series = daily_totals.mean().fillna(0).round(1).to_dict()

        # Line 1 string
        line_1 = f"**{goals_log.start_date.day} {goals_log.start_date:%B %Y} ~ {goals_log.end_date.day} {goals_log.end_date:%B %Y}**"
        
        # Line 2 string
        line_2 = "🎯 Target: "
        for x in mm.macro_ui_rules:
            line_2 += f"{x.emoji} {getattr(goals_log.macros, x.key)} {x.unit}  "
            
        # Line 3 string
        line_3 = "📊 Average: "
        for x in mm.macro_ui_rules:
            line_3 += f"{x.emoji} {avg_series[x.key]} {x.unit}  "
                
        button_label = f"{line_1}\n\n{line_2}\n\n{line_3}"
        
        # B. Draw the cards:
        if st.button(
            label=button_label,
            width='stretch',
            key=f"goal_card_button_{str(goals_log.id)}"
        ):
            ui.edit_goals.open(goals_log)
        

# INITIALIZE SAME AS DASHBOARD
# 1. Initialize selected_user with persisting memory
utils.initialize('selected_user_memo','Sexy Theo')
utils.initialize('selected_user',st.session_state.selected_user_memo)
st.session_state.selected_user_memo = st.session_state.selected_user

# 2. Iniitalize the database form supabase
if 'food_data' not in st.session_state:
    st.session_state.food_data = db.FromSupabase(st.session_state.selected_user,'food_data')
if 'goals' not in st.session_state:
    st.session_state.goals = db.FromSupabase(st.session_state.selected_user,'goals')
if 'user_settings' not in st.session_state:
    st.session_state.goals_settings = db.FromSupabase(st.session_state.selected_user, 'user_settings')
### Sidebar Draw ###
with st.sidebar:
    st.selectbox(
        label = "Select User",
        options = ["Sexy Ano", "Sexy Theo", "Guest"],
        key = "selected_user",
        on_change=utils.state_del,
        args=(['food_data', 'goals', 'user_settings'],)
    )
### 1 ###
# Segment Selector for time range WITH MEMORY
utils.initialize('goal_view_mode_memo', 'Week')

st.segmented_control(
    label='',
    label_visibility='collapsed',
    options=['Day', 'Week', 'Month', 'Year', 'Custom'],
    key='goal_view_mode_raw',
    width='stretch'
)

# Commit selection to memory if it isn't None
if st.session_state.goal_view_mode_raw is not None:
    st.session_state.goal_view_mode_memo = st.session_state.goal_view_mode_raw

# Lock in the active view mode
active_view_mode = st.session_state.goal_view_mode_memo


### 2 ###
# Floating action button
button_clicked = floating_button(
    label="➕ New Goal"
)
if button_clicked:
    ui.new_goal.open(active_view_mode)


### 3 ###
st.markdown(f"**{active_view_mode} Goals**")
# Goal cards draw
for x in st.session_state.goals.list():
    if x.range_type == active_view_mode:
        GoalCards.single_goal_card(x, st.session_state.food_data)