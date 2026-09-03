# Third Party
import streamlit as st
import datetime 
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo
from PIL import Image
# In-app
from src import database as db
from src import macro_models as mm
from src import utils
from src import visuals

import ui

### WEB CONFIGURATION ###
# Streamlit configuration
icon = Image.open("assets/app_logo.png")
st.set_page_config(
    page_title= "babybabynomnom",
    layout="centered", 
    initial_sidebar_state="collapsed",
    page_icon=icon
)
# Kill resize handle on plotly
st.markdown("""
    <style>
    /* Completely disable the drag-to-resize handle on all data_editors */
    [data-testid="stDataFrameResizable"] {
        resize: none !important;
    }
    </style>
""", unsafe_allow_html=True)
### BEGIN INITIALIZATION ###
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
### END INITIALIZATION ###

### BEGIN SIDEBAR UI ###
# 1. username selector
with st.sidebar:
    st.selectbox(
        label = "Select User",
        options = ["Sexy Ano", "Sexy Theo", "Guest"],
        key = "selected_user",
        on_change=utils.state_del,
        args=(['food_data','goals','bucket_values'],)
    )
### END SIDEBAR UI ###

ui.dashboard.draw()