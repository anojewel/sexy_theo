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
from src import db, lmn, mm, utils
import ui


# 1. Username selector package:
lmn.username_selector()
# 2. Iniitalize the database form supabase
if 'food_data' not in st.session_state:
    st.session_state.food_data = db.FromSupabase(st.session_state.selected_user,'food_data')
if 'goals' not in st.session_state:
    st.session_state.goals = db.FromSupabase(st.session_state.selected_user,'goals')
