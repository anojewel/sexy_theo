import streamlit as st
import datetime 
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import calendar
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

@st.dialog("➕ New Goal")
def open(view_mode):
    ### 1. Initializer script for the time_input field ###
    tz = ZoneInfo('Asia/Taipei')
    today = datetime.datetime.now(tz).date()

    # Calculate current week bounds (Monday to Sunday)
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)

    # Calculate current month bounds
    start_of_month = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_of_month = today.replace(day=last_day)

    # Calculate current year bounds
    start_of_year = datetime.date(today.year, 1, 1)
    end_of_year = datetime.date(today.year, 12, 31)

    # Initialize keys specifically for date tuples (except Day)
    utils.initialize('new_goal_day', today)
    utils.initialize('new_goal_week', (start_of_week, end_of_week))
    utils.initialize('new_goal_month', (start_of_month, end_of_month))
    utils.initialize('new_goal_year', (start_of_year, end_of_year))
    utils.initialize('new_goal_custom', (today, today))
    
    ### 2. Draw time_input field with dependency ###
    if view_mode == 'Day':
        st.date_input(label='', label_visibility='collapsed', key='new_goal_day')
    elif view_mode == 'Week':
        date_range_picker(title='', key='new_goal_week')
    elif view_mode == 'Month':
        date_range_picker(title='', key='new_goal_month')
    elif view_mode == 'Year':
        date_range_picker(title='', key='new_goal_year')
    elif view_mode == 'Custom':
        date_range_picker(title='', key='new_goal_custom')
        
    ### 3. MacroVal input fields ###
    utils.macros_input_field(mm.MacroVal(1700,220,100,55), 'new_goal_macros',show_macroval=True)
    
    ### 4. Time input processing & Validation Definitions ###
    time_key_map = {
        'Day': 'new_goal_day',
        'Week': 'new_goal_week',
        'Month': 'new_goal_month',
        'Year': 'new_goal_year',
        'Custom': 'new_goal_custom'
    }
    
    active_time_key = time_key_map[view_mode]
    active_range = st.session_state[active_time_key]

    def _get_range_error(view_mode, date_tuple):
        # Date picker single-day returns a single date, range picker returns a tuple
        if type(date_tuple) is not tuple: 
            return None if view_mode == 'Day' else "Please select a full date range."
            
        start, end = date_tuple
        
        if view_mode == 'Week':
            # Must start on Monday (0) and be exactly 6 days apart
            if start.weekday() != 0 or (end - start).days != 6:
                return "Date range must be exactly one calendar week (Monday to Sunday)."        
        elif view_mode == 'Month':
            # Must start on day 1 and end on the final day of the same month
            last_day_of_month = calendar.monthrange(start.year, start.month)[1]
            if start.day != 1 or end.day != last_day_of_month or start.month != end.month:
                return "Date range must perfectly cover one full calendar month."
                
        elif view_mode == 'Year':
            # Must start Jan 1 and end Dec 31 of the same year
            if start.month != 1 or start.day != 1 or end.month != 12 or end.day != 31 or start.year != end.year:
                return "Date range must perfectly cover one full calendar year (Jan 1 to Dec 31)."
                
        return None 

    ### 5. Action Definitions ###
    def _save_new_goal():
        error_msg = _get_range_error(view_mode, active_range)
        
        # Guard clause: Stop saving and show error if validation fails
        if error_msg:
            st.error(error_msg, icon="📅")
            return
            
        # Parse start and end dates based on view_mode output type
        if view_mode == 'Day':
            start_val = active_range
            end_val = active_range
        else:
            start_val, end_val = active_range

        # DB action (Reverting back to start_date and end_date)
        payload_goal = mm.GoalsLog(
            username=st.session_state.selected_user,
            range_type=view_mode,
            start_date=start_val,
            end_date=end_val,
            macros=st.session_state.new_goal_macros,
        )
        db.save_goal(payload_goal, st.session_state.goals)
        
        # Clean up widget states upon saving, then close dialog
        utils.state_del([active_time_key, 'new_goal_macros'])
        st.rerun()
    def _clear_new_goal():
        utils.state_del([active_time_key, 'new_goal_macros'])
        st.rerun(scope='fragment')

    ### 6. Draw the Action Pills ###
    
    utils.pill_buttons(
        actions={
            "💾 Save": _save_new_goal,
            "🗑️ Clear": _clear_new_goal
        },
        key="new_goal_action_pills"
    )