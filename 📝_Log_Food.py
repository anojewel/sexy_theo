# Note for AI:
# This is my project for learning python from scratch by making a streamlit app for tracking calories for my grilfriend
# I'd prefer to learn to be given what syntax for what instead of giving me the whole block of code to copy paste. If it's tedious or necessary please tell me why copy pasting is preferrable in certain scenario. Also, i'd like to learn concepts since I am new at coding.
# Learning Logs
# Day 1: 
# Learned streamlit UI, setting up virtual environments, random ugly code
# Day 2: 
# Python keywords and bullshits jargon learning i keep fucking up
# Day 3: 
# Realized streamlit reruns every sinlge click, so use session state
# Day 4: 
# Realized streamlit doesnt save data, spent the whole day trying to connect to google sheets, managing keys.
# Day 5: 
# Created the visual data frame table that you can add from table input
# Day 6: 
# Created the visual progress bars using plotly, first time making use of defining my own function.
# Created the date filter table that only views the selected date
# Day 7: 
# Realized that using a save button is faster and saves amount of data transferred to database, spent a lot of time making a save button functional
# Also made a highlight feature of the stuff that is not saved.
# Day 8:
# Rearrange code script tidiness, and order.
# Realized a lot of the data is repeating, so implement DRY code, using loops to do stuff for me.
# Doing the above needs me to understand what is a list, tuple, and pandas series.
# Day 9:
# Finished replacing repeating code to a dry one.
# Day 10:
# Switching from gsheets to supabase
# Day 11:
# Bugfixing the switch to supabase
# Added a user selector
# Added interactive data_editor 
# Day 12:
# bug fix the data_editor.understand how it controls data
# Day 13:
# data_editor connect with bar
# Added bottom container, discovered streamlit extras
# Deploy for the first time 
# Day 14:
# Mobile ui restricts one element on 1 row, need UI overhaul
# Uses st.dialog and popovers and st.segment thing for single row butotns.
# Bugfixing the save stuff 
# NEW DONUT PLOTLY GRAPHS YIIPPE
# Chagne date and time inputs into one single datetime input
# Made it private in streamlit only though
# Day 15
# Change save button/main database table into pillbox per item mode
# Added eat status and its functions
# Day 16 
# added all the buttons and their functions correctly
# save delete eat status functions aare added and bugfixxed
# Day 17
# Change to date range picker and their functions
# Change food data filtering
# Added a average view mode and day view mode THIS IS UNEXPECTED SO MUCH WORK
# Plans:
# update the name matcher using FUZZY SEARCH DIFFLIB
# implement a week button inside food_card_day that ends with week 2 and so on, use a pillbox 
# Pressing the week button should change the donut to display that week's average
# use css to make the donuts floating?????
# specialized input streamlit extras search?????
# Persist account selection per last use? Is it possible
# Bugs:
# Edit dialogues open and only show the data of the data first pressed
# Changing eating status doesnt show directly in the food cards
### IMPORTS ###
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
### BEGIN CONFIGURATION ###
st.set_page_config(
    page_title= "💋 Baby Tracker",
    layout="centered", 
    initial_sidebar_state="collapsed",
)
# KIll reszie handle on plotly
st.markdown("""
    <style>
    /* Completely disable the drag-to-resize handle on all data_editors */
    [data-testid="stDataFrameResizable"] {
        resize: none !important;
    }
    </style>
""", unsafe_allow_html=True)
# for fucking up timezones
LOCAL_TZ = ZoneInfo("Asia/Taipei")

### END CONFIGURATION ###
### BEGIN INDEP DICTIONARY ###
# 1. Macro Configuration Dictionary
# Combines: macro_str_list, max_str_list, initial_max_list, bar_color_primary, bar_color_secondary
macros_config = {
    "Calories": {
        "max_key": "max_cal", 
        "max_val": 2500, 
        "color_primary": "#FF6F61", 
        "color_secondary": "#FFB6B3",
        "color_overflow" : "#661B16",
        "color_overflow2" : "#972820",
        "emoji": "🔥",
        "unit" : "kcal"
    },
    "Carbs": {
        "max_key": "max_carbs", 
        "max_val": 300,  
        "color_primary": "#6A5ACD", 
        "color_secondary": "#B0C4DE",
        "color_overflow": "#282054",
        "color_overflow2" : "#423589",
        "emoji": "🍞",
        "unit" : "g"
    },
    "Protein": {
        "max_key": "max_protein", 
        "max_val": 100,  
        "color_primary": "#3CB371", 
        "color_secondary": "#90EE90",
        "color_overflow": "#113C21",
        "color_overflow2" : "#1A5831",
        "emoji": "🥩",
        "unit" : "g"
    },
    "Fat": {
        "max_key": "max_fat", 
        "max_val": 75,   
        "color_primary": "#FFA500", 
        "color_secondary": "#FFDAB9",
        "color_overflow": "#3F2001",
        "color_overflow2" : "#6D3700",
        "emoji": "🧈",
        "unit" : "g"
    }
}

# 2. Input Fields Dictionary
# Combines: input_str_list, input_str_list_norm, input_initial_values
inputs_config = {
    "Food":     {"norm": "food_name", "initial": ""},
    "Calories": {"norm": "calories",  "initial": 0.0},
    "Carbs":    {"norm": "carbs",     "initial": 0.0},
    "Protein":  {"norm": "protein",   "initial": 0.0},
    "Fat":      {"norm": "fat",       "initial": 0.0},
    "Time":     {"norm": "time",      "initial":  datetime.datetime.now(LOCAL_TZ).time()},
    "Date":     {"norm": "date",      "initial":  datetime.datetime.now(LOCAL_TZ).date()}
}
### END INDEP DICTIONARIES ###
### BEGIN DEFINITIONS ###
# 1. Load food data from backend
@st.cache_data
def load_food_data(username_input):
    # Assign variable to the food_data table that has equal user name values
    response = conn.table("food_data").select("*").eq("username", username_input).execute()
    # List of appropriate column names:
    column_name = [x["norm"] for x in inputs_config.values()] + ["id"] + ["username"] + ["eat_status"] #<-- add the id column
    # Check if the table is empty
    if not response.data:
        return pd.DataFrame(columns = column_name)
    food_df = (
    pd.DataFrame(response.data)
    .assign(
        date=lambda df: pd.to_datetime(df["date"]).dt.date,
        time=lambda df: pd.to_datetime(df["time"]).dt.time,
    ))
    return food_df[column_name]


# 2. Load maximum values from backend
@st.cache_data
def load_macro_goals(username_input):
    column_name = ", ".join([x["max_key"] for x in macros_config.values()])
    response = (conn.table("macro_goals")
                .select(column_name)
                .order("created_at", desc=True)
                .eq("username", username_input)   
                .execute()
                )
    
    # We want to initialize the loading if it's empty.
    if not response.data:
        return {
            x["max_key"]:x["max_val"] for x in macros_config.values()
        }
    else:
        return response.data[0]

# 3. Log food function for the log food button
def log_food():
    sync_datetime_to_split_keys('datetime','date','time')
    valid_input = st.session_state.food_name and all(st.session_state[x.lower()]>= 0 for x in macros_config)
    # Check if fields are empty, zero values are accepted, name is mandatory.
    if valid_input:
        # Put the stuff in input field into payload
        payload={
            config["norm"]:st.session_state[config["norm"]] for config in inputs_config.values()
        }
        # Mark the username into the payload
        payload["username"] = st.session_state.selected_user
        # Mark the eating status based on before/after
        payload["eat_status"] = (True if st.session_state.datetime.replace(tzinfo = LOCAL_TZ) <= datetime.datetime.now(LOCAL_TZ) else False)
        # Change the datetime value in the payload (AFTER PUSHING TO FOOD DF) to strinsg
        payload["date"] = payload["date"].isoformat()
        payload["time"] = payload["time"].isoformat()
        # Delete the id column before pushing to supabase
        # PUSH THE DATA TO SUPABASE
        conn.table("food_data").insert(payload).execute()
        # Clear input fields after adding ingredient
        for x in inputs_config.values():
                st.session_state[x["norm"]] = x["initial"]
        # MANUALLY clear the new UI-only datetime widget
        st.session_state["datetime"] = datetime.datetime.now(LOCAL_TZ)
        # Rerun the whoel script
        #Clear cache
        st.cache_data.clear()
        st.session_state.food_df = load_food_data(st.session_state.selected_user)
        
    else:
        st.error("Please fill in all fields with valid values.")
    

# 4. Saving max button action definition:
def save_max():
    # Define the dictionary payload as the data from session_state
    payload = {x["max_key"] : st.session_state[x["max_key"]] for x in macros_config.values()}
    payload["username"] = st.session_state.selected_user
    # Push to database
    conn.table("macro_goals").insert(payload, count=None).execute()
    # Clear cache
    st.cache_data.clear()
# 5. Plotly figures inside the input dialog
def figure_progress_bar(
        factor, 
        projected_factor, 
        bar_color, 
        projected_bar_color,
        overflow_color,
        projected_overflow_color
        ):
    # BUCKET CONCEPT HERE
    bucket = 1
    bar1 = min(factor , bucket)
    overflow1 = max(0, factor - bucket)
    # treat remaining room as a bucket
    small_bucket = min(bucket, 1-bar1)
    bar2 = min(projected_factor, small_bucket)
    overflow2 = max(0, projected_factor - small_bucket)

    data = pd.DataFrame({
        "Value": [
            bar1,
            bar2,
            overflow1,
            overflow2
            ],
        "Type": ["Current", "Projected", "Overflow", "Projected Overflow"],
        "Shelf": ["","","",""]
    })
    # Define px.bar parameters
    fig = px.bar(
                data_frame = data,
                x = "Value",
                y= "Shelf",
                color = "Type",
                orientation = "h",
                barmode = "stack",
                color_discrete_map={ 
                    "Current": bar_color, 
                    "Projected": projected_bar_color,
                    "Overflow": overflow_color,
                    "Projected Overflow": projected_overflow_color,
                    },
                range_x = [0, max(1, factor + projected_factor)], 
                text_auto = False if (factor + projected_factor) > 1 else ".1%"
            )   
    # Hide fluff
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(255,255,255,0.1)",
        height=20
    )
    # Hide fluff and lock axes
    fig.update_xaxes(visible=False, fixedrange=True) # <-- Add fixedrange=True
    fig.update_yaxes(visible=False, fixedrange=True) # <-- Add fixedrange=True

    # Add rounded corners AND explicitly enforce the auto text position
    fig.update_traces(
        marker_cornerradius=4, 
        textposition="auto",
        hoverinfo="skip",      
        hovertemplate=None     
    )
    return fig
# 6. (Name Matcher) Fills key values with most recent past data with the same name
def fill_matching_data():
    # Create filtered df with the same name as the search bar
    same_name_df = st.session_state.food_df[st.session_state.food_df["food_name"] == st.session_state.food_name]
        # Sort by new
    timesort_same_name_df = same_name_df.sort_values(
        by = ["date", "time"],
        ascending = False
    )
    if not same_name_df.empty:
    # Single row data frame of the newest same name
        newest_same_name_df = timesort_same_name_df.iloc[0]
        for macro in macros_config:
        # Dynamically update the session state
            st.session_state[macro.lower()] = newest_same_name_df[macro.lower() ]
# 7. Initializer function to initialize stuff.
def simple_initializer(name:str, initial_value):
    if name not in st.session_state:
        st.session_state[name] = initial_value
# 8. Function that reset the session_state values for the username change
def username_change_reset():
    # List the direct keys to delete
    keys_to_delete = ["food_df", "targets_dict_recent"]
    
    # Add the macro keys from your config
    for config in macros_config.values():
        keys_to_delete.append(config["max_key"])
        
    # Safely delete them only if they exist in the session state
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]

# 9. Floating dialog for logging food
@st.dialog("➕ Log New Food")
def food_input_dialog():
    
    st.text_input(
        label="Food Name", 
        key="food_name",
        on_change=fill_matching_data,
    )
    st.datetime_input(
        label="Date & Time", 
        key="datetime", 
        value=st.session_state["datetime"],
        label_visibility = "collapsed",
    )

    # Create an pd series of the same day as the date chosen in the keys
    same_date_df = st.session_state.food_df[st.session_state.food_df['date']==st.session_state.datetime.date()]
    sum_same_date = same_date_df[[macro.lower() for macro in macros_config]].sum()
    # Loop through the dictionary WITHOUT creating st.columns
    for macro, config in macros_config.items():
        macro_lower = macro.lower()
        step_value = 50.0 if macro == "Calories" else 5.0

        # B. Define the variables
        current_val = sum_same_date[macro_lower]
        projected_val = st.session_state[macro_lower]
        max_val = st.session_state[config["max_key"]]

        # A. The Number Input (Occupies 1 full row)
        st.number_input(
            label = f"{config['emoji']} {macro} ({'kcal' if macro == 'Calories' else 'g'})" + f"{number_if_overflow(current_val, projected_val, max_val)}" , 
            min_value=0.0, 
            step=step_value, 
            key=macro_lower,
            format="%.2f"
        )
        

        # D. The Original Progress Bar (Occupies 1 full row)
        st.plotly_chart(
            figure_progress_bar(
                factor=current_val / max_val, 
                projected_factor=projected_val / max_val, 
                bar_color=config["color_primary"], 
                projected_bar_color=config["color_secondary"],
                overflow_color=config["color_overflow"],
                projected_overflow_color=config["color_overflow2"]
            ),
            width= "stretch",
            config={'displayModeBar': False}
        )
    
    # 3. Bottom Row: Action buttons
    col_log, col_ingredient = st.columns(2)
    
    # Use on_click=log_food so the state clears BEFORE widgets instantiate on the next run!
    if col_log.button("Log Food", icon = "➕", on_click=log_food, use_container_width=True, type="primary"):
        st.rerun() # Closes the dialog
        
    col_ingredient.button("Ingredient Mode", use_container_width=True, icon = "🥣")
# 10 Dialog for setting maximum target
@st.dialog("Set Maximum Target")
def open_set_max():
    for x, y in macros_config.items():
        st.number_input(label = x, width = 100, value = st.session_state[y["max_key"]], key = y["max_key"])
    st.button(
        label = "Save", 
        on_click = save_max,
        disabled = any(st.session_state[x["max_key"]] == 0 for x in macros_config.values())
        )

# 11. The numbers of the charts display on top of the INPUT FIELDS labels
def number_if_overflow(current_val, projected_val, max_val):
    if current_val + projected_val > max_val:
        return f": :red[{current_val:.0f}/{max_val:.0f} | + {(current_val + projected_val - max_val):.0f} ({(current_val + projected_val - max_val) / max_val * 100:.0f}% Overflow)]"
    else:
        return f": {current_val:.0f}/{max_val:.0f} | + {projected_val:.0f}"

# 12. Used to use two keys of date and time, so have to convert the input fields into date and time in the session state.
def sync_datetime_to_split_keys(datetime_key:str, date_key:str, time_key:str):
    # Safety check (the widget can technically return None if cleared by the user)
    if st.session_state[datetime_key] is not None:
        # Push the extracted values into the existing date and time keys!
        st.session_state[date_key] = st.session_state[datetime_key].date()
        st.session_state[time_key] = st.session_state[datetime_key].time()
# 13. Donut Charts
def donut_progress_bars(for_plot_df):
    sum_series = for_plot_df[[macro.lower() for macro in macros_config]].sum()
    eaten_sum_series = for_plot_df[for_plot_df['eat_status']==True][[macro.lower() for macro in macros_config]].sum()
    not_eaten_sum_series = for_plot_df[for_plot_df['eat_status']==False][[macro.lower() for macro in macros_config]].sum()
    #If the selected range has zero food will return 0 sum and 0 length.
    # want 0 as output when this happens so take 1 as the denominator instead
    daily_average_series = sum_series/max(1,len(for_plot_df['date'].unique()))
    
    # Plotly function that make a single element room, that can put four plots in it
    fig = make_subplots(
        rows = 1,
        cols = 4,
        specs = [[ {"type" : "domain"}] * 4] # domain types are require for donuts
    )
    # The subplots have numbers assigned for each row, we need to assign them with enumerate.
    for col_index, (macro, config) in enumerate(macros_config.items(), start = 1):
        ### DATA PROCESSING ###
        if st.session_state.donut_view == 'Day' or st.session_state.donut_memory == 'Day':
            water = eaten_sum_series[macro.lower()] 
            oil = not_eaten_sum_series[macro.lower()] 
        elif st.session_state.donut_view == 'Average' or st.session_state.donut_memory == 'Average':
            water = daily_average_series[macro.lower()]
            oil = 0
        bucket = st.session_state[config["max_key"]] 
        oil_bucket = max(bucket - water, 0) # The non-water volume inside the bucket is the oil_bucket
        water_spill = max(0, water - bucket) 
        oil_spill = max(0, oil - oil_bucket) 
        non_spill_water = min(bucket, water) 
        non_spill_oil = min(oil_bucket, oil)
        empty_air = max(0, bucket - (water + oil))

        donut_text = f"{config['emoji']} <br>{macro} <br> {(oil+water):.0f}/{bucket:.0f}"
        #######################
        # Plotly function that make graphs inside the graph
        fig.add_trace(
            # Draw the donuts
            go.Pie(
                values = [non_spill_water, non_spill_oil, water_spill, oil_spill, empty_air],
                marker_colors=[
                    config["color_primary"], 
                    config["color_secondary"], 
                    config["color_overflow"], 
                    config["color_overflow2"], 
                    "rgba(255,255,255,0.05)" # Color for empty air
                ],
                hole = 0.65, #IMPORTANT DONUT HOLE
                textinfo = "none",
                hoverinfo = "skip",
                sort = False,
                direction = 'clockwise',
            ),
            row = 1,
            col = col_index,
        )
    #  Add the centered text
        donut_logo = f"{config['emoji']}"
        donut_text =  f"{macro}"
        donut_numbers = f'{(oil+water):.0f}/{bucket:.0f}'
        x_pos = (col_index - 1) * 0.261 + 0.109
        
        fig.add_annotation(
            text=donut_logo,
            x=x_pos,
            y=0.55, 
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="middle",
            showarrow=False,
            font=dict(size=20)
        )
        fig.add_annotation(
            text=donut_text,
            x=x_pos,
            y=1.04, 
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="middle",
            showarrow=False,
            font=dict(size=14)
        )
        fig.add_annotation(
            text=donut_numbers,
            x=x_pos,
            y=0.35,
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="middle",
            showarrow=False,
            font=dict(size=11)
        )

    #  Clean up the background and margins outside the loop
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(255,255,255,0.02)",
        height=130,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    
    return fig
# 15. The editing ui    
@st.dialog("✏️ Edit Log")
def open_food_editor(row):
    #Initialize edit_eat_status if it doesnt exist
    simple_initializer(
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
    # 3. Loop through macros_config
    for macro, config in macros_config.items():
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
        save_edit(row)
        st.rerun() # to exit to main page
    elif clicked_pill == "❌ Delete":
        delete_selected_food(row)
        st.rerun()

        # function that changes the eatn value of said id to false
    
# 16. (Single food card)
def single_food_card(row):
    macro_string = ""
    for macro, config in macros_config.items():
        macro_string = macro_string + f"{config['emoji']} {row[macro.lower()]} {config['unit']} "
    # Draw the cards:
    card_button = st.button(
        label = f"**{row['food_name']}**    || {macro_string} ||     {row['time']:%H:%M}" if row['eat_status'] == True else f":grey[**{row['food_name']}**    || {macro_string}||    {row['time']:%H:%M}]",
        use_container_width= True,
        key = f"food_card_button_{str(row['id'])}" # Adds a key id based on the row number
    )
    if card_button:
        # Change the edit keys in the session state to the buttons in question
        input_list = [x['norm'] for x in inputs_config.values()] +['eat_status']
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
        use_container_width = True,
        on_click = donut_view_to_date
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
# 19. Function that pushes edit into the database
def save_edit(row):
    sync_datetime_to_split_keys('edit_datetime','edit_date','edit_time')
    valid_input = st.session_state['edit_'+'food_name'] and all(st.session_state['edit_'+ x.lower()]>= 0 for x in macros_config)
    # Check if fields are empty, zero values are accepted, name is mandatory.
    if valid_input:
        # Put the stuff in input field into payload
        payload={
            config["norm"]:st.session_state['edit_'+ config["norm"]] for config in inputs_config.values()
        }
        # Mark the username into the payload
        payload["username"] = st.session_state.selected_user
        # Mark the eating status based on the value in the pill button
        payload["eat_status"] = st.session_state.edit_eat_status
        # Change the datetime value in the payload (AFTER PUSHING TO FOOD DF) to strinsg
        payload["date"] = payload["date"].isoformat()
        payload["time"] = payload["time"].isoformat()
        # PUSH THE DATA TO SUPABASE
        conn.table("food_data").update(payload).eq('id',int(row['id'])).execute()
        # Clear input fields after adding ingredient
        for x in inputs_config.values():
                st.session_state[x["norm"]] = x["initial"]
        # MANUALLY clear the new UI-only datetime widget
        st.session_state["datetime"] = datetime.datetime.now(LOCAL_TZ)
        # clear the cache
        st.cache_data.clear()
        # Reload the food df with supabase
        st.session_state.food_df = load_food_data(st.session_state.selected_user)
    else:
        st.error("Please fill in all fields with valid values.")
    # CLEAR CACHE
    
# 20. Function that delete the desired row
def delete_selected_food(row):
   # Delete the data in the supabase
    conn.table("food_data").delete().eq('id',int(row['id'])).execute()
    #Clear cache
    st.cache_data.clear()
    st.session_state.food_df = load_food_data(st.session_state.selected_user)
# 21. DONUT VIEW MODE FORCE SELECT
def donut_store_memory():
    if st.session_state.donut_view == 'Day':
        st.session_state.donut_memory = 'Day'
    elif st.session_state.donut_view == 'Average':
        st.session_state.donut_memory = 'Average'
# 22 CHANGE for donut df when average is clicked
def segment_donut_change(date_range,food_df):
    if st.session_state.donut_view == 'Average' or st.session_state.donut_memory == 'Average':
        if len(date_range) == 2:
            st.session_state.for_plot_df = food_df[food_df['date'].between(date_range[0],date_range[1])]
    elif st.session_state.donut_view == 'Day' or st.session_state.donut_memory == 'Day':
        same_date_df = food_df[food_df['date']==st.session_state.selected_date] 
        st.session_state.for_plot_df = same_date_df
        
# 24. Action that changes donut_view key to 'Date'
def donut_view_to_date():
    st.session_state.donut_view = 'Day'
# 25. Label for the donut currently showing
def donut_label():
    if st.session_state.selected_date == datetime.datetime.now(LOCAL_TZ).date():
        date_label = 'today.'
    elif st.session_state.selected_date == datetime.datetime.now(LOCAL_TZ).date()-datetime.timedelta(days=1):
        date_label = 'yesterday.'
    else:
        date_label = f"{st.session_state.selected_date:%d %B %Y}."
    if st.session_state.donut_view == 'Average' or st.session_state.donut_memory == 'Average':
        return f"Showing daily average from {st.session_state.date_range[0]:%d %B %Y} ~ {st.session_state.date_range[1]:%d %B %Y}."
    elif st.session_state.donut_view == 'Day' or st.session_state.donut_memory == 'Day':
        return f"Showing data for {date_label}"
### BEGIN BACKEND CONNECTION ###
conn = st.connection("supabase", type=SupabaseConnection)
### END BACKEND CONNECTION ###

### BEGIN INITIALIZATION ###
# 1. (User Select) Initialize selected user
simple_initializer(name = "selected_user", initial_value = "Sexy Theo")
# 2. (Food Data) Initialize food_df data frame with the data from supabase
simple_initializer(name = "food_df", initial_value= load_food_data(st.session_state.selected_user))
# 3. (Log Food) Initialize session state keys for the input fields
for x in inputs_config.values():
    simple_initializer(name = x["norm"], initial_value = x["initial"])
# 4. (Max Values) Initialize macro targets into a dictionary from supabase with the most recent value
simple_initializer(name = "targets_dict_recent", initial_value = load_macro_goals(st.session_state.selected_user))
# 6. (Max Values)Initialize max value keys in session_stat  e
for x,y in st.session_state.targets_dict_recent.items():
    simple_initializer(x,y)
# 7. (Log Food) Initialize datetime, used for the input buttons
simple_initializer(
    name="datetime", 
    initial_value=datetime.datetime.now(LOCAL_TZ)
)
# 8. Initialize the data used for the plot called 'for_plot_df'
simple_initializer(
    name ='for_plot_df', 
    initial_value = st.session_state.food_df[st.session_state.food_df['date']==datetime.datetime.now(LOCAL_TZ).date()]
)
# 9. Initialize pill key
simple_initializer(
    name = 'pill_key',
    initial_value = None
)
# 10. Initialize edit values:
     # Input fields, excluding datetime but with date time
for x in inputs_config.values():
    simple_initializer(name = x["norm"], initial_value = x["initial"])
# 11. This is for the segment control at the top cannot have a None value
simple_initializer('donut_view_forcer', 'Day')
# 12. This is to initialize the donut_view so the UI uses an existing data
simple_initializer('donut_view', 'Day')
# 13. Initialize date_range
simple_initializer('date_range',(datetime.datetime.now(LOCAL_TZ).date()-datetime.timedelta(days=7),datetime.datetime.now(LOCAL_TZ).date())) 
### END INITIALIZATION ###
# 14. variable for the last selected date
simple_initializer('selected_date', datetime.datetime.now(LOCAL_TZ).date())
# 15. Donut memory to allow none
simple_initializer('donut_memory', 'Day')
### BEGIN SIDEBAR UI ###
# 1. username selector
with st.sidebar:
    st.selectbox(
        label = "Select User",
        options = ["Sexy Ano", "Sexy Theo", "Guest"],
        key = "selected_user",
        on_change = username_change_reset
    )
# 2. Setting maximum
    if st.button("Set Max Target"):
         open_set_max()
### END SIDEBAR UI ###

### BEGIN MAIN UI ###
# 1. Segmented Control for donut view
donut_view_mode = st.segmented_control(
    label = "",
    label_visibility = 'collapsed',
    options = ['Day', 'Average'],
    key = 'donut_view',
    width = 'stretch',
    selection_mode = 'single',
    on_change = donut_store_memory,
    default = 'Day'
)
# FORCE THE USER TO ALWAYS HAVE A CHOICE
# 2.1 The for_plot_df use date range when turned to average
segment_donut_change(st.session_state.date_range,st.session_state.food_df)
# 2.2 The for_plot_df use the last saved date when turned to date
# 2. Draw the plotly bars
st.plotly_chart(
    donut_progress_bars(st.session_state.for_plot_df), 
    use_container_width=True, 
    key="main_donut_chart",
    config={'displayModeBar': False,}
)
# 3. Draw Date range selector
selected_date_range = date_range_picker(
    title = donut_label(),
    key = "date_range",
    default_start = (datetime.datetime.now(LOCAL_TZ).date()-datetime.timedelta(days=7)),
    default_end = datetime.datetime.now(LOCAL_TZ).date()  
    )
# 4. Draw food cards:
draw_date_range(st.session_state.date_range, st.session_state.food_df)
### END MAIN UI ###

### INPUT FIELD UI ###
# 1. Floating action button
button_clicked = floating_button(
    label="🍽️ Add Food"
)
if button_clicked:
    food_input_dialog() # Opens the @st.dialog window