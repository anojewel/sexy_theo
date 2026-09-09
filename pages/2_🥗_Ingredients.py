import streamlit as st
from streamlit_extras.mandatory_date_range import *

# Self
from src import db, lmn
import ui


# 1. Username selector package:
lmn.username_selector()
# 2. Iniitalize the database form supabase
db.initialize(st.session_state.selected_user)
