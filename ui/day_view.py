### IMPORTS ###
# Third Party
import streamlit as st
import datetime 
from streamlit_extras.floating_button import floating_button
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo
# In-app
from src import *
def day_view():
    # 1. Floating action button
    button_clicked = floating_button(
        label="🍽️ Add Food"
    )
    if button_clicked:
        components.food_input_dialog()

    # 2. Draw the plotly donuts
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
    # 3. Draw food cards:
    date_range = (datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()-datetime.timedelta(days=30),datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()+datetime.timedelta(days=365*100))
    components.draw_date_range(date_range, st.session_state.food_data)
    ### END MAIN UI ###

   