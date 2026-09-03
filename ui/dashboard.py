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
from src import visuals
from src import database as db
from src import utils
from src import macro_models as mm

import ui
class FoodCards:
    def __init__(self):
        pass
    def single_food_card(food_log: mm.FoodLog):
        # A. Write the button labels
        macro_string = ""
        for x in mm.macro_ui_rules:
            macro_string = macro_string + f"{x.emoji} {getattr(food_log.macros,x.key)} {x.unit} "
        if food_log.eat_status == True:
            button_label = f"**{food_log.food_name}** ‎ ‎ {food_log.time:%H:%M} \n\n {macro_string}"
        else:
            button_label = f":grey[**{food_log.food_name}** ‎ ‎ {food_log.time:%H:%M}] \n\n :grey[{macro_string}]"
        # B. Draw the cards:
        card_button = st.button(
            label= button_label,
            width= 'stretch',
            key = f"food_card_button_{str(food_log.id)}" # Adds a key id based on the row number
        )
        # C. Button action:
        if card_button:
            # C.1 Open the food editor
            ui.edit_food.open(food_log)
    def draw_cards_day(date_input,food_data:db.FromSupabase):
        # Filter the same date
        same_date_list = [x for x in food_data.list() if x.date == date_input]
        # Sort the list by oldest
        same_date_list.sort(key = lambda x: x.time)
        # Draw button that alters the selected date in the dashboard
        if st.button(
            label = f"{date_input:%d %B %Y}",
            type = 'tertiary',
            width = 'stretch',
        ):
            st.session_state.selected_date = date_input
            st.rerun()
            st.session_state.view_mode = 'Day'
        # Draw all the cards within that same day:
        for obj in same_date_list:
            FoodCards.single_food_card(obj)

    # 5. MULTIPLE DAYS FOOD CARDS
    def draw_date_range(date_range,food_data:db.FromSupabase):
        # This is for the date buttons from draw_cards_day, put here so it doesnt repeat too much
        utils.initialize('selected_date', datetime.datetime.now(ZoneInfo("Asia/Taipei")).date())
        # date lists
        date_list = [x.date for x in food_data.list() if ((date_range[0]<=x.date)&(x.date<=date_range[1]))]
        for single_date in sorted(set(date_list), reverse=True):
            FoodCards.draw_cards_day(single_date, food_data)

def draw():
    # Initialize the values. These are used multiple times throughout this specific page:
    utils.initialize('selected_date', datetime.datetime.now(ZoneInfo("Asia/Taipei")).date())
    utils.initialize('selected_date_range',(datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()-datetime.timedelta(days=30),datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()+datetime.timedelta(days=30)))
    st.session_state.water_values = utils.day_total(st.session_state.selected_date, True, st.session_state.food_data)
    st.session_state.oil_values = utils.day_total(st.session_state.selected_date, False, st.session_state.food_data)
    
    # 1. Floating action button
    button_clicked = floating_button(
        label="🍽️ Add Food"
    )
    if button_clicked:
        ui.new_food.open()

    # 2. Try to draw the plotly donuts
    try:
        utils.initialize('bucket_values', utils.initial_bucket_filter())
        
        st.plotly_chart(
            visuals.donut_progress_bars(
                water_values=st.session_state.water_values,
                oil_values=st.session_state.oil_values,
                bucket_values=st.session_state.bucket_values
            ), 
            width='stretch', 
            key="main_donut_chart",
            config={'displayModeBar': False}
        )
    except ValueError:
        st.info("No active goal for today. Head to the Goals tab to set your targets!", icon="🎯")
    # 3. Date Range Selector
    date_range_picker(title='',label_visibility='collapsed',key='selected_date_range')
    # 4. Draw food cards:
    FoodCards.draw_date_range(st.session_state.selected_date_range, st.session_state.food_data)
    ### END MAIN UI ###

   