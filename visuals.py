# Third Party
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
import hashmap
# 1. Plotly figures inside the input dialog
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

# 2. Donut Charts
def donut_progress_bars(for_plot_df):
    sum_series = for_plot_df[[macro.lower() for macro in hashmap.macros_config]].sum()
    eaten_sum_series = for_plot_df[for_plot_df['eat_status']==True][[macro.lower() for macro in hashmap.macros_config]].sum()
    not_eaten_sum_series = for_plot_df[for_plot_df['eat_status']==False][[macro.lower() for macro in hashmap.macros_config]].sum()
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
    for col_index, (macro, config) in enumerate(hashmap.macros_config.items(), start = 1):
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
                values = [non_spill_water, non_spill_oil,  oil_spill, water_spill, empty_air],
                marker_colors=[
                    f'rgba({config['rgb']},1)', 
                    f'rgba({config['rgb']},0.7)', 
                    f'rgba({config['rgb']},0.6)', 
                    f'rgba({config['rgb']},0.4)', 
                    f'rgba({config['rgb']},0.1)' # Color for empty air
                ],
                hole = 0.62, #IMPORTANT DONUT HOLE
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