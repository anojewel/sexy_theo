# Note for AI:
# This is my project for learning python from scratch by making a streamlit app for tracking calories for my grilfriend
# I'd prefer to learn to be given what syntax for what instead of giving me the whole block of code to copy paste. If it's tedious or necessary please tell me why copy pasting is preferrable in certain scenario. Also, i'd like to learn concepts since I am new at coding.
# Learning Logs
# Aug 03, 2026 (Day 1): 
# Learned streamlit UI, setting up virtual environments, random ugly code
# Aug 04, 2026 (Day 2): 
# Python keywords and bullshits jargon learning i keep fucking up
# Aug 05, 2026 (Day 3): 
# Realized streamlit reruns every single click, so use session state
# Aug 06, 2026 (Day 4): 
# Realized streamlit doesnt save data, spent the whole day trying to connect to google sheets, managing keys.
# Aug 07, 2026 (Day 5): 
# Created the visual data frame table that you can add from table input
# Aug 08, 2026 (Day 6): 
# Created the visual progress bars using plotly, first time making use of defining my own function.
# Created the date filter table that only views the selected date
# Aug 09, 2026 (Day 7): 
# Realized that using a save button is faster and saves amount of data transferred to database, spent a lot of time making a save button functional
# Also made a highlight feature of the stuff that is not saved.
# Aug 10, 2026 (Day 8):
# Rearrange code script tidiness, and order.
# Realized a lot of the data is repeating, so implement DRY code, using loops to do stuff for me.
# Doing the above needs me to understand what is a list, tuple, and pandas series.
# Aug 11, 2026 (Day 9):
# Finished replacing repeating code to a dry one.
# Aug 12, 2026 (Day 10):
# Switching from gsheets to supabase
# Aug 13, 2026 (Day 11):
# Bugfixing the switch to supabase
# Added a user selector
# Added interactive data_editor 
# Aug 14, 2026 (Day 12):
# bug fix the data_editor.understand how it controls data
# Aug 15, 2026 (Day 13):
# data_editor connect with bar
# Added bottom container, discovered streamlit extras
# Deploy for the first time 
# Aug 16, 2026 (Day 14):
# Mobile ui restricts one element on 1 row, need UI overhaul
# Uses st.dialog and popovers and st.segment thing for single row butotns.
# Bugfixing the save stuff 
# NEW DONUT PLOTLY GRAPHS YIIPPE
# Chagne date and time inputs into one single datetime input
# Made it private in streamlit only though
# Aug 17, 2026 (Day 15):
# Change save button/main database table into pillbox per item mode
# Added eat status and its functions
# Aug 18, 2026 (Day 16): 
# added all the buttons and their functions correctly
# save delete eat status functions aare added and bugfixxed
# Aug 19, 2026 (Day 17):
# Change to date range picker and their functions
# Change food data filtering
# Added a average view mode and day view mode THIS IS UNEXPECTED SO MUCH WORK
# Migrated google sheets data
# Aug 20, 2026 (Day 18):
# make close menu clears the session state variables
# changed color UI to use rgb and put rgb in hashmap, opacity play
# REFACTORING TO DIFFERENT FILE NAMESSS woohooo, just learning
# Aug 21 to Aug 28, 2026 (Day 19 ~ 26): 
# holiday
# Aug 29, 2026 (Day 27):
# Refactoring just to put ui folderes and src folders
# Created a new data table for goals, need a lot of work just to make small changes? 
# My data management is not quite right
# Aug 30, 2026 (Day 28):
# learned class and refactoring again using classes
# Learning what is Object Oriented Programming and applying it in the refactoring

# Plans:
# update the name matcher using FUZZY SEARCH DIFFLIB
# specialized input streamlit extras search?????
# make max value time dependent
# ingredient mode please
# Refactor based on purpose.
### IMPORTS ###
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
st.session_state.water_values = utils.macro_totals(st.session_state.selected_date, True)
st.session_state.oil_values = utils.macro_totals(st.session_state.selected_date, False)
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
        on_change = utils.username_change_reset
    )
### END SIDEBAR UI ###


### BEGIN MAIN UI ###
# Segmented Control for changing homepage view
view_mode_mode = st.segmented_control(
    label = "",
    label_visibility = 'collapsed',
    options = ['Day', 'Week'],
    key = 'view_mode',
    width = 'stretch',
    selection_mode = 'single',
    on_change = utils.donut_store_memory,
    default = 'Day'
)
# Change homepage view depending on this key
if st.session_state.view_mode == 'Day':
    day_view.day_view()
elif st.session_state.view_mode == 'Week':
    week_view.week_view()
