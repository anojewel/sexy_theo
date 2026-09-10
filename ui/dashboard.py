import streamlit as st
import datetime 
import pandas as pd
from streamlit_extras.floating_button import floating_button
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo
# Self
from src import db, lmn, mm, utils
import ui

class FoodCards:
    def __init__(self):
        pass
        
    def single_food_card(food_log: mm.FoodLog):
        # A. Write the button labels
        macro_string = ""
        # Updated to true_macroval to support your new mutually exclusive toggle
        true_macros = food_log.true_macroval(st.session_state.ingredients_list, st.session_state.recipe_list)
        for x in mm.macro_ui_rules:
            macro_string += f"{x.emoji} {getattr(true_macros, x.key):.1f} {x.unit} "
            
        if food_log.eat_status == True:
            button_label = f"**{food_log.food_name}** ‎ ‎ {food_log.time:%H:%M} \n\n {macro_string}"
        else:
            button_label = f":grey[**{food_log.food_name}** ‎ ‎ {food_log.time:%H:%M}] \n\n :grey[{macro_string}]"
            
        # B. Draw the cards:
        card_button = st.button(
            label= button_label,
            width= 'stretch',
            key = f"food_card_button_{str(food_log.id)}" 
        )
        # C. Button action:
        if card_button:
            # C.1 Open the food editor
            ui.edit_food.open(food_log)
            
    def draw_cards_day(date_input,food_list):
        # Filter the same date
        same_date_list = [x for x in food_list if x.date == date_input]
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
        # Draw all the cards within that same day:
        for obj in same_date_list:
            FoodCards.single_food_card(obj)

    # 5. MULTIPLE DAYS FOOD CARDS
    def draw_date_range(date_range,food_data:db.FromSupabase):
        # This is for the date buttons from draw_cards_day, put here so it doesnt repeat too much
        utils.initialize('selected_date', datetime.datetime.now(ZoneInfo("Asia/Taipei")).date())
        # date lists
        food_list = food_data.list()
        date_list = [x.date for x in food_list if ((date_range[0]<=x.date)&(x.date<=date_range[1]))]
        for single_date in sorted(set(date_list), reverse=True):
            FoodCards.draw_cards_day(single_date, food_list)

def draw():
    # Initialize the values. These are used multiple times throughout this specific page:
    utils.initialize('selected_date', datetime.datetime.now(ZoneInfo("Asia/Taipei")).date())
    utils.initialize('selected_date_range',(datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()-datetime.timedelta(days=30),datetime.datetime.now(ZoneInfo("Asia/Taipei")).date()+datetime.timedelta(days=30)))
    
    # 1. Floating action button (moved above the math so it renders instantly)
    button_clicked = floating_button(
        label="🍽️ Add Food"
    )
    if button_clicked:
        ui.new_food.open()

    # --- THE DONUT PLACEHOLDER ---
    donut_placeholder = st.empty()
    donut_placeholder.plotly_chart(lmn.donut_skeleton(), width='stretch', config={'displayModeBar': False})

    # 2. Heavy Math Execution (Now happens while the skeleton is holding the layout open)
    st.session_state.water_values = utils.day_total(st.session_state.selected_date, True, st.session_state.food_data)
    st.session_state.oil_values = utils.day_total(st.session_state.selected_date, False, st.session_state.food_data)
    
    # 3. Overwrite the placeholder with the actual chart
    with donut_placeholder:
        try:
            st.session_state.bucket_values = utils.goal_specificity_choose(st.session_state.selected_date)
            
            st.plotly_chart(
                lmn.donut_progress_bars(
                    water_values=st.session_state.water_values,
                    oil_values=st.session_state.oil_values,
                    bucket_values=st.session_state.bucket_values
                ), 
                width='stretch', 
                config={'displayModeBar': False}
            )
        except ValueError:
            st.info(f"No active goal for {st.session_state.selected_date:%d %B %Y}. Head to the Goals tab to set your targets!", icon="🎯")
            
    # 4. Date Range Selector
    date_range_picker(title='',label_visibility='collapsed',key='selected_date_range')
    # 5. Draw food cards:
    FoodCards.draw_date_range(st.session_state.selected_date_range, st.session_state.food_data)