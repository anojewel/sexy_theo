import streamlit as st
import datetime 
from streamlit_extras.floating_button import floating_button
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo

from src import visuals
from src import database as db
from src import utils
from src import macro_models as mm

@st.dialog("➕ New Food")
def open():
    # Z. Draw donuts or show warning if no goals exist
    utils.initialize('new_macros_val', mm.MacroVal(0.0,0.0,0.0,0.0))
    utils.initialize('new_datetime', datetime.datetime.now(ZoneInfo('Asia/Taipei')))

    if 'bucket_values' in st.session_state:
        # For plotly to use the chosen date
        food_df = st.session_state.food_data.df()
        same_date_df = food_df[food_df['date']==st.session_state.new_datetime.date()]
        st.session_state.sum_same_date = same_date_df[[x.key for x in mm.macro_ui_rules]].sum()
        st.plotly_chart(
            visuals.donut_progress_bars(
            water_values=st.session_state.sum_same_date,
            oil_values=st.session_state.new_macros_val.dict(),
            bucket_values=st.session_state.bucket_values
            ),
            width='stretch'
        )   
        
    else:
        # Friendly message for new users!
        st.info("No goals set yet! Set your daily macro goals to see your progress rings here.",icon="🎯")

    # A. Let user fill food name 
    utils.initialize('new_food_name','')
    st.text_input(
        label="Food Name", 
        key="new_food_name"
    )
    
    # B. Let user fill datetime
    st.datetime_input(
        label="Date & Time",    
        key="new_datetime",
        label_visibility="collapsed",
    )
    
    # C. Draw the input fields (Key perfectly matches now!)
    utils.macros_input_field(mm.MacroVal(0.0,0.0,0.0,0.0), 'new_macros_val')
    
    # D. Log button & Clear button actions
    def save_action():
        food_draft = mm.FoodLog(
            food_name=st.session_state.new_food_name,
            macros=st.session_state.new_macros_val,
            date=st.session_state.new_datetime.date(),
            time=st.session_state.new_datetime.time(),
            username=st.session_state.selected_user,
            eat_status=True if st.session_state.new_datetime.date() <= datetime.datetime.now(ZoneInfo('Asia/Taipei')).date() else False
        )
        db.save_food(food_draft, st.session_state.food_data)
        
        # Clear database cache and reset form inputs for the next open
        utils.state_del([
            'new_food_name', 'new_datetime', 'new_macros_val','bucket_values'
        ])
        st.rerun()

    def clear_action():
        # Deleting these keys lets your utils.initialize() functions reset them to defaults automatically
        utils.state_del([
            'new_food_name', 'new_datetime', 'new_macros_val'
        ])  
        st.rerun(scope='fragment')
        
    # D1. Draw the pills
    utils.pill_buttons(
        actions={
            "➕ Log Food": save_action,
            "🧹 Clear": clear_action
        },
        key="input_pill_key"
    )
        
    st.button("Ingredient Mode", width='stretch', icon="🥣")