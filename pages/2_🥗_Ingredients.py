import streamlit as st
from streamlit_extras.mandatory_date_range import *

# Self
from src import db, lmn, mm, utils



# 1. Username selector package:
lmn.username_selector()
# 2. Iniitalize the database form supabase
db.initialize(st.session_state.selected_user)
# 3. Ingredient Selector
selected_ingr = st.selectbox(
    label="Select Ingredient to Edit",
    options=st.session_state.ingredients_list, # Pulls from your initialized db[cite: 2]
    format_func=lambda x: x.display_name,
    index=None,
    placeholder="Choose an ingredient..."
)

# 4. Edit UI
if selected_ingr:
    st.markdown(f"**Editing: {selected_ingr.display_name}**")
    
    # Create a unique memory key tied to this specific ingredient's ID
    macroval_key = f"edit_ingr_macroval_{selected_ingr.id}"
    
    new_name = st.text_input("Ingredient Name", value=selected_ingr.display_name)
    new_weight = st.number_input("Base Weight (g)", value=float(selected_ingr.weight), step=1.0)
    
    # Pass a fresh copy of the MacroVal so we don't accidentally mutate the underlying list 
    # before the user actually clicks Save
    fresh_macroval = mm.MacroVal(
        selected_ingr.macros.calories,
        selected_ingr.macros.carbs,
        selected_ingr.macros.protein,
        selected_ingr.macros.fat
    )
    
    # Render your custom macro UI[cite: 3]
    lmn.macros_input_field(
        initial_macroval=fresh_macroval, 
        target_macroval_key=macroval_key, 
        show_macroval=True
    )
    
    if st.button("💾 Save Changes", type="primary", use_container_width=True):
        # 1. Apply UI changes to the Python object
        selected_ingr.display_name = new_name
        selected_ingr.weight = new_weight
        selected_ingr.macros = st.session_state[macroval_key]
        
        # 2. Save directly to your Supabase ingredients table
        db.save([selected_ingr], st.session_state.ingredients)
        
        # 3. Clear the specific memory key so it reloads fresh from DB next time
        utils.state_del([macroval_key])
        
        # 4. Vanishing pop-up notification
        st.toast(f"Updated {new_name}!", icon="✅")
        st.rerun()