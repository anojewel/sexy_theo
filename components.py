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
import utils

# 9. Floating dialog for logging food
@st.dialog("➕ Log New Food")
def food_input_dialog():
    
    st.text_input(
        label="Food Name", 
        key="food_name",
        on_change=utils.fill_matching_data,
    )
    st.datetime_input(
        label="Date & Time", 
        key="datetime", 
        value=st.session_state["datetime"],
        label_visibility = "collapsed",
    )

    # Create an pd series of the same day as the date chosen in the keys
    same_date_df = st.session_state.food_df[st.session_state.food_df['date']==st.session_state.datetime.date()]
    sum_same_date = same_date_df[[macro.lower() for macro in hashmap.macros_config]].sum()
    # Loop through the dictionary WITHOUT creating st.columns
    for macro, config in hashmap.macros_config.items():
        macro_lower = macro.lower()
        step_value = 50.0 if macro == "Calories" else 5.0

        # B. Define the variables
        current_val = sum_same_date[macro_lower]
        projected_val = st.session_state[macro_lower]
        max_val = st.session_state[config["max_key"]]

        # A. The Number Input (Occupies 1 full row)
        st.number_input(
            label = f"{config['emoji']} {macro} ({'kcal' if macro == 'Calories' else 'g'})" + f"{utils.number_if_overflow(current_val, projected_val, max_val)}" , 
            min_value=0.0, 
            step=step_value, 
            key=macro_lower,
            format="%.2f"
        )
        

        # D. The Original Progress Bar (Occupies 1 full row)
        st.plotly_chart(
            visuals.figure_progress_bar(
                factor=current_val / max_val, 
                projected_factor=projected_val / max_val, 
                bar_color=f'rgba({config['rgb']},0.85)', 
                projected_bar_color=f'rgba({config['rgb']},0.6)',
                overflow_color=f'rgba({config['rgb']},1)',
                projected_overflow_color=f'rgba({config['rgb']},0.6)'
            ),
            width= "stretch",
            config={'displayModeBar': False}
        )
    
    # 3. Bottom Row: Action buttons
    col_log, col_ingredient = st.columns(2)
    
    # Use on_click=log_food so the state clears BEFORE widgets instantiate on the next run!
    if col_log.button("Log Food", icon = "➕", on_click=database.log_food, width = 'stretch' , type="primary"):
        st.rerun() # Closes the dialog
        
    col_ingredient.button("Ingredient Mode", width='stretch', icon = "🥣")
# 10 Dialog for setting maximum target
@st.dialog("Set Maximum Target")
def open_set_max():
    for x, y in hashmap.macros_config.items():
        st.number_input(label = x, width = 100, value = st.session_state[y["max_key"]], key = y["max_key"])
    st.button(
        label = "Save", 
        on_click = database.save_max,
        disabled = any(st.session_state[x["max_key"]] == 0 for x in hashmap.macros_config.values())
        )
# 15. The editing ui    
@st.dialog("✏️ Edit Log")
def open_food_editor(row):
    #Initialize edit_eat_status if it doesnt exist
    utils.simple_initializer(
        name = 'edit_eat_status',
        initial_value = row['eat_status']
    )
    # 1. Draw Text Input
    st.text_input(
            label="Food Name", 
            key= "edit_food_name",
            value = row['food_name']
        )
    # 2. Combine date tand time
    combined_datetime = datetime.datetime.combine(row['date'], row['time'])
    # 3. Draw the datetime
    st.datetime_input(
        label="Date & Time", 
        key="edit_datetime", 
        value=combined_datetime,
        label_visibility = "collapsed",
    )
    # 3. Loop through hashmap.macros_config
    for macro, config in hashmap.macros_config.items():
        macro_lower = macro.lower()
        step_value = 50.0 if macro == "Calories" else 5.0
        # A. The Number Input 
        st.number_input(
            label = f"{config['emoji']} {macro} ({'kcal' if macro == 'Calories' else 'g'})" , 
            min_value=0.0, 
            step=step_value, 
            key="edit_" + macro_lower,
            format="%.2f",
            value = row[macro.lower()]
        )
    # 4. Draw toggle and buttons for saving/deleting
    st.toggle(
        label="✅ Eaten", 
        key="edit_eat_status"
    )
    
    # 5. Draw buttons for saving and deleting, 
    st.pills(
        label = "", 
        label_visibility= "collapsed",
        options = ["💾 Save", "❌ Delete"],
        key = "pill_key"
    )
    clicked_pill = st.session_state.pill_key
    if clicked_pill == "💾 Save":
        database.save_edit(row)
        st.rerun() # to exit to main page
    elif clicked_pill == "❌ Delete":
        database.delete_selected_food(row)
        st.rerun()

        # function that changes the eatn value of said id to false
# 16. (Single food card)
def single_food_card(row):
    macro_string = ""
    for macro, config in hashmap.macros_config.items():
        macro_string = macro_string + f"{config['emoji']} {row[macro.lower()]} {config['unit']} "
    # Draw the cards:
    card_button = st.button(
        label = f"**{row['food_name']}** ‎ ‎ {row['time']:%H:%M} \n\n {macro_string}" if row['eat_status'] == True else f":grey[**{row['food_name']}** ‎ ‎ {row['time']:%H:%M} \n{macro_string}]",
        width= 'stretch',
        key = f"food_card_button_{str(row['id'])}" # Adds a key id based on the row number
    )
    if card_button:
        # Change the edit keys in the session state to the buttons in question
        input_list = [x['norm'] for x in hashmap.inputs_config.values()] +['eat_status']
        for input_name in input_list:
            st.session_state['edit_'+ input_name] = row[input_name]
        # Assign the datetime because its weid:
        combine_datetime = datetime.datetime.combine(row['date'],row['time'])
        st.session_state['edit_datetime'] = combine_datetime 
        open_food_editor(row)
    
# 17. DRAW FOOD CARDS IN ONE DAY
def draw_cards_day(date_input,food_df):
    # Filter out data with the same date
    same_date_df = food_df[food_df['date']==date_input] 
    # Draw button for ASSIGN DATE RANGE TO PLOT
    date_button = st.button(
        label = f"{date_input:%d %B %Y}",
        type = 'tertiary',
        width = 'stretch',
        on_click = utils.donut_view_to_date
    )
    # ASSIGN DATE RANGE TO PLOT function
    if date_button:
        st.session_state.for_plot_df = same_date_df
        st.session_state.selected_date = date_input
        st.rerun()
    # Draw all the cards within that same day:
    for index, row in same_date_df.iterrows():
        single_food_card(row)
# 18. DRAW DAYS OF A CERTAIN RANGE
def draw_date_range(date_range,food_df):
    filtered_dates = food_df[food_df['date'].between(date_range[0],date_range[1])]['date'].unique()
    for single_date in sorted(filtered_dates, reverse=True):
        draw_cards_day(single_date, food_df)