import streamlit as st
import datetime 
from streamlit_extras.mandatory_date_range import *
from zoneinfo import ZoneInfo

from src import db, lmn, mm, utils

@st.dialog("➕ New Food")
def open():
    # Z. Draw donuts or show warning if no goals exist
    utils.initialize('new_macros_val', mm.MacroVal(0.0,0.0,0.0,0.0))
    utils.initialize('new_datetime', datetime.datetime.now(ZoneInfo('Asia/Taipei')))
    utils.initialize('new_ingr_macrosval', mm.MacroVal(0.0,0.0,0.0,0.0))
    display_macros_val = st.session_state.new_macros_val + st.session_state.new_ingr_macrosval
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
        lmn.macro_badge_button(display_macros_val)
        st.info("No goals set yet! Set a goal that includes this food's logged date",icon="🎯")
    # A. Let user fill food name 
    utils.initialize('new_food_name','')
    lmn.food_name_select(st.session_state.food_data, 'new_food_name', 'new_macros_val')
    
    # B. Let user fill datetime
    st.datetime_input(
        label="Date & Time",    
        key="new_datetime",
        label_visibility="collapsed",
    )
    
    # C. Draw the input fields (Key perfectly matches now!)
    lmn.macros_input_field(mm.MacroVal(0.0,0.0,0.0,0.0), 'new_macros_val')
    # D. Append data to a food log object
    food_draft = mm.FoodLog(
        food_name=st.session_state.new_food_name,
        macros=st.session_state.new_macros_val,
        date=st.session_state.new_datetime.date(),
        time=st.session_state.new_datetime.time(),
        username=st.session_state.selected_user,
        eat_status=True if st.session_state.new_datetime.date() <= datetime.datetime.now(ZoneInfo('Asia/Taipei')).date() else False
    )
    # E. Ingredient add
    lmn.recipe_builder(food_draft, st.session_state.ingredients_list, st.session_state.recipe_list,'edit_rcp_key', 'new_ingr_key', 'new_ingr_macrosval')
    # F. Log button & Clear button actions
    def save_action():
        if st.session_state.new_food_name != '':
            # 1. Save food log to database
            saved_food = db.save([food_draft], st.session_state.food_data)
            # 2. Get foodlog id
            food_draft.id = saved_food[0]['id']
            # 3. Save new ingredients to database
            if len(st.session_state.new_ingr_key) != 0:
                saved_ingr_list = db.save(st.session_state.new_ingr_key, st.session_state.ingredients)
                # Loop through the database response to find and assign the generated IDs
                for saved_dict in saved_ingr_list:
                    for ingr_obj in st.session_state.new_ingr_key:
                        if ingr_obj.display_name == saved_dict['display_name']:
                            ingr_obj.id = saved_dict['id']
                            break
            
            final_recipes = []

            # 3A. Update your EXISTING recipes with the new food_draft.id
            for rcp in st.session_state.edit_rcp_key:
                rcp.food_id = food_draft.id
                final_recipes.append(rcp)

            # 3B. Create NEW recipes for your newly saved ingredients
            if len(st.session_state.new_ingr_key) != 0:
                for ingr_obj in st.session_state.new_ingr_key:
                    new_rcp = mm.Recipe(
                        food_id = food_draft.id,
                        ingr_id = ingr_obj.id,          # The new ID we just assigned in Step 2!
                        weight = ingr_obj.weight,       
                        username = st.session_state.selected_user,
                        id = None                       # None because this recipe isn't in the DB yet
                    )
                    final_recipes.append(new_rcp)
            db.save(final_recipes, st.session_state.recipe)
            
            # Clear database cache and reset form inputs for the next open
            utils.state_del([
                'new_food_name', 'new_datetime', 'new_macros_val','bucket_values','edit_rcp_key','new_ingr_key','new_ingr_macrosval'
            ])
            st.rerun()
        else:
            st.info('Please fill in the food name')

    def clear_action():
        # Deleting these keys lets your utils.initialize() functions reset them to defaults automatically
        utils.state_del([
            'new_food_name', 'new_datetime', 'new_macros_val','bucket_values','edit_rcp_key','new_ingr_key','new_ingr_macrosval'
        ])  
        st.rerun(scope='fragment')
        
    # D1. Draw the pills
    lmn.pill_buttons(
        actions={
            "➕ Log Food": save_action,
            "🧹 Clear": clear_action
        },
        key="input_pill_key"
    )

    