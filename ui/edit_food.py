import streamlit as st
import datetime 
from streamlit_extras.mandatory_date_range import *
# Self
from src import db, lmn, mm, utils

@st.dialog("✏️ Edit Log")
def open(food_log: mm.FoodLog):
    edit_name_key = f"edit_food_name_{food_log.id}"
    edit_datetime_key = f"edit_datetime_{food_log.id}"
    edit_macros_key = f"edit_macros_{food_log.id}"
    edit_eat_status_key = f"edit_eat_status_{food_log.id}"
    new_ingr_macrosval_key = f"new_ingr_macrosval_{food_log.id}"
    edit_bucket_key = f"edit_bucket_{food_log.id}"
    # Initialize the input values here
    utils.initialize(edit_name_key, food_log.food_name)
    utils.initialize(edit_datetime_key, datetime.datetime.combine(food_log.date,food_log.time))
    utils.initialize(edit_eat_status_key, food_log.eat_status)
    utils.initialize(edit_macros_key, food_log.macros)
    utils.initialize(new_ingr_macrosval_key, mm.MacroVal(0.0,0.0,0.0,0.0))
    # Z. Donut display
    display_macros_val = st.session_state[edit_macros_key] + st.session_state[new_ingr_macrosval_key]
    try:
        st.session_state[edit_bucket_key] = utils.goal_specificity_choose(food_log.date)
        if edit_bucket_key in st.session_state:
                # For plotly to use the chosen date
                food_df = st.session_state.food_data.df()
                st.plotly_chart(
                    lmn.donut_progress_bars(
                    water_values=st.session_state.sum_same_date,
                    oil_values=display_macros_val.dict(),
                    bucket_values=st.session_state[edit_bucket_key],
                    hole_size=0.75
                    ),
                    width='stretch'
                )         
    except Exception:
        lmn.macro_badge_button(display_macros_val, f"badge_{food_log.id}")
        st.info("No goals set yet! Set a goal that includes this food's logged date",icon="🎯")
    # A. Allow user to edit the food text
    lmn.food_name_select(st.session_state.food_data, edit_name_key, edit_macros_key)
    # B.2 Allow user to edit datetime
    st.datetime_input(
        label="Date & Time", 
        key=edit_datetime_key, 
        label_visibility = "collapsed",
    )
    # C. Allow user to edit the macro values
    lmn.macros_input_field(food_log.macros, edit_macros_key, show_macroval=False)

    # D. Draw a button toggle for the eat status
    if st.session_state[edit_eat_status_key] == True:
        if st.button("✅ Eaten",width='stretch'):
            st.session_state[edit_eat_status_key] = False
            st.rerun(scope='fragment')
    elif st.session_state[edit_eat_status_key] == False:
        if st.button("⬜ Eaten",width='stretch'):
            st.session_state[edit_eat_status_key] = True
            st.rerun(scope='fragment')
    # E. Recipe builder
    edit_rcp_key = f"edit_rcp_{food_log.id}"
    new_ingr_key = f"new_ingr_{food_log.id}"
    lmn.recipe_builder(food_log, st.session_state.ingredients_list, st.session_state.recipe_list, edit_rcp_key, new_ingr_key, new_ingr_macrosval_key)
    # E. Define the target actions using your existing class methods
    def save_action():
        # Update the existing object's attributes with the new UI widget states
        food_log.food_name = st.session_state[edit_name_key]
        food_log.date = st.session_state[edit_datetime_key].date()
        food_log.time = st.session_state[edit_datetime_key].time()
        food_log.macros = st.session_state[edit_macros_key]
        food_log.eat_status = st.session_state[edit_eat_status_key]
        # Save food log item to database
        db.save([food_log],st.session_state.food_data)
        # Grab orinal recipe
        original_recipes = food_log.recipes(st.session_state.recipe_list)
        if len(st.session_state[new_ingr_key]) != 0:
            # Save new ingredient to database
            saved_ingr_list = db.save(st.session_state[new_ingr_key], st.session_state.ingredients)
            # Loop through the database response to find and assign the generated IDs
            for saved_dict in saved_ingr_list:
                for ingr_obj in st.session_state[new_ingr_key]:
                    if ingr_obj.display_name == saved_dict['display_name']:
                        ingr_obj.id = saved_dict['id']
                        break
        final_recipes = []

        # 3A. Update your EXISTING recipes with the new id
        if len(st.session_state[edit_rcp_key]) != 0:
            for rcp in st.session_state[edit_rcp_key]:
                rcp.food_id = food_log.id
                final_recipes.append(rcp)

        # 3B. Create NEW recipes for your newly saved ingredients
        if len(st.session_state[new_ingr_key]) != 0:
            for ingr_obj in st.session_state[new_ingr_key]:
                new_rcp = mm.Recipe(
                    food_id = food_log.id,
                    ingr_id = ingr_obj.id,          # The new ID we just assigned in Step 2!
                    weight = ingr_obj.weight,       
                    username = st.session_state.selected_user,
                    id = None                       # None because this recipe isn't in the DB yet
                )
                final_recipes.append(new_rcp)
        # 4. Filter out the removed recipes to a list
        removed_recipes = []
        for orcp in original_recipes:
            if orcp.id not in [rcp.id for rcp in final_recipes]:
                removed_recipes.append(orcp)
        db.save(final_recipes, st.session_state.recipe)
        db.delete(removed_recipes, st.session_state.recipe)
        # Nuke the database cache and all dialog widget states
        utils.state_del([
            edit_name_key, 
            edit_datetime_key,
            edit_eat_status_key,
            edit_macros_key,
            edit_rcp_key,
            new_ingr_key,
            new_ingr_macrosval_key,
            f"ingr_select_{food_log.id}" # <- Add this here!
        ])
        st.rerun()

    def delete_action():
        # Recipe list to delete:
        rcps_to_del= food_log.recipes(st.session_state.recipe_list)
        db.delete(rcps_to_del, st.session_state.recipe)
        # Call your built-in class method
        db.delete([food_log],st.session_state.food_data)

        # Nuke the database cache and all dialog widget states
        utils.state_del([
            edit_name_key, 
            edit_datetime_key,
            edit_eat_status_key,
            edit_macros_key,
            edit_rcp_key,
            new_ingr_key,
            new_ingr_macrosval_key,
            f"ingr_select_{food_log.id}" # <- Add this here!
        ])
        st.rerun()

    # E1. Draw the pills and pass the actions
    lmn.pill_buttons(
        actions={
            "💾 Save": save_action,
            "❌ Delete": delete_action
        }, 
        key="edit_pill_key"
    )