import streamlit as st
import datetime 
from streamlit_extras.mandatory_date_range import *

from src import db, lmn, mm, utils

@st.dialog("✏️ Edit Log")
def open(food_log: mm.FoodLog):
    # 1. Define ALL keys first
    edit_name_key = f"edit_food_name_{food_log.id}"
    edit_datetime_key = f"edit_datetime_{food_log.id}"
    edit_macros_key = f"edit_macros_{food_log.id}"
    edit_eat_status_key = f"edit_eat_status_{food_log.id}"
    new_ingr_macrosval_key = f"new_ingr_macrosval_{food_log.id}"
    edit_bucket_key = f"edit_bucket_{food_log.id}"
    edit_rcp_key = f"edit_rcp_{food_log.id}"
    new_ingr_key = f"new_ingr_{food_log.id}"
    edit_is_simple_key = f"edit_is_simple_{food_log.id}" 
    
    # 2. Initialize the input values safely
    utils.initialize(edit_name_key, food_log.food_name)
    utils.initialize(edit_datetime_key, datetime.datetime.combine(food_log.date, food_log.time))
    utils.initialize(edit_eat_status_key, food_log.eat_status)
    utils.initialize(edit_macros_key, food_log.macros if food_log.macros else mm.MacroVal(0.0,0.0,0.0,0.0))
    
    is_simple_default = food_log.is_simple if food_log.is_simple is not None else True
    utils.initialize(edit_is_simple_key, is_simple_default)
    utils.initialize(new_ingr_macrosval_key, food_log.ingr_macroval(st.session_state.ingredients_list, st.session_state.recipe_list))

    # --- THE DONUT PLACEHOLDER ---
    # Instantly lock in the layout with the grey skeleton chart
    donut_placeholder = st.empty()
    donut_placeholder.plotly_chart(lmn.donut_skeleton(hole_size=0.75), width='stretch')

    # A. Allow user to edit the food text
    # A. Allow user to edit the food text
    lmn.food_name_select(
        food_data=st.session_state.food_data, 
        name_key=edit_name_key, 
        macroval_key=edit_macros_key,
        is_simple_key=edit_is_simple_key,
        ingr_select_key=f"ingr_select_{food_log.id}",
        sgmnt_key=f"sgmnt_key_{food_log.id}"
    )
    
    # B. Allow user to edit datetime
    st.datetime_input(
        label="Date & Time", 
        key=edit_datetime_key, 
        label_visibility = "collapsed",
    )
    
    # C. Draw the simple/ingr input fields
    lmn.simple_or_ingr(
        food=food_log,
        simple_macroval_key=edit_macros_key,
        ingr_macroval_key=new_ingr_macrosval_key,
        target_is_simple_key=edit_is_simple_key,
        edit_recipe_key=edit_rcp_key,
        new_ingr_key=new_ingr_key
    )

    # D. Draw a button toggle for the eat status
    if st.session_state[edit_eat_status_key] == True:
        if st.button("✅ Eaten",width='stretch'):
            st.session_state[edit_eat_status_key] = False
            st.rerun(scope='fragment')
    elif st.session_state[edit_eat_status_key] == False:
        if st.button("⬜ Eaten",width='stretch'):
            st.session_state[edit_eat_status_key] = True
            st.rerun(scope='fragment')

    # Z. Donut display (Overwrites the skeleton placeholder when math finishes)
    with donut_placeholder:
        if st.session_state[edit_is_simple_key] == True:
            display_macros_val = st.session_state[edit_macros_key]
        else:
            display_macros_val = st.session_state[new_ingr_macrosval_key]
        
        try:
            st.session_state[edit_bucket_key] = utils.goal_specificity_choose(food_log.date).to_dict()
            day_total_series = utils.day_total(food_log.date, food_log.eat_status, st.session_state.food_data)
            water_dict = day_total_series.to_dict()
            
            original_true_macros = food_log.true_macroval(
                st.session_state.ingredients_list, 
                st.session_state.recipe_list
            )
            for x in mm.macro_ui_rules:
                water_dict[x.key] = max(0, water_dict[x.key] - getattr(original_true_macros, x.key))

            st.plotly_chart(
                lmn.donut_progress_bars(
                    water_values=water_dict,
                    oil_values=display_macros_val.dict(),
                    bucket_values=st.session_state[edit_bucket_key],
                    hole_size=0.75
                ),
                width='stretch'
            )        
        except ValueError: 
            st.info("No goals set yet! Set a goal that includes this food's logged date", icon="🎯")

    def save_action():
        food_log.food_name = st.session_state[edit_name_key]
        food_log.date = st.session_state[edit_datetime_key].date()
        food_log.time = st.session_state[edit_datetime_key].time()
        food_log.macros = st.session_state[edit_macros_key]
        food_log.eat_status = st.session_state[edit_eat_status_key]
        food_log.is_simple = st.session_state[edit_is_simple_key] 
        
        db.save([food_log], st.session_state.food_data)
        original_recipes = food_log.recipes(st.session_state.recipe_list)
        
        # --- IS_SIMPLE DEPENDENT RECIPE LOGIC ---
        if not st.session_state[edit_is_simple_key]: 
            # If in Ingredient Mode, process all recipe additions and deletions
            if st.session_state[new_ingr_key]:
                saved_ingr_list = db.save(st.session_state[new_ingr_key], st.session_state.ingredients)
                for saved_dict in saved_ingr_list:
                    for ingr_obj in st.session_state[new_ingr_key]:
                        if ingr_obj.display_name == saved_dict['display_name']:
                            ingr_obj.id = saved_dict['id']
                            break
                            
            final_recipes = []
            for rcp in st.session_state[edit_rcp_key]:
                rcp.food_id = food_log.id
                final_recipes.append(rcp)

            for ingr_obj in st.session_state[new_ingr_key]:
                new_rcp = mm.Recipe(
                    food_id = food_log.id,
                    ingr_id = ingr_obj.id,          
                    weight = ingr_obj.weight,       
                    username = st.session_state.selected_user,
                    id = None                       
                )
                final_recipes.append(new_rcp)
                
            removed_recipes = []
            for orcp in original_recipes:
                if orcp.id not in [rcp.id for rcp in final_recipes]:
                    removed_recipes.append(orcp)
                    
            db.save(final_recipes, st.session_state.recipe)
            db.delete(removed_recipes, st.session_state.recipe)
            
        else:
            # If in Simple Mode, actively purge any old recipes so they don't haunt the database
            if original_recipes:
                db.delete(original_recipes, st.session_state.recipe)
        
        # --- CLEANUP ---
        utils.state_del([
            edit_name_key, edit_datetime_key, edit_eat_status_key, edit_macros_key,
            edit_rcp_key, new_ingr_key, new_ingr_macrosval_key, edit_is_simple_key,
            f"ingr_select_{food_log.id}", f"sgmnt_key_{food_log.id}", 
            f"pill_input_mode_{edit_macros_key}", f"pill_input_mode_memo_{edit_macros_key}"
        ])
        st.rerun()

    def delete_action():
        rcps_to_del= food_log.recipes(st.session_state.recipe_list)
        db.delete(rcps_to_del, st.session_state.recipe)
        db.delete([food_log],st.session_state.food_data)

        utils.state_del([
            edit_name_key, edit_datetime_key, edit_eat_status_key, edit_macros_key,
            edit_rcp_key, new_ingr_key, new_ingr_macrosval_key, edit_is_simple_key,
            f"ingr_select_{food_log.id}", f"sgmnt_key_{food_log.id}", 
            f"pill_input_mode_{edit_macros_key}", f"pill_input_mode_memo_{edit_macros_key}"
        ])
        st.rerun()

    lmn.pill_buttons(
        actions={
            "💾 Save": save_action,
            "❌ Delete": delete_action
        }, 
        key="edit_pill_key"
    )