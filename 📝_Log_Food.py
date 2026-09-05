# Third Party
import streamlit as st
from streamlit_extras.mandatory_date_range import *
from PIL import Image
# In-app
from src import db, lmn
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
# 1. Username selector package:
lmn.username_selector()
# 2. Iniitalize the database form supabase
if 'food_data' not in st.session_state:
    st.session_state.food_data = db.FromSupabase(st.session_state.selected_user,'food_data')
if 'goals' not in st.session_state:
    st.session_state.goals = db.FromSupabase(st.session_state.selected_user,'goals')
### END INITIALIZATION ###

### BEGIN SIDEBAR UI ###

        
### END SIDEBAR UI ###

ui.dashboard.draw()