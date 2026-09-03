# Third Party
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from streamlit_extras.floating_button import floating_button
from streamlit_extras.mandatory_date_range import *
# Self
from . import macro_models as mm
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
                    f'rgba({x.rgb},0.6)', 
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