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
from . import visuals
from . import database as db
from . import utils
from . import macro_models as mm

# 1. Make window to let user log food
@st.dialog("➕ Log New Food")
def food_input_dialog():
    # A. Let user fill food name 
        # A Initialize:
    utils.initialize('food_name','')
        # A Draw:
    st.text_input(
        label="Food Name", 
        key="food_name",
        on_change=utils.fill_matching_data,
    )
    # B Let user fill datetime
    utils.initialize('datetime', datetime.datetime.now(ZoneInfo('Asia/Taipei')))
    st.datetime_input(
        label="Date & Time", 
        key="datetime", 
        value=st.session_state["datetime"],
        label_visibility = "collapsed",
    )
    # B.1 For plotly to use the chosen date
    food_df = st.session_state.food_data.df()
    same_date_df = food_df[food_df['date']==st.session_state.datetime.date()]
    sum_same_date = same_date_df[[x.key for x in mm.macro_ui_rules]].sum()
    # C. Make macro inputs with a loop
    for x in mm.macro_ui_rules:
        # Need to initialize becaues the calculation uses a value before the input is created
        utils.initialize(x.key, 0.0)
        # Value used inside the graphs and numbers
        current_val = sum_same_date[x.key]
        projected_val = st.session_state[x.key]
        max_val = st.session_state.bucket_values[x.key]
        # C1. The Number Input 
        st.number_input(
            label = f"{x.emoji} {x.title} ({x.unit}): " + f"{current_val:.1f}/{projected_val:.1f}" , 
            min_value=0.0, 
            step=x.step_val, 
            key=x.key,
            format="%.1f"
        )
        
        # C2. The Original Progress Bar 
        st.plotly_chart(
            visuals.figure_progress_bar(
                factor=current_val / max_val, 
                projected_factor=projected_val / max_val, 
                bar_color=f'rgba({x.rgb},0.85)', 
                projected_bar_color=f'rgba({x.rgb},0.6)',
                overflow_color=f'rgba({x.rgb},1)',
                projected_overflow_color=f'rgba({x.rgb},0.6)'
            ),
            width= "stretch",
            config={'displayModeBar': False},
            key=f"progress_chart_{x.key}"
        )

    # D. Log button & Clear button actions
    def save_action():
        macros_draft = mm.MacroVal(
            calories=st.session_state.calories,
            carbs=st.session_state.carbs,
            protein=st.session_state.protein,
            fat=st.session_state.fat
        )
        food_draft = mm.FoodLog(
            food_name=st.session_state.food_name,
            macros=macros_draft,
            date=st.session_state.datetime.date(),
            time=st.session_state.datetime.time(),
            username=st.session_state.selected_user,
            eat_status=True if st.session_state.datetime.date() <= datetime.datetime.now(ZoneInfo('Asia/Taipei')).date() else False
        )
        food_draft.save(db.conn)
        
        # Clear database cache and reset form inputs for the next open
        utils.state_del([
            'food_data', 'food_name', 'datetime', 
            'calories', 'carbs', 'protein', 'fat'
        ])
        st.rerun()

    def clear_action():
        # Deleting these keys lets your utils.initialize() functions reset them to defaults automatically
        utils.state_del([
            'food_name', 'datetime', 
            'calories', 'carbs', 'protein', 'fat'
        ])
        st.rerun()
    # D1. Draw the pills
    utils.pill_buttons(
        actions={
            "➕ Log Food": save_action,
            "🧹 Clear": clear_action
        },
        key="input_pill_key"
    )
        
    st.button("Ingredient Mode", width='stretch', icon="🥣")
# 2. Window to edit the existing logs   
def clear_dialog_states():
    keys_to_purge = ["edit_food_name", "edit_datetime", "edit_eat_status"]
    for key in keys_to_purge:
        if key in st.session_state:
            del st.session_state[key]
@st.dialog("✏️ Edit Log",  on_dismiss=clear_dialog_states)
def open_food_editor(food_log: mm.FoodLog):
    # A. Allow user to edit the food text
    st.text_input(
            label="Food Name", 
            key= "edit_food_name",
            value = food_log.food_name
        )
    # B.1 Combine date tand time
    combined_datetime = datetime.datetime.combine(food_log.date,food_log.time)
    # B.2 Allow user to edit datetime
    st.datetime_input(
        label="Date & Time", 
        key="edit_datetime", 
        value=combined_datetime,
        label_visibility = "collapsed",
    )
    # C. Allow user to edit the macro values
    for x in mm.macro_ui_rules:
        # A. The Number Input 
        st.number_input(
            label = f"{x.emoji} {x.title} ({x.unit})" , 
            min_value=0.0, 
            step=x.step_val, 
            key="edit_" + x.key,
            format="%.1f",
            value = getattr(food_log.macros, x.key)
        )
    # D. Draw toggle and buttons for saving/deleting
    st.toggle(
        label="✅ Eaten", 
        key="edit_eat_status",
        value = food_log.eat_status
    )
    # E. Define the target actions using your existing class methods
    def save_action():
        # Update the existing object's attributes with the new UI widget states
        food_log.food_name = st.session_state.edit_food_name
        food_log.date = st.session_state.edit_datetime.date()
        food_log.time = st.session_state.edit_datetime.time()
        food_log.eat_status = st.session_state.edit_eat_status
        
        food_log.macros.calories = st.session_state.edit_calories
        food_log.macros.carbs = st.session_state.edit_carbs
        food_log.macros.protein = st.session_state.edit_protein
        food_log.macros.fat = st.session_state.edit_fat

        # Call your built-in class method
        food_log.save(db.conn)
        
        # Nuke the database cache and all dialog widget states
        utils.state_del([
            'food_data', 'edit_food_name', 'edit_datetime', 'edit_eat_status',
            'edit_calories', 'edit_carbs', 'edit_protein', 'edit_fat'
        ])
        st.rerun()

    def delete_action():
        # Call your built-in class method
        food_log.delete(db.conn)
        
        # Nuke the database cache and all dialog widget states
        utils.state_del([
            'food_data', 'edit_food_name', 'edit_datetime', 'edit_eat_status',
            'edit_calories', 'edit_carbs', 'edit_protein', 'edit_fat'
        ])
        st.rerun()

    # E1. Draw the pills and pass the actions
    utils.pill_buttons(
        actions={
            "💾 Save": save_action,
            "❌ Delete": delete_action
        }, 
        key="edit_pill_key"
    )
# 3. Draw Single Food Card
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
        open_food_editor(food_log)
    
# 4. SINGLE DAY FOOD CARDS
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
        single_food_card(obj)

# 5. MULTIPLE DAYS FOOD CARDS
def draw_date_range(date_range,food_data:db.FromSupabase):
     # date lists
    date_list = [x.date for x in food_data.list() if ((date_range[0]<=x.date)&(x.date<=date_range[1]))]
    for single_date in sorted(set(date_list), reverse=True):
        draw_cards_day(single_date, food_data)
