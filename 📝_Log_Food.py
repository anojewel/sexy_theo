# Note for AI:
# This is my project for learning python from scratch by making a streamlit app for tracking calories for my grilfriend
# I'd prefer to learn to be given what syntax for what instead of giving me the whole block of code to copy paste. If it's tedious or necessary please tell me why copy pasting is preferrable in certain scenario. Also, i'd like to learn concepts since I am new at coding.
# Learning Logs
# Day 1: 
# Learned streamlit UI, setting up virtual environments, random ugly code
# Day 2: 
# Python keywords and bullshits jargon learning i keep fucking up
# Day 3: 
# Realized streamlit reruns every sinlge click, so use session state
# Day 4: 
# Realized streamlit doesnt save data, spent the whole day trying to connect to google sheets, managing keys.
# Day 5: 
# Created the visual data frame table that you can add from table input
# Day 6: 
# Created the visual progress bars using plotly, first time making use of defining my own function.
# Created the date filter table that only views the selected date
# Day 7: 
# Realized that using a save button is faster and saves amount of data transferred to database, spent a lot of time making a save button functional
# Also made a highlight feature of the stuff that is not saved.
# Day 8:
# Rearrange code script tidiness, and order.
# Realized a lot of the data is repeating, so implement DRY code, using loops to do stuff for me.
# Doing the above needs me to understand what is a list, tuple, and pandas series.
# Day 9:
# Finished replacing repeating code to a dry one.
# Day 10:
# Switching from gsheets to supabase
# Day 11:
# Bugfixing the switch to supabase
# Added a user selector
# Added interactive data_editor 
# Day 12:
# bug fix the data_editor.understand how it controls data
# Day 13:
# data_editor connect with bar
# Added bottom container, discovered streamlit extras
# Deploy for the first time 
# Day 14:
# Mobile ui restricts one element on 1 row, need UI overhaul
# Uses st.dialog and popovers and st.segment thing for single row butotns.
# Bugfixing the save stuff 
# NEW DONUT PLOTLY GRAPHS YIIPPE
# Chagne date and time inputs into one single datetime input
# Made it private in streamlit only though
# Day 15
# Change save button/main database table into pillbox per item mode
# Added eat status and its functions
# Day 16 
# added all the buttons and their functions correctly
# save delete eat status functions aare added and bugfixxed
# Day 17
# Change to date range picker and their functions
# Change food data filtering
# Added a average view mode and day view mode THIS IS UNEXPECTED SO MUCH WORK
# Migrated google sheets data
# Day 18
# make close menu clears the session state variables
# changed color UI to use rgb and put rgb in hashmap, opacity play
# REFACTORING TO DIFFERENT FILE NAMESSS
# Day 19 holiday
# Day 20 holiday
# Day 21 holiday
# Plans:
# update the name matcher using FUZZY SEARCH DIFFLIB
# specialized input streamlit extras search?????
# make max value time dependent
# ingredient mode please
# Bugs:
### IMPORTS ###
# Third Party
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
import hashmap
import visuals
import database
import components
import utils
### BEGIN CONFIGURATION ###

icon = Image.open("assets/app_logo.png")
st.set_page_config(
    page_title= "babybabynomnom",
    layout="centered", 
    initial_sidebar_state="collapsed",
    page_icon=icon
)
# KIll reszie handle on plotly
st.markdown("""
    <style>
    /* Completely disable the drag-to-resize handle on all data_editors */
    [data-testid="stDataFrameResizable"] {
        resize: none !important;
    }
    </style>
""", unsafe_allow_html=True)
# for fucking up timezones
LOCAL_TZ = ZoneInfo("Asia/Taipei")

### END CONFIGURATION ###
### BEGIN INDEP DICTIONARY ###
# 1. Macro Configuration Dictionary
# Combines: macro_str_list, max_str_list, initial_max_list, bar_color_primary, bar_color_secondary
# 2. Input Fields Dictionary
# Combines: input_str_list, input_str_list_norm, input_initial_values

### END INDEP DICTIONARIES ###
### BEGIN DEFINITIONS ###



### BEGIN BACKEND CONNECTION ###

### END BACKEND CONNECTION ###

### BEGIN INITIALIZATION ###
# 1. (User Select) Initialize selected user
utils.simple_initializer(name = "selected_user", initial_value = "Sexy Theo")
# 2. CONSTANT UPDATE food data from supabase
st.session_state.food_df = database.load_food_data(st.session_state.selected_user)
# 3. (Log Food) Initialize session state keys for the input fields
for x in hashmap.inputs_config.values():
    utils.simple_initializer(name = x["norm"], initial_value = x["initial"])
# 4. (Max Values) Initialize macro targets into a dictionary from supabase with the most recent value
if 'targets_dict_recent' not in st.session_state:
    st.session_state.targets_dict_recent = database.load_macro_goals(st.session_state.selected_user)
# 6. (Max Values)Initialize max value keys in session_stat  e
for x,y in st.session_state.targets_dict_recent.items():

    utils.simple_initializer(x,y)
# 7. (Log Food) Initialize datetime, used for the input buttons
utils.simple_initializer(
    name="datetime", 
    initial_value=datetime.datetime.now(LOCAL_TZ)
)
# 8. Initialize the data used for the plot called 'for_plot_df'
utils.simple_initializer(
    name ='for_plot_df', 
    initial_value = st.session_state.food_df[st.session_state.food_df['date']==datetime.datetime.now(LOCAL_TZ).date()]
)
# 9. Initialize pill key
utils.simple_initializer(
    name = 'pill_key',
    initial_value = None
)
# 10. Initialize edit values:
     # Input fields, excluding datetime but with date time
for x in hashmap.inputs_config.values():
    utils.simple_initializer(name = x["norm"], initial_value = x["initial"])
# 11. This is for the segment control at the top cannot have a None value
utils.simple_initializer('donut_view_forcer', 'Day')
# 12. This is to initialize the donut_view so the UI uses an existing data
utils.simple_initializer('donut_view', 'Day')
# 13. Initialize date_range
utils.simple_initializer('date_range',(datetime.datetime.now(LOCAL_TZ).date()-datetime.timedelta(days=7),datetime.datetime.now(LOCAL_TZ).date())) 
### END INITIALIZATION ###
# 14. variable for the last selected date
utils.simple_initializer('selected_date', datetime.datetime.now(LOCAL_TZ).date())
# 15. Donut memory to allow none
utils.simple_initializer('donut_memory', 'Day')
### BEGIN SIDEBAR UI ###
# 1. username selector
with st.sidebar:
    st.selectbox(
        label = "Select User",
        options = ["Sexy Ano", "Sexy Theo", "Guest"],
        key = "selected_user",
        on_change = utils.username_change_reset
    )
# 2. Setting maximum
    if st.button("Set Max Target"):
         components.open_set_max()
### END SIDEBAR UI ###

### BEGIN MAIN UI ###
# 1. Segmented Control for donut view
donut_view_mode = st.segmented_control(
    label = "",
    label_visibility = 'collapsed',
    options = ['Day', 'Average'],
    key = 'donut_view',
    width = 'stretch',
    selection_mode = 'single',
    on_change = utils.donut_store_memory,
    default = 'Day'
)
# FORCE THE USER TO ALWAYS HAVE A CHOICE
# 2.1 The for_plot_df use date range when turned to average
utils.segment_donut_change(st.session_state.date_range,st.session_state.food_df)
# 2.2 The for_plot_df use the last saved date when turned to date
# 2. Draw the plotly bars
st.plotly_chart(
    visuals.donut_progress_bars(st.session_state.for_plot_df), 
    width='stretch', 
    key="main_donut_chart",
    config={'displayModeBar': False,}
)
# 3. Draw Date range selector
selected_date_range = date_range_picker(
    title = utils.donut_label(),
    key = "date_range",
    default_start = (datetime.datetime.now(LOCAL_TZ).date()-datetime.timedelta(days=7)),
    default_end = datetime.datetime.now(LOCAL_TZ).date()  
    )
# 4. Draw food cards:
components.draw_date_range(st.session_state.date_range, st.session_state.food_df)
### END MAIN UI ###

### INPUT FIELD UI ###
# 1. Floating action button
button_clicked = floating_button(
    label="🍽️ Add Food"
)
if button_clicked:
    utils.reset_input_field()
    components.food_input_dialog() # Opens the @st.dialog window

