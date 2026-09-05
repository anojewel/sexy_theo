import streamlit as st
import datetime 
from streamlit_extras.mandatory_date_range import *
# Self
from src import db, lmn, mm, utils

@st.dialog("✏️ Edit Log", on_dismiss = lambda: utils.state_del(["edit_food_name", "edit_datetime", "edit_eat_status",'edit_macros_value']))
def open(food_log: mm.FoodLog):
    # Initialize the input values here
    utils.initialize('edit_food_name', food_log.food_name)
    utils.initialize('edit_datetime', datetime.datetime.combine(food_log.date,food_log.time))
    utils.initialize('edit_eat_status', food_log.eat_status)

    # A. Allow user to edit the food text
    lmn.food_name_select(st.session_state.food_data, 'edit_food_name', 'edit_macros_value')
    # B.2 Allow user to edit datetime
    st.datetime_input(
        label="Date & Time", 
        key="edit_datetime", 
        label_visibility = "collapsed",
    )
    # C. Allow user to edit the macro values
    lmn.macros_input_field(food_log.macros, 'edit_macros_value', show_macroval=True)
    # D. Draw a button toggle for the eat status
    # 1. 
    if st.session_state.edit_eat_status == True:
        if st.button("✅ Eaten",width='stretch'):
            st.session_state.edit_eat_status = False
            st.rerun(scope='fragment')
    elif st.session_state.edit_eat_status == False:
        if st.button("⬜ Eaten",width='stretch'):
            st.session_state.edit_eat_status = True
            st.rerun(scope='fragment')

    # E. Define the target actions using your existing class methods
    def save_action():
        # Update the existing object's attributes with the new UI widget states
        food_log.food_name = st.session_state.edit_food_name
        food_log.date = st.session_state.edit_datetime.date()
        food_log.time = st.session_state.edit_datetime.time()
        food_log.macros = st.session_state.edit_macros_value
        food_log.eat_status = st.session_state.edit_eat_status
        
        db.save_food(food_log,st.session_state.food_data)
        
        # Nuke the database cache and all dialog widget states
        utils.state_del([
            'edit_food_name', 'edit_datetime', 'edit_eat_status','edit_macros_value'
        ])
        st.rerun()

    def delete_action():
        # Call your built-in class method
        db.delete_food(food_log,st.session_state.food_data)
        
        # Nuke the database cache and all dialog widget states
        utils.state_del([
            'food_data', 'edit_food_name', 'edit_datetime', 'edit_eat_status','edit_macros_value'
        ])
        st.rerun()

    # E1. Draw the pills and pass the actions
    lmn.pill_buttons(
        actions={
            "💾 Save": save_action,
            "❌ Delete": delete_action
        }, 
        key="edit_pill_key"
    )