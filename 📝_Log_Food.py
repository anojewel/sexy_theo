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
# Deploy
### IMPORTS ###
import streamlit as st
import datetime 
import pandas as pd
import plotly.express as px
from st_supabase_connection import SupabaseConnection
from streamlit_extras.bottom_container import bottom
### BEGIN CONFIGURATION ###
st.set_page_config(
    page_title= "💋 Baby Tracker",
    layout="centered", 
    initial_sidebar_state="collapsed"
)
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
    "Time":     {"norm": "time",      "initial": datetime.datetime.now().time()},
    "Date":     {"norm": "date",      "initial": datetime.date.today()}
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
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    # Add rounded corners AND explicitly enforce the auto text position
    fig.update_traces(
        marker_cornerradius=4, # Adjust this number for more/less rounding
        textposition="auto"     # Keeps the smart inside/outside placement
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
# 12. Toggle function for the bottom menu show hide
def toggle_menu():
    st.session_state.show_bottom_menu = not st.session_state.show_bottom_menu
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

### BEGIN UI ###
# Sidebar username selector
with st.sidebar:
    st.selectbox(
        label = "Select User",
        options = ["Sexy Ano", "Sexy Theo", "Guest"],
        key = "selected_user",
        on_change = username_change_reset
    )
# 1. First Row
date_column, spacer_lakjsdfhlajksdfh, set_maximum_column, save_changes_column, delete_changes_column = st.columns([2,6,2,1,1])

# 1.2 Date Picker and Variable Assignment
date_column.date_input(label="Date", 
    value=datetime.date.today(), 
    label_visibility="collapsed", key = "date_filter_value")

# 1.3 POP UP WINDOW FOR SETTING MAXIMUM
with set_maximum_column.popover(label = "Set Max", width = "stretch"):
    for x, y in macros_config.items():
        st.number_input(label = x, width = 100, value = st.session_state[y["max_key"]], key = y["max_key"])
    st.button(
        label = "Save", 
        on_click = save_max,
        disabled = any(st.session_state[x["max_key"]] == 0 for x in macros_config.values())
        )
    #  Check if there are any new rows OR any edits
has_new_rows = st.session_state.food_df["id"].isna().any()
    # Initialize the has_edits as false
has_edits = False
if "main_editor" in st.session_state:
    if len(st.session_state["main_editor"]["edited_rows"]) > 0:
        has_edits = True

    # Disable buttons if there are NO new rows AND NO edits
buttons_disabled = not (has_new_rows or has_edits)

# 1.4 Display the save changes button
save_changes_column.button(
    label="💾",
    on_click=save_changes,
    type="secondary",
    disabled=buttons_disabled
)

# 1.5 Display the delete/discard button
delete_changes_column.button(
    label="🗑️",
    type="secondary",
    on_click=delete_changes,
    disabled=buttons_disabled 
)
# 2.  Display the bars in new second row
# Sum the data here, Needs to be here for the bars.
filtered_food_sum = st.session_state.filtered_df[[x.lower() for x in macros_config]].sum()
bar_cols = st.columns(4) 
for col, (macro, config) in zip(bar_cols, macros_config.items()):
    # Calculate once per loop iteration using explicit names
    number_display_cur = st.session_state[macro.lower()] + filtered_food_sum[macro.lower()]
    number_display_max = st.session_state[config['max_key']]
    
    # Inline overflow/remaining display in caption
    col.caption(
        f"{config["emoji"]} :red[{number_display_cur:.0f}/{number_display_max:.0f} | + {number_display_cur - number_display_max:.0f} ({(number_display_cur - number_display_max) / number_display_max * 100:.0f}%)]" 
        if number_display_cur > number_display_max 
        else f"{config["emoji"]} {number_display_cur:.0f}/{number_display_max:.0f} | - {number_display_max - number_display_cur:.0f} ({(number_display_max - number_display_cur) / number_display_max * 100:.0f}%)"
    )
    # Display progress bars
    col.plotly_chart(
        figure_progress_bar(
            factor = filtered_food_sum[macro.lower()]/st.session_state[config["max_key"]], 
            projected_factor = (st.session_state[macro.lower()])/st.session_state[config["max_key"]], 
            bar_color = config["color_primary"], 
            projected_bar_color =config["color_secondary"],
            overflow_color = config["color_overflow"],
            projected_overflow_color = config["color_overflow2"]))
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
        "food_name": st.column_config.TextColumn(label="Food", width="medium"),
        "calories": st.column_config.NumberColumn(format="%.0f",label = "Calories", width = "small"),
        "carbs": st.column_config.NumberColumn(format="%.0f", label = "Carbs", width ="small"),
        "protein": st.column_config.NumberColumn(format="%.0f", label = 'Protein', width ="small"),
        "fat": st.column_config.NumberColumn(format="%.0f", label = 'Fat', width ="small"),
        "time": st.column_config.TimeColumn(format="HH:mm", label = 'Time', width ="small")
    }) 
# Take a snapshot of the table TO SESSION STATE so the Save button can find the IDs later!
st.session_state.filtered_df = filtered_df

# Put inside a bottom container
with bottom():
    if st.session_state.show_bottom_menu:
        emoji_label = "🔽" # Point down to close
    else:
        emoji_label = "🔼" # Point up to open

    spacerljkngtnjk, toggle_button, spacernjkgmf = st.columns([3,1,3])

    toggle_button.button(label=emoji_label, on_click=toggle_menu)
    if st.session_state.show_bottom_menu:
        macro_input_cols = st.columns(4) 

        for col, (macro, config) in zip(macro_input_cols, macros_config.items()):
            step_value = 50 if macro == "Calories" else 1
            col.number_input(f"{config["emoji"]}{macro} ({"kcal" if macro == "Calories" else "g"})", min_value = 0, step = step_value, key = macro.lower())

        # 4. Fourth Row: Text and date inputs
        col_food, col_time, col_date = st.columns([4,1,1]) #Creates column for food name and date time
        # 4.1 Text input with past matching function
        col_food.text_input(
            label = "Food Name", 
            key = "food_name",
            on_change = fill_matching_data,
            )
        # 4.2 Simple datetime inputs
        col_date.date_input("Date", key ="date")
        col_time.time_input("Time", key ="time")


        # 5. Fifth Row: The lower buttons of ingredient and log button    
        spacerfkjasdbflkjadfjkadf,add_ingredient_button, log_button = st.columns([9,3,1.5])
        # 5.1  Log food
        log_button.button("➕Log", on_click=log_food)

        # 6.1 Ingredient omde
        add_ingredient_button.button("🥣 Ingredient Mode")

### END UI ###