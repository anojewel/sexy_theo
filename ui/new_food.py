import streamlit as st
import datetime 
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo

from src import db, lmn, mm, utils

@st.dialog("➕ New Food")
def open():
    utils.initialize('new_macros_val', mm.MacroVal(0.0,0.0,0.0,0.0))
    utils.initialize('new_datetime', datetime.datetime.now(ZoneInfo('Asia/Taipei')))
    utils.initialize('new_ingr_macrosval', mm.MacroVal(0.0,0.0,0.0,0.0))
    utils.initialize('new_is_simple', True) 
    utils.initialize('new_food_name','')

    food_draft = mm.FoodLog(
        id="new_draft", 
        food_name=st.session_state.new_food_name,
        macros=st.session_state.new_macros_val,
        date=st.session_state.new_datetime.date(),
        time=st.session_state.new_datetime.time(),
        username=st.session_state.selected_user,
        eat_status=True if st.session_state.new_datetime.date() <= datetime.datetime.now(ZoneInfo('Asia/Taipei')).date() else False,
        is_simple=st.session_state.new_is_simple 
    )

    # --- THE DONUT PLACEHOLDER ---
    # Instantly lock in the layout with the grey skeleton chart
    donut_placeholder = st.empty()
    donut_placeholder.plotly_chart(lmn.donut_skeleton(hole_size=0.75), width='stretch')
        
    # A. Let user fill food name 
    lmn.food_name_select(
        food_data=st.session_state.food_data, 
        name_key='new_food_name', 
        macroval_key='new_macros_val',
        is_simple_key='new_is_simple',
        ingr_select_key="ingr_select_new_draft",
        sgmnt_key="sgmnt_key_new_draft"
    )
    
    st.datetime_input(
        label="Date & Time",    
        key="new_datetime",
        label_visibility="collapsed",
    )
    
    lmn.simple_or_ingr(
        food=food_draft,
        simple_macroval_key='new_macros_val',
        ingr_macroval_key='new_ingr_macrosval',
        target_is_simple_key='new_is_simple',
        edit_recipe_key='edit_rcp_key',
        new_ingr_key='new_ingr_key'
    )

    # Z. Draw donuts (Overwrites the skeleton placeholder when math finishes)
    with donut_placeholder:
        if st.session_state.new_is_simple:
            display_macros_val = st.session_state.new_macros_val
        else:
            display_macros_val = st.session_state.new_ingr_macrosval
         
        if 'bucket_values' in st.session_state:
            st.plotly_chart(
                lmn.donut_progress_bars(
                    water_values=utils.day_total(st.session_state.new_datetime.date(),True,st.session_state.food_data),
                    oil_values=display_macros_val.dict(),
                    bucket_values=st.session_state.bucket_values,
                    hole_size=0.75
                ),
                width='stretch'
            )       
        else:
            lmn.macro_badge_button(display_macros_val, "new_badge_fallback")
            st.info("No goals set yet! Set a goal that includes this food's logged date", icon="🎯")
            
    def save_action():
        if st.session_state.new_food_name != '':
            food_draft.id = None 
            saved_food = db.save([food_draft], st.session_state.food_data)
            food_draft.id = saved_food[0]['id']
            
            if len(st.session_state.new_ingr_key) != 0:
                saved_ingr_list = db.save(st.session_state.new_ingr_key, st.session_state.ingredients)
                for saved_dict in saved_ingr_list:
                    for ingr_obj in st.session_state.new_ingr_key:
                        if ingr_obj.display_name == saved_dict['display_name']:
                            ingr_obj.id = saved_dict['id']
                            break
            
            final_recipes = []

            for rcp in st.session_state.edit_rcp_key:
                rcp.food_id = food_draft.id
                final_recipes.append(rcp)

            if len(st.session_state.new_ingr_key) != 0:
                for ingr_obj in st.session_state.new_ingr_key:
                    new_rcp = mm.Recipe(
                        food_id = food_draft.id,
                        ingr_id = ingr_obj.id,          
                        weight = ingr_obj.weight,       
                        username = st.session_state.selected_user,
                        id = None                       
                    )
                    final_recipes.append(new_rcp)
            db.save(final_recipes, st.session_state.recipe)
            
            utils.state_del([
                'new_food_name', 'new_datetime', 'new_macros_val','bucket_values',
                'edit_rcp_key','new_ingr_key','new_ingr_macrosval', 'new_is_simple'
            ])
            st.rerun()
        else:
            st.info('Please fill in the food name')

    def clear_action():
        utils.state_del([
            'new_food_name', 'new_datetime', 'new_macros_val','bucket_values',
            'edit_rcp_key','new_ingr_key','new_ingr_macrosval', 'new_is_simple'
        ])  
        st.rerun(scope='fragment')
        
    lmn.pill_buttons(
        actions={
            "➕ Log Food": save_action,
            "🧹 Clear": clear_action
        },
        key="input_pill_key"
    )