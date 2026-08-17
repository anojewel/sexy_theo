# Note for AI:
# Learning python from scratch by making a streamlit app. I hope to learn to manage data in python by making this macro tracker app. If i ask question to code, please prioritize giving me syntaxes as tools and teach concepts. Don't be too quick on giving the whole code.
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
### IMPORTS ###
import streamlit as st
import datetime 
import pandas as pd
import plotly.express as px
from st_supabase_connection import SupabaseConnection
from streamlit_extras.floating_button import floating_button
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
        "emoji": "🔥"
    },
    "Carbs": {
        "max_key": "max_carbs", 
        "max_val": 300,  
        "color_primary": "#6A5ACD", 
        "color_secondary": "#B0C4DE",
        "color_overflow": "#282054",
        "color_overflow2" : "#423589",
        "emoji": "🍞"
    },
    "Protein": {
        "max_key": "max_protein", 
        "max_val": 100,  
        "color_primary": "#3CB371", 
        "color_secondary": "#90EE90",
        "color_overflow": "#113C21",
        "color_overflow2" : "#1A5831",
        "emoji": "🥩"
    },
    "Fat": {
        "max_key": "max_fat", 
        "max_val": 75,   
        "color_primary": "#FFA500", 
        "color_secondary": "#FFDAB9",
        "color_overflow": "#3F2001",
        "color_overflow2" : "#6D3700",
        "emoji": "🧈"
    }
}

# 2. Input Fields Dictionary
# Combines: input_str_list, input_str_list_norm, input_initial_values
inputs_config = {
    "Food":     {"norm": "food_name", "initial": ""},
    "Calories": {"norm": "calories",  "initial": 0},
    "Carbs":    {"norm": "carbs",     "initial": 0},
    "Protein":  {"norm": "protein",   "initial": 0},
    "Fat":      {"norm": "fat",       "initial": 0},
    "Time":     {"norm": "time",      "initial":  datetime.datetime.now(LOCAL_TZ).time()},
    "Date":     {"norm": "date",      "initial":  datetime.datetime.now(LOCAL_TZ).date()}
}
### END INDEP DICTIONARIES ###
### BEGIN DEFINITIONS ###
# 1. Action that loads supabase table into a data
@st.cache_data
def load_food_data(username_input):
    # Assign variable to the food_data table that has equal user name values
    response = conn.table("food_data").select("*").eq("username", username_input).execute()
    # List of appropriate column names:
    column_name = [x["norm"] for x in inputs_config.values()] + ["id"] #<-- add the id column
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


# 2. Supabase macro_goals load function. Directly outputs a dictionary
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

# 3. Log food function, later used for the button.
def log_food():
    valid_input = st.session_state.food_name and all(st.session_state[x.lower()]>= 0 for x in macros_config)
    # Check if fields are empty, zero values are accepted, name is mandatory.
    if valid_input:
        # Append data from keys to the lowest row in food_df
        st.session_state.food_df.loc[len(st.session_state.food_df)] = [st.session_state[x["norm"]] for x in inputs_config.values()] + [None]
        # Clear input fields after adding ingredient
        for x in inputs_config.values():
                st.session_state[x["norm"]] = x["initial"]
    else:
        st.error("Please fill in all fields with valid values.")
    
# 4. Define a save function/action, purpose is to save to supabase.
def save_changes():
    # Fill username columns with the selected username
    st.session_state.food_df["username"] = st.session_state.selected_user
    # Grab the dictionary of the changes of the main_editor. 
    # We use index because the dictionary logs specific indexes of which the df changed.
    for index, changes  in st.session_state["main_editor"]["edited_rows"].items():
        # Grab from filtered_df, the id of the specific index 
        row_id = st.session_state.filtered_df.iloc[index]["id"]
        conn.table("food_data").update(changes).eq("id", row_id).execute()

    # Create data frame of new inputs
    payload4insert = st.session_state.food_df[pd.isna(st.session_state.food_df["id"])].astype({"date" : str, "time" : str}).drop(columns=["id"]).to_dict(orient="records")
    # Insert the payload4insert if its not empty
    if payload4insert:
        conn.table("food_data").insert(payload4insert, count=None).execute()
    # Clear cache
    st.cache_data.clear()
    # delete food_df to re-initialize data
    del st.session_state.food_df
   
# 5. need callable function for delete changes
def delete_changes():
    # 1. Delete the dataframe so it reloads fresh from the database
    if "food_df" in st.session_state:
        del st.session_state.food_df
        
    # 2. Clear out any typed edits in the data editor
    if "main_editor" in st.session_state:
        del st.session_state["main_editor"]

# 6. Saving max button action definition:
def save_max():
    # Define the dictionary payload as the data from session_state
    payload = {x["max_key"] : st.session_state[x["max_key"]] for x in macros_config.values()}
    payload["username"] = st.session_state.selected_user
    # Push to database
    conn.table("macro_goals").insert(payload, count=None).execute()
    # Clear cache
    st.cache_data.clear()
# 7. Function that creates a plotly figure to be displayed later in the app.
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
        height=30
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
# 8. Define a number display counter
def progressive_number_display(total, added, max):
    if added == 0:
        text = f"{total}/{max}"
    else:
        text = f"{total + added}/{max}"
    return text
# 9. (Name Matcher) Fills key values with most recent past data with the same name
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
# 10. Define initializer for simple objects/ not from gsheet
def simple_initializer(name:str, initial_value):
    if name not in st.session_state:
        st.session_state[name] = initial_value
# 11. Function that reset the session_state values for the username change
def username_change_reset():
    save_before_clearing = st.session_state.selected_user
    st.session_state.clear()
    st.session_state.selected_user = save_before_clearing
# 12. New combined progress bar function
def combined_progress_bar(filtered_food_sum):
    # Concept: Lists and Dictionaries. 
    # We will gather all our rows in a list, then convert it to a DataFrame.
    all_data = []
    color_map = {}
    
    # Loop through your macros_config just like you did in the UI
    for macro, config in macros_config.items():
        macro_lower = macro.lower()
        
        # Calculate current and max values
        number_display_cur = st.session_state[macro_lower] + filtered_food_sum[macro_lower]
        number_display_max = st.session_state[config["max_key"]]
        
        # BUCKET CONCEPT
        factor = filtered_food_sum[macro_lower] / number_display_max
        projected_factor = st.session_state[macro_lower] / number_display_max
        
        bucket = 1
        bar1 = min(factor, bucket)
        overflow1 = max(0, factor - bucket)
        small_bucket = min(bucket, 1 - bar1)
        bar2 = min(projected_factor, small_bucket)
        overflow2 = max(0, projected_factor - small_bucket)
        
        # Create a dynamic label for the Y-axis that includes your text and emojis!
        if number_display_cur > number_display_max:
            y_label = f"{config['emoji']} {macro}<br>{number_display_cur:.0f}/{number_display_max:.0f} (+{number_display_cur - number_display_max:.0f})"
        else:
            y_label = f"{config['emoji']} {macro}<br>{number_display_cur:.0f}/{number_display_max:.0f}"

        # Append dictionaries (rows) to our master list
        # Notice we combine the macro name and type to ensure unique colors
        all_data.extend([
            {"Shelf": y_label, "Value": bar1,      "Type": f"{macro} Current"},
            {"Shelf": y_label, "Value": bar2,      "Type": f"{macro} Projected"},
            {"Shelf": y_label, "Value": overflow1, "Type": f"{macro} Overflow"},
            {"Shelf": y_label, "Value": overflow2, "Type": f"{macro} Projected Overflow"},
        ])
        
        # Assign the correct hex codes to our unique type names
        color_map[f"{macro} Current"] = config["color_primary"]
        color_map[f"{macro} Projected"] = config["color_secondary"]
        color_map[f"{macro} Overflow"] = config["color_overflow"]
        color_map[f"{macro} Projected Overflow"] = config["color_overflow2"]

    # Convert the massive list of dictionaries into one Pandas DataFrame
    df = pd.DataFrame(all_data)
    
    # Plotly magic using our combined DataFrame and dynamic color map
    fig = px.bar(
        data_frame=df,
        x="Value",
        y="Shelf",
        color="Type",
        orientation="h",
        barmode="stack",
        color_discrete_map=color_map,
        range_x = [0, max(1, factor + projected_factor)],
    )   
    
    # Hide fluff but MAKE SURE Y-AXIS IS VISIBLE so your labels show!
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0), # Added slight top margin
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(255,255,255,0.02)",
        height=250 # Increased height so 4 bars fit comfortably
    )
    
    fig.update_xaxes(visible=False, fixedrange=True) 
    # Important: Set yaxes to visible=True so we see the emojis and numbers
    fig.update_yaxes(visible=True, fixedrange=True, title=None, autorange = "reversed") 

    fig.update_traces(
        marker_cornerradius=4, 
        hoverinfo="skip",      
        hovertemplate=None     
    )
    return fig
# 13. Floating dialog for logging food
@st.dialog("➕ Log New Food")
def food_input_dialog():
    # 1. Top Row: Text, Date, and Time inputs
    col_food, col_time, col_date = st.columns([4, 2, 2]) 
    
    col_food.text_input(
        label="Food Name", 
        key="food_name",
        on_change=fill_matching_data,
    )
    col_date.date_input("Date", key="date")
    col_time.time_input("Time", key="time")

    st.divider()

    # 2. Mobile-Friendly Macro Inputs & Individual Bars
    # Calculate the sum of food already eaten today
    filtered_food_sum = st.session_state.filtered_df[[x.lower() for x in macros_config]].sum()

    # Loop through the dictionary WITHOUT creating st.columns
    for macro, config in macros_config.items():
        macro_lower = macro.lower()
        step_value = 50 if macro == "Calories" else 1
        
        # A. The Number Input (Occupies 1 full row)
        st.number_input(
            f"{config['emoji']} {macro} ({'kcal' if macro == 'Calories' else 'g'})", 
            min_value=0, 
            step=step_value, 
            key=macro_lower
        )
        
        # B. Define the variables for your old function
        current_val = filtered_food_sum[macro_lower]
        projected_val = st.session_state[macro_lower]
        max_val = st.session_state[config["max_key"]]
        
        # C. The Old Caption Text (Occupies 1 full row)
        if current_val + projected_val > max_val:
            st.caption(f":red[{current_val:.0f}/{max_val:.0f} | + {projected_val:.0f} ({(current_val + projected_val - max_val) / max_val * 100:.0f}% Overflow)]")
        else:
            st.caption(f"{current_val:.0f}/{max_val:.0f} | + {projected_val:.0f}")

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
            use_container_width=True,
            config={'displayModeBar': False}
        )
        
        # Add a tiny bit of vertical spacing between each macro group
        st.markdown("<br>", unsafe_allow_html=True) 
    
    st.divider()
    
    # 3. Bottom Row: Action buttons
    col_log, col_ingredient = st.columns(2)
    
    # Use on_click=log_food so the state clears BEFORE widgets instantiate on the next run!
    if col_log.button("➕ Log Food", on_click=log_food, use_container_width=True, type="primary"):
        st.rerun() # Closes the dialog
        
    col_ingredient.button("🥣 Ingredient Mode", use_container_width=True)

# 14. Segmented Control Callback Action
def handle_save_segment():
    # Grab the value of what the user just clicked
    action = st.session_state.save_action_segment
    
    if action == "💾 Save":
        save_changes()
        # Non-blocking temporary green text!
        st.toast("✅ Saved successfully!", icon="✅") 
    elif action == "🗑️ Discard":
        delete_changes()
        st.toast("🗑️ Changes discarded.", icon="🗑️")
        
    # Crucial step: Reset the state to None so the button visually "un-clicks"
    st.session_state.save_action_segment = None

@st.dialog("Set Maximum Target")
def open_set_max():
    for x, y in macros_config.items():
        st.number_input(label = x, width = 100, value = st.session_state[y["max_key"]], key = y["max_key"])
    st.button(
        label = "Save", 
        on_click = save_max,
        disabled = any(st.session_state[x["max_key"]] == 0 for x in macros_config.values())
        )

### END DEFINITIONS ###

### BEGIN BACKEND CONNECTION ###
conn = st.connection("supabase", type=SupabaseConnection)
### END BACKEND CONNECTION ###

### BEGIN INITIALIZATION ###
# 1. Initialize selected user
simple_initializer(name = "selected_user", initial_value = "Guest")
# 2. Initialize food_df data frame with the data from supabase
simple_initializer(name = "food_df", initial_value= load_food_data(st.session_state.selected_user))
# 3. Initialize session state keys, for the input fields
for x in inputs_config.values():
    simple_initializer(name = x["norm"], initial_value = x["initial"])
# 4. Initialize macro targets into a dictionary from supabas with the most recent value
simple_initializer(name = "targets_dict_recent", initial_value = load_macro_goals(st.session_state.selected_user))
# 5. Initial date_filter_value
simple_initializer(name = "date_filter_value", initial_value = datetime.date.today())
# 6. Initialize max value keys in session_state
for x,y in st.session_state.targets_dict_recent.items():
    simple_initializer(x,y)
# 7. initialize the bottom menu boolean
if "show_bottom_menu" not in st.session_state:
    st.session_state.show_bottom_menu = True
# 8. Initialize filtered_df so it exists for the first run
simple_initializer(
    name="filtered_df", 
    initial_value=st.session_state.food_df[st.session_state.food_df["date"] == st.session_state.date_filter_value].copy()
)
### END INITIALIZATION ###

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
### BEGIN UI ###
# 1. Display the bars in the first row
filtered_food_sum = st.session_state.filtered_df[[x.lower() for x in macros_config]].sum()
st.plotly_chart(
    combined_progress_bar(filtered_food_sum), 
    use_container_width=True, 
    config={'displayModeBar': False}
)
date_column, save_changes_column = st.columns([2,1])
# 1.2 Date Picker and Variable Assignment
date_column.date_input(label="Date", 
    value=datetime.date.today(), 
    label_visibility="collapsed", key = "date_filter_value")
# 2. Second Row: The main date table
filtered_df = st.session_state.food_df[st.session_state.food_df["date"] == st.session_state.date_filter_value].copy()

filtered_df = st.data_editor(data = filtered_df, 
             hide_index=True, 
             width="stretch", 
             height=280, 
             key= "main_editor",
             column_config = {
        "date": None, 
        "Save Marker": None,
        "id": None,
        "food_name": st.column_config.TextColumn(label="Food", width="small"),
        "calories": st.column_config.NumberColumn(format="%.0f",label = "Calories", width = "small"),
        "carbs": st.column_config.NumberColumn(format="%.0f", label = "Carbs", width ="small"),
        "protein": st.column_config.NumberColumn(format="%.0f", label = 'Protein', width ="small"),
        "fat": st.column_config.NumberColumn(format="%.0f", label = 'Fat', width ="small"),
        "time": st.column_config.TimeColumn(format="HH:mm", label = 'Time', width ="small")
    }) 
# Take a snapshot of the table TO SESSION STATE so the Save button can find the IDs later!
#  Check if there are any new rows OR any edits
has_new_rows = st.session_state.food_df["id"].isna().any()
        # Initialize the has_edits as false
has_edits = False
if "main_editor" in st.session_state:
    if len(st.session_state["main_editor"]["edited_rows"]) > 0:
        has_edits = True

    # Disable buttons if there are NO new rows AND NO edits
buttons_disabled = not (has_new_rows or has_edits)
# The segmented control that acts like a dual-button row
st.segmented_control(
    label="Save or Discard",
    options=["💾 Save", "🗑️ Discard"],
    label_visibility="collapsed", # Hides the label so it looks like pure buttons
    selection_mode="single",
    key="save_action_segment",
    on_change=handle_save_segment,
    disabled=buttons_disabled #this isdefined earlier to check if new stuff is in the food data
)
### END UI ###

### INPUT FIELD UI ###
# Floating action button
button_clicked = floating_button(
    label="🍔 Add Food"
)
if button_clicked:
    food_input_dialog() # Opens the @st.dialog window