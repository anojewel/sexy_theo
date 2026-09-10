import streamlit as st
from streamlit_extras.floating_button import floating_button
from streamlit_extras.mandatory_date_range import *

# Self
from src import db, lmn, mm, utils
import ui

class GoalCards:
    @staticmethod
    def single_goal_card(goals_log: mm.GoalsLog, food_data):
        # 1. Group true macros by date using a dictionary
        daily_totals = {}
        
        for food in food_data.list():
            if goals_log.start_date <= food.date <= goals_log.end_date:
                # Calculate true macros (base or ingredients based on is_simple flag)
                true_macros = food.true_macroval(
                    st.session_state.ingredients_list, 
                    st.session_state.recipe_list
                )
                
                # Add to that specific date's total
                if food.date not in daily_totals:
                    daily_totals[food.date] = true_macros
                else:
                    daily_totals[food.date] = daily_totals[food.date] + true_macros

        # 2. Calculate the averages across the active days
        num_days = len(daily_totals)
        avg_series = {key: 0.0 for key in ['calories', 'carbs', 'protein', 'fat']}
        
        if num_days > 0:
            for date_key, daily_macro in daily_totals.items():
                for x in mm.macro_ui_rules:
                    avg_series[x.key] += getattr(daily_macro, x.key)
                    
            for key in avg_series:
                avg_series[key] = round(avg_series[key] / num_days, 1)

        # Line 1 string
        line_1 = f"**{goals_log.start_date.day} {goals_log.start_date:%B %Y} ~ {goals_log.end_date.day} {goals_log.end_date:%B %Y}**"
        
        # Line 2 string
        line_2 = "🎯: "
        for x in mm.macro_ui_rules:
            line_2 += f"{x.emoji} {getattr(goals_log.macros, x.key)} {x.unit}  "
            
        # Line 3 string
        line_3 = "📊: "
        for x in mm.macro_ui_rules:
            line_3 += f"{x.emoji} {avg_series[x.key]} {x.unit}  "
                
        button_label = f"{line_1}\n\n{line_2}\n\n{line_3}"
        
        # B. Draw the cards:
        if st.button(
            label=button_label,
            width='stretch',
            key=f"goal_card_button_{str(goals_log.id)}"
        ):
            ui.edit_goals.open(goals_log)
# 1. Username selector package:
lmn.username_selector()

# 2. Iniitalize the database form supabase
db.initialize(st.session_state.selected_user)

### 1 ###
# Segment Selector for time range WITH MEMORY
utils.initialize('goal_view_mode_memo', 'Week')
st.segmented_control(
    label='',
    label_visibility='collapsed',
    options=['Day', 'Week', 'Month', 'Year', 'Custom'],
    key='goal_view_mode_raw',
    width='stretch'
)

# Commit selection to memory if it isn't None
if st.session_state.goal_view_mode_raw is not None:
    st.session_state.goal_view_mode_memo = st.session_state.goal_view_mode_raw

# Lock in the active view mode
active_view_mode = st.session_state.goal_view_mode_memo

### 2 ###
# Floating action button
button_clicked = floating_button(
    label="➕ New Goal"
)
if button_clicked:
    ui.new_goal.open(active_view_mode)

### 3 ###
st.markdown(f"**{active_view_mode} Goals**")
# Goal cards draw
for x in st.session_state.goals.list():
    if x.range_type == active_view_mode:
        GoalCards.single_goal_card(x, st.session_state.food_data)