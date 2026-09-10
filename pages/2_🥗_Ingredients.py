import streamlit as st
from streamlit_extras.mandatory_date_range import *

# Self
from src import db, lmn, mm, utils

# 1. Username selector package:
lmn.username_selector()
# 2. Initialize the database from supabase
db.initialize(st.session_state.selected_user)

# 3. Ingredient Selector (Now with accept_new_option!)
selected_ingr = st.selectbox(
    label="Select Ingredient to Edit or Type to Create",
    options=st.session_state.ingredients_list, 
    # If it's a new option, Streamlit returns a string. If existing, it's your object.
    format_func=lambda x: x if isinstance(x, str) else x.display_name,
    index=None,
    placeholder="Choose an ingredient or type a new one...",
    accept_new_options=True
)

# 4. Dynamic Edit/Create UI
if selected_ingr:
    # Check if Streamlit returned a raw string (meaning the user typed something new)
    is_new_ingredient = isinstance(selected_ingr, str)
    
    if is_new_ingredient:
        st.markdown(f"**➕ Creating New: {selected_ingr}**")
        macroval_key = "new_ingr_macroval_create"
        
        new_name = st.text_input("Ingredient Name", value=selected_ingr)
        new_weight = st.number_input("Base Weight (g)", value=100.0, step=1.0)
        fresh_macroval = mm.MacroVal(0.0, 0.0, 0.0, 0.0)
        
        button_label = "➕ Save New Ingredient"
        
    else:
        st.markdown(f"**✏️ Editing: {selected_ingr.display_name}**")
        macroval_key = f"edit_ingr_macroval_{selected_ingr.id}"
        
        new_name = st.text_input("Ingredient Name", value=selected_ingr.display_name)
        new_weight = st.number_input("Base Weight (g)", value=float(selected_ingr.weight), step=1.0)
        fresh_macroval = mm.MacroVal(
            selected_ingr.macros.calories,
            selected_ingr.macros.carbs,
            selected_ingr.macros.protein,
            selected_ingr.macros.fat
        )
        
        button_label = "💾 Save Changes"

    # Render your custom macro UI (Shared by both modes)
    lmn.macros_input_field(
        initial_macroval=fresh_macroval, 
        target_macroval_key=macroval_key, 
        show_macroval=True
    )
    
    # Disable button if name is blanked out
    if st.button(button_label, type="primary", use_container_width=True, disabled=not new_name):
        
        if is_new_ingredient:
            # Construct a brand new Ingredient object
            ingr_payload = mm.Ingredient(
                id=None, # Assuming your db.save / Supabase assigns the ID
                display_name=new_name,
                weight=new_weight,
                macros=st.session_state[macroval_key],
                username=st.session_state.selected_user
            )
            toast_msg = f"Created {new_name}!"
            toast_icon = "🎉"
        else:
            # Overwrite the existing Python object
            ingr_payload = selected_ingr
            ingr_payload.display_name = new_name
            ingr_payload.weight = new_weight
            ingr_payload.macros = st.session_state[macroval_key]
            
            toast_msg = f"Updated {new_name}!"
            toast_icon = "✅"
            
        # Save directly to your Supabase ingredients table
        db.save([ingr_payload], st.session_state.ingredients)
        
        # Clear the memory key
        utils.state_del([macroval_key])
        
        st.toast(toast_msg, icon=toast_icon)
        st.rerun()