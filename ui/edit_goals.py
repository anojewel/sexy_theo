import streamlit as st
import datetime 
import calendar
from streamlit_extras.mandatory_date_range import *

from src import database as db
from src import utils
from src import macro_models as mm

@st.dialog("✏️ Edit Goal", on_dismiss=lambda: utils.state_del(["edit_goal_date", "edit_goal_macros"]))
def open(goals_log: mm.GoalsLog):
    # 1. Initialize Values
    utils.initialize('edit_goal_macros', goals_log.macros)
    
    if goals_log.range_type == 'Day':
        utils.initialize('edit_goal_date', goals_log.start_date)
    else:
        utils.initialize('edit_goal_date', (goals_log.start_date, goals_log.end_date))

    # 2. Draw Widgets
    if goals_log.range_type == 'Day':
        st.date_input(
            label="Goal Date", 
            key="edit_goal_date",
            label_visibility="collapsed"
        )
    else:
        date_range_picker(
            title='', 
            key='edit_goal_date'
        )
        
    utils.macros_input_field(goals_log.macros, 'edit_goal_macros')

    # 3. Validation Logic
    def _get_range_error(view_mode, date_tuple):
        if type(date_tuple) is not tuple: 
            return None if view_mode == 'Day' else "Please select a full date range."
            
        start, end = date_tuple
        
        if view_mode == 'Week':
            if start.weekday() != 6 or (end - start).days != 6:
                return "Date range must be exactly one calendar week (Sunday to Saturday)."
                        
        elif view_mode == 'Month':
            last_day_of_month = calendar.monthrange(start.year, start.month)[1]
            if start.day != 1 or end.day != last_day_of_month or start.month != end.month:
                return "Date range must perfectly cover one full calendar month."
                
        elif view_mode == 'Year':
            if start.month != 1 or start.day != 1 or end.month != 12 or end.day != 31 or start.year != end.year:
                return "Date range must perfectly cover one full calendar year (Jan 1 to Dec 31)."
                
        return None

    # 4. Define Actions
    def save_action():
        active_range = st.session_state.edit_goal_date
        error_msg = _get_range_error(goals_log.range_type, active_range)
        
        # Guard clause: Stop saving and show error if validation fails
        if error_msg:
            st.error(error_msg, icon="📅")
            return
            
        # Parse dates safely based on type
        if goals_log.range_type == 'Day':
            goals_log.start_date = active_range
            goals_log.end_date = active_range
        else:
            goals_log.start_date, goals_log.end_date = active_range
            
        goals_log.macros = st.session_state.edit_goal_macros
        
        db.save_goal(goals_log, st.session_state.goals)
        utils.state_del(["edit_goal_date", "edit_goal_macros", 'bucket_values'])
        st.rerun()

    def delete_action():
        db.delete_goal(goals_log, st.session_state.goals)
        utils.state_del(["edit_goal_date", "edit_goal_macros",'bucket_values'])
        st.rerun()

    # 5. Draw Action Pills
    utils.pill_buttons(
        actions={
            "💾 Save": save_action,
            "❌ Delete": delete_action
        }, 
        key="edit_goal_pill_key"
    )