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
# In-app
from src import *

def day_view():
    ### INPUT FIELD UI ###
    # 1. Floating action button
    button_clicked = floating_button(
        label="🍽️ Add Food"
    )
    if button_clicked:
        utils.reset_input_field()
        components.food_input_dialog() # Opens the @st.dialog window

    # 1. Draw the plotly donuts
    st.plotly_chart(
        visuals.donut_progress_bars(
            water_values=st.session_state.water_values,
            oil_values=st.session_state.oil_values,
            bucket_values=st.session_state.bucket_values
        ), 
        width='stretch', 
        key="main_donut_chart",
        config={'displayModeBar': False,}
    )
    # 2. Draw food cards:
    components.draw_date_range(st.session_state.date_range, st.session_state.food_df)
    ### END MAIN UI ###

   