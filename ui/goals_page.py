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
    def __init__(self):
        pass
    def single_goal_card(goals_log:mm.GoalsLog, index:int):
        macro_string = "Average: "
        for x in mm.macro_ui_rules:
            macro_string = macro_string + f"{x.emoji} {getattr(goals_log.macros,x.key)} {x.unit}"
        
        button_label = f"{goals_log.range_type} {index} \n\n {macro_string}"        # B. Draw the cards:
        card_button = st.button(
            label= button_label,
            width= 'stretch',
            key = f"goal_card_button_{str(goals_log.id)}"
        )
        # C. Button action:
        if card_button:
            # C.1 Open the editor
            ui.edit_goals.open(goals_log)
def draw(view_mode:str):
    if view_mode == 'Day':
        st.write('hello')
    if view_mode == 'Week':
        st.write('this is week page')
    if view_mode == 'Month':
        st.write('this is month page')
    if view_mode == 'Year':
        st.write('this is year page')
    if view_mode == 'Custom':
        st.write('this is custom page')
