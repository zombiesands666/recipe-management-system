import streamlit as st
import pandas as pd
from database import (
    init_db, add_recipe, get_all_recipes, search_recipes,
    update_recipe, delete_recipe, get_recipe_by_id
)
from utils import validate_recipe_input, format_time

# Initialize the database
init_db()

# Page configuration
st.set_page_config(
    page_title="Recipe Manager",
    page_icon="🍳",
    layout="wide"
)

def main():
    st.title("🍳 Recipe Manager")
    
    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["View Recipes", "Add Recipe", "Search Recipes"])
    
    if page == "View Recipes":
        display_recipes()
    elif page == "Add Recipe":
        add_recipe_form()
    else:
        search_recipe_form()

def display_recipes():
    st.header("All Recipes")
    recipes = get_all_recipes()
    
    if not recipes:
        st.info("No recipes found. Add some recipes to get started!")
        return
    
    for recipe in recipes:
        with st.expander(f"📖 {recipe['title']} ({recipe['category']})"):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.subheader("Ingredients")
                st.write(recipe['ingredients'])
                
                st.subheader("Instructions")
                st.write(recipe['instructions'])
                
                st.text(f"⏱️ Cooking Time: {format_time(recipe['cooking_time'])}")
            
            with col2:
                if st.button("Edit", key=f"edit_{recipe['id']}"):
                    st.session_state['editing_recipe'] = recipe
                    st.experimental_rerun()
            
            with col3:
                if st.button("Delete", key=f"delete_{recipe['id']}"):
                    delete_recipe(recipe['id'])
                    st.success("Recipe deleted successfully!")
                    st.experimental_rerun()

def add_recipe_form():
    st.header("Add New Recipe")
    
    # Check if we're editing a recipe
    editing_recipe = st.session_state.get('editing_recipe', None)
    
    title = st.text_input("Recipe Title", value=editing_recipe['title'] if editing_recipe else "")
    category = st.selectbox(
        "Category",
        ["Breakfast", "Lunch", "Dinner", "Dessert", "Snack"],
        index=["Breakfast", "Lunch", "Dinner", "Dessert", "Snack"].index(editing_recipe['category'])
        if editing_recipe else 0
    )
    ingredients = st.text_area(
        "Ingredients (one per line)",
        value=editing_recipe['ingredients'] if editing_recipe else ""
    )
    instructions = st.text_area(
        "Instructions",
        value=editing_recipe['instructions'] if editing_recipe else ""
    )
    cooking_time = st.number_input(
        "Cooking Time (minutes)",
        min_value=1,
        value=editing_recipe['cooking_time'] if editing_recipe else 30
    )
    
    if st.button("Save Recipe"):
        errors = validate_recipe_input(title, category, ingredients, instructions, cooking_time)
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                if editing_recipe:
                    update_recipe(
                        editing_recipe['id'],
                        title, category, ingredients,
                        instructions, cooking_time
                    )
                    st.success("Recipe updated successfully!")
                    del st.session_state['editing_recipe']
                else:
                    add_recipe(title, category, ingredients, instructions, cooking_time)
                    st.success("Recipe added successfully!")
                
                # Clear the form
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error saving recipe: {str(e)}")

def search_recipe_form():
    st.header("Search Recipes")
    
    search_term = st.text_input("Enter search term (title or ingredients)")
    
    if search_term:
        recipes = search_recipes(search_term)
        
        if not recipes:
            st.info("No recipes found matching your search.")
            return
        
        st.subheader(f"Found {len(recipes)} recipes:")
        for recipe in recipes:
            with st.expander(f"📖 {recipe['title']} ({recipe['category']})"):
                st.write("**Ingredients:**")
                st.write(recipe['ingredients'])
                
                st.write("**Instructions:**")
                st.write(recipe['instructions'])
                
                st.text(f"⏱️ Cooking Time: {format_time(recipe['cooking_time'])}")

if __name__ == "__main__":
    main()
