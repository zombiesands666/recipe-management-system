import streamlit as st
from database import (
    init_db, get_categories, add_recipe, get_recipes,
    get_recipe, get_recipe_ingredients
)

# Initialize the database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

st.title("Recipe Management System")
st.write("Welcome to your personal recipe collection!")

# Sidebar navigation
page = st.sidebar.selectbox("Choose an action", ["View Recipes", "Add New Recipe"])

if page == "View Recipes":
    st.subheader("Your Recipes")
    
    try:
        recipes = get_recipes()
        for recipe in recipes:
            with st.expander(f"{recipe['title']} ({recipe['category_name']})"):
                st.write(f"**Description:** {recipe['description']}")
                st.write(f"**Cooking Time:** {recipe['cooking_time']} minutes")
                st.write(f"**Servings:** {recipe['servings']}")
                
                st.write("**Ingredients:**")
                ingredients = get_recipe_ingredients(recipe['id'])
                for ing in ingredients:
                    st.write(f"- {ing['quantity']} {ing['unit']} {ing['name']}")
                
                st.write("**Instructions:**")
                st.write(recipe['instructions'])

    except Exception as e:
        st.error(f"Failed to load recipes: {e}")

elif page == "Add New Recipe":
    st.subheader("Add New Recipe")
    
    with st.form("recipe_form"):
        title = st.text_input("Recipe Title")
        description = st.text_area("Description")
        
        col1, col2 = st.columns(2)
        with col1:
            cooking_time = st.number_input("Cooking Time (minutes)", min_value=1)
        with col2:
            servings = st.number_input("Servings", min_value=1)
        
        # Category selection
        categories = get_categories()
        category_options = {cat['name']: cat['id'] for cat in categories}
        category = st.selectbox("Category", options=list(category_options.keys()))
        
        # Dynamic ingredient input
        st.subheader("Ingredients")
        num_ingredients = st.number_input("Number of ingredients", min_value=1, max_value=20)
        ingredients_data = []
        
        for i in range(int(num_ingredients)):
            col1, col2, col3 = st.columns(3)
            with col1:
                ingredient_name = st.text_input(f"Ingredient {i+1} name")
            with col2:
                quantity = st.number_input(f"Quantity {i+1}", min_value=0.0, step=0.1)
            with col3:
                unit = st.text_input(f"Unit {i+1} (e.g., g, ml, cups)")
            
            if ingredient_name and quantity and unit:
                ingredients_data.append({
                    "name": ingredient_name,
                    "quantity": quantity,
                    "unit": unit
                })
        
        instructions = st.text_area("Cooking Instructions")
        submit_button = st.form_submit_button("Add Recipe")
        
        if submit_button:
            if not title or not instructions or not ingredients_data:
                st.error("Please fill in all required fields")
            else:
                try:
                    recipe_id = add_recipe(
                        title=title,
                        description=description,
                        instructions=instructions,
                        cooking_time=cooking_time,
                        servings=servings,
                        category_id=category_options[category],
                        ingredients_data=ingredients_data
                    )
                    st.success("Recipe added successfully!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Failed to add recipe: {e}")
