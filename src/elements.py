from plotly.subplots import make_subplots
import plotly.graph_objects as go
from streamlit_extras.mandatory_date_range import *
import datetime
# Self
from . import macro_models as mm
from . import database as db
from . import utils

def donut_progress_bars(water_values, oil_values, bucket_values):
    # Plotly function that make a single element room, that can put four plots in it
    fig = make_subplots(
        rows = 1,
        cols = 4,
        specs = [[ {"type" : "domain"}] * 4] # domain types are require for donuts
    )
    # The subplots have numbers assigned for each row, we need to assign them with enumerate.
    for index, x in enumerate(mm.macro_ui_rules,start=1):
        # Take numbers from each macro
        water = water_values[x.key] 
        oil = oil_values[x.key] 
        bucket = bucket_values[x.key]
        # Bucket math
        oil_bucket = max(bucket - water, 0) # The non-water volume inside the bucket is the oil_bucket
        water_spill = max(0, water - bucket) 
        oil_spill = max(0, oil - oil_bucket) 
        non_spill_water = min(bucket, water) 
        non_spill_oil = min(oil_bucket, oil)
        empty_air = max(0, bucket - (water + oil))
        #
        donut_text = f"{x.emoji} <br>{x.title} <br> {(oil+water):.0f}/{bucket:.0f}"
        # Plotly function that make graphs inside the graph
        fig.add_trace(
            # Draw the donuts
            go.Pie(
                values = [non_spill_water, non_spill_oil,  oil_spill, water_spill, empty_air],
                marker_colors=[
                    f'rgba({x.rgb},0.85)', 
                    f'rgba({x.rgb},0.3)', 
                    f'rgba({x.rgb},0.9)', 
                    f'rgba({x.rgb},1.0)', 
                    f'rgba({x.rgb},0.1)' # Color for empty air
                ],
                hole = 0.62, #IMPORTANT DONUT HOLE
                textinfo = "none",
                hoverinfo = "skip",
                sort = False,
                direction = 'clockwise',
            ),
            row = 1,
            col = index,
        )
    #  Add the centered text
        donut_logo = f"{x.emoji}"
        donut_text =  f"{x.title}"
        donut_numbers = f'{(oil+water):.0f}/{bucket:.0f}'
        x_pos = (index - 1) * 0.261 + 0.109
        
        fig.add_annotation(
            text=donut_logo,
            x=x_pos,
            y=0.52, 
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
            y=1.02, 
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
            y=0.39,
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="middle",
            showarrow=False,
            font=dict(size=10)
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
def username_selector():
    utils.initialize('selected_user','Sexy Theo')
    with st.sidebar:
        st.selectbox(
            label = "Select User",
            options = ["Sexy Ano", "Sexy Theo", "Guest"],
            key = "selected_user",
            on_change=utils.state_del,
            args=(['food_data','goals','bucket_values'],),  
            persist_state='session'
        )
def macros_input_field(initial_macroval: mm.MacroVal, target_macroval_key, show_macroval = False):
    # A. Use the input values to initial keys
    utils.initialize(target_macroval_key, initial_macroval)
    
    # B. Create pill option labels
    options_map = {f"{x.key}": f"{x.emoji}" for x in mm.macro_ui_rules}
    
    # --- MEMORY INITIALIZATION ---
    utils.initialize("pill_input_mode_memo", 'calories')
    # C1 Draw badges
    macros_number_label=""  
    for x in mm.macro_ui_rules:
        macros_number_label = macros_number_label + f"{getattr(st.session_state[target_macroval_key],x.key)} ({x.unit})‎ ‎ ‎ ‎ ‎ " 
    if show_macroval == True:
        st.button(
            width='stretch',
            type="tertiary",
            label=macros_number_label,
            disabled=True
        ) 
    # C2. Draw the pills
    st.pills(
        label="",
        label_visibility="collapsed",
        width='stretch',
        key="pill_input_mode",
        options=[f"{x.key}" for x in mm.macro_ui_rules],
        format_func=lambda option: options_map[option]
    )
    
    # --- MEMORY CAPTURE ---
    # If the pill is actively selected, commit it to memory. 
    # If it resets to None during a date change, this ignores the None and keeps the old memory.
    if st.session_state.pill_input_mode is not None:
        st.session_state.pill_input_mode_memo = st.session_state.pill_input_mode
        
    # Lock in the active mode using the memory variable
    active_mode = st.session_state.pill_input_mode_memo

    # D. Replace target macro key action using entered value 
    def _change_target():
        for x in mm.macro_ui_rules:
            if active_mode == x.key:
                setattr(st.session_state[target_macroval_key], x.key, st.session_state[f"macros_number_input_{x.key}"])
                
    # E. Sync four session state variables with the four keys for the number input below
    for x in mm.macro_ui_rules:
        st.session_state[f"macros_number_input_{x.key}"] = getattr(st.session_state[target_macroval_key], x.key)
        
    # G. Draw number input
    step_map = {x.key: x.step_val for x in mm.macro_ui_rules}
    st.number_input(
        label="",
        label_visibility="collapsed",
        width='stretch',
        key=f"macros_number_input_{active_mode}",
        on_change=_change_target,
        step=step_map[active_mode],
        format="%.1f",
        min_value=0.0
    )
def pill_buttons(actions: dict, key: str):
    """
    Creates a row of pills that execute assigned functions when clicked.
    Uses a pending state proxy to allow st.rerun() in the mapped functions.
    """
    utils.initialize(key, None)
    pending_key = f"{key}_pending"
    
    # 1. Callback: ONLY manages state, no actions or reruns here!
    def _callback():
        selected = st.session_state[key]
        if selected:
            # Save the choice to the pending flag and visually un-click the pill
            st.session_state[pending_key] = selected
            st.session_state[key] = None 
            
    # 2. Draw the Widget
    st.pills(
        label="hidden_label", 
        label_visibility="collapsed",
        options=list(actions.keys()),
        key=key,
        on_change=_callback,
        width='stretch'
    )
    
    # 3. Main Script Flow: Execute the action safely
    if pending_key in st.session_state:
        action_str = st.session_state[pending_key]
        del st.session_state[pending_key]
        
        # Execute the mapped function in the main flow (st.rerun() works perfectly here!)
        actions[action_str]()
def food_name_select(food_data:db.Supabase, target_key:str, macroval_key:str):
    def fill_matching_data():
        same_name_foodlogs = []
        for x in food_data.list():
            if x.food_name == st.session_state[target_key]:
                same_name_foodlogs = same_name_foodlogs + [x]
        if len(same_name_foodlogs) > 0:   
            st.session_state[macroval_key] = max(same_name_foodlogs, key=lambda f:datetime.datetime.combine(f.date,f.time)).macros
    food_df = food_data.df()
    st.selectbox(
        label='',
        label_visibility='collapsed',
        placeholder='Food Name',
        options=food_df['food_name'].unique(),
        on_change= fill_matching_data,
        key=target_key,
        accept_new_options=True
    )   
