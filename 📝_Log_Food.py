# Third Party
import streamlit as st
import datetime 
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo
from PIL import Image
# In-app
from src import components
from src import database as db
from src import macro_models as mm
from src import utils
from src import visuals
from ui import *

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
# 1. This key is the tag for the whole app for the username column
utils.initialize('selected_user','Sexy Theo')
# 2. Iniitalize the database form supabase
if 'food_data' not in st.session_state:
    st.session_state.food_data = db.FromSupabase(st.session_state.selected_user,'food_data')
if 'goals' not in st.session_state:
    st.session_state.goals = db.FromSupabase(st.session_state.selected_user,'goals')
# 3. Variable for the date buttons on top of the food cards
utils.initialize('selected_date', datetime.datetime.now(ZoneInfo("Asia/Taipei")).date())
# 4. Constant update the values for the donuts with the selected_date
st.session_state.water_values = utils.day_total(st.session_state.selected_date, True)
st.session_state.oil_values = utils.day_total(st.session_state.selected_date, False)
# 5. Initialize the maximum values of the donuts
if 'bucket_values' not in st.session_state:
    st.session_state.bucket_values = utils.initial_bucket_filter()
# 6. This is to initialize the view_mode so the default view is to be day
utils.initialize('view_mode', 'Day')
# 8. This is needed so that when no segment is selected, it will retain the last chosen segment
utils.initialize('view_memory', 'Day')
### END INITIALIZATION ###

### BEGIN SIDEBAR UI ###
# 1. username selector
with st.sidebar:
    st.selectbox(
        label = "Select User",
        options = ["Sexy Ano", "Sexy Theo", "Guest"],
        key = "selected_user",
        on_change=utils.state_del,
        args=(['food_data'],)
    )
### END SIDEBAR UI ###


### BEGIN MAIN UI ###
# Segmented Control for changing homepage view
st.segmented_control(
    label = "",
    label_visibility = 'collapsed',
    options = ['Day', 'Week'],
    key = 'view_mode',
    width = 'stretch',
    selection_mode = 'single',
    on_change = utils.segment_memorize('view_mode','view_memory',st.session_state.view_mode),
    default = 'Day'
)
# Change homepage view depending on this key
if st.session_state.view_mode == 'Day':
    day_view.day_view()
elif st.session_state.view_mode == 'Week':
    week_view.week_view()
