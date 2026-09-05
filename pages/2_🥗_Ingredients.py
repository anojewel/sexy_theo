import streamlit as st
from streamlit_extras.mandatory_date_range import *

# Self
from src import db, lmn
import ui


# 1. Username selector package:
lmn.username_selector()
# 2. Iniitalize the database form supabase
if 'food_data' not in st.session_state:
    st.session_state.food_data = db.FromSupabase(st.session_state.selected_user,'food_data')
if 'goals' not in st.session_state:
    st.session_state.goals = db.FromSupabase(st.session_state.selected_user,'goals')
