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
from . import hashmap
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
            label = f"{x.emoji} {x.title} ({x.unit})" + f"{current_val}/{projected_val}" , 
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
            config={'displayModeBar': False}
        )

    # D. Log button
    # D.1. Create FoodLog item from the session state inputs
    macros_draft = mm.MacroVal(
        calories = st.session_state.calories,
        carbs = st.session_state.carbs,
        protein = st.session_state.protein,
        fat = st.session_state.fat
    )
    food_draft = mm.FoodLog(
        food_name= st.session_state.food_name,
        macros = macros_draft,
        date = st.session_state.datetime.date(),
        time = st.session_state.datetime.time(),
        username = st.session_state.selected_user,
        eat_status = True if st.session_state.datetime.date() <= datetime.datetime.now(ZoneInfo('Asia/Taipei')).date() else False
    )
    # 
    if st.button("Log Food",icon="➕",width='stretch',type="primary"):
        food_draft.save(db.conn)
        del st.session_state.food_data
        st.rerun() 
        
    st.button("Ingredient Mode",width='stretch',icon = "🥣")

# 2. Make window for user to set goals and max (WORKING)
@st.dialog("Set Maximum Target")
def open_set_max():
    for x, y in hashmap.macros_config.items():
        st.number_input(label = x, width = 100, value = st.session_state[y["max_key"]], key = y["max_key"])
    st.button(
        label = "Save", 
        on_click = db.save_max,
        disabled = any(st.session_state[x["max_key"]] == 0 for x in hashmap.macros_config.values())
        )
# 3. Window to edit the existing logs   
@st.dialog("✏️ Edit Log")
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
    # E.buttons for saving and deleting, 
        # Initialize
    utils.initialize('pill_key',None)
    st.pills(
        label = "", 
        label_visibility= "collapsed",
        options = ["💾 Save", "❌ Delete"],
        key = "pill_key"
    )
    # E1. Mechanics for each button to do shit
    clicked_pill = st.session_state.pill_key
    if clicked_pill == "💾 Save":
        macros_draft = mm.MacroVal(
            calories= st.session_state.edit_calories,
            carbs= st.session_state.edit_carbs,
            protein= st.session_state.edit_protein,
            fat= st.session_state.edit_fat
        )
        food_draft = mm.FoodLog(
            food_name = st.session_state.edit_food_name,
            macros = macros_draft,
            date = st.session_state.edit_datetime.date(),
            time = st.session_state.edit_datetime.time(),
            username = st.session_state.selected_user,
            eat_status= st.session_state.edit_eat_status,
            id = food_log.id
        )
        food_draft.save(db.conn)
        del st.session_state.food_data
        st.rerun() # to exit to main page
    elif clicked_pill == "❌ Delete":
        food_log.delete(db.conn)
        del st.session_state.food_data
        st.rerun()
# 4. Draw Single Food Card
def single_food_card(food_log: mm.FoodLog):
    # A. Write the button labels
    macro_string = ""
    for x in mm.macro_ui_rules:
        macro_string = macro_string + f"{x.emoji} {getattr(food_log.macros,x.key)} {x.unit} "
    # B. Draw the cards:
    card_button = st.button(
        label= f"**{food_log.food_name}** ‎ ‎ {food_log.time:%H:%M} \n\n {macro_string}" if food_log.eat_status == True else f":grey[**{food_log.food_name}** ‎ ‎ {food_log.time:%H:%M} \n\n {macro_string}]",
        width= 'stretch',
        key = f"food_card_button_{str(food_log.id)}" # Adds a key id based on the row number
    )
    # C. Button action:
    if card_button:
        # C.1 Open the food editor
        open_food_editor(food_log)
    
# 5. SINGLE DAY FOOD CARDS
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

# 6. MULTIPLE DAYS FOOD CARDS
def draw_date_range(date_range,food_data:db.FromSupabase):
     # date lists
    date_list = [x.date for x in food_data.list() if ((date_range[0]<=x.date)&(x.date<=date_range[1]))]
    for single_date in sorted(set(date_list), reverse=True):
        draw_cards_day(single_date, food_data)
