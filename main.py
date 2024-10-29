import streamlit as st
from database import (
    init_db, get_categories, add_recipe, get_recipes,
    get_recipe, get_recipe_ingredients
)
from conversions import UnitConverter
import os
from streamlit.components.v1 import html

# Initialize the database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

# Configure the page
st.set_page_config(
    page_title="Recipe Management System",
    page_icon="🍳",
    layout="wide"
)

# Custom CSS for mobile responsiveness
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-size: 16px !important;
    }
    @media (max-width: 768px) {
        .row-widget.stButton {
            margin: 5px 0;
        }
        .stMarkdown {
            font-size: 14px;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("Recipe Management System")
st.write("Welcome to your personal recipe collection!")

# Sidebar navigation
page = st.sidebar.selectbox("Choose an action", ["View Recipes", "Add New Recipe", "Unit Converter"])

if page == "View Recipes":
    st.subheader("Your Recipes")
    
    # Add search functionality
    search_col1, search_col2 = st.columns(2)
    with search_col1:
        search_query = st.text_input("Search recipes by title")
    with search_col2:
        category_filter = st.selectbox(
            "Filter by category",
            ["All Categories"] + [cat['name'] for cat in get_categories()]
        )
    
    try:
        recipes = get_recipes()
        filtered_recipes = recipes
        
        # Apply search filters
        if search_query:
            filtered_recipes = [
                recipe for recipe in filtered_recipes 
                if search_query.lower() in recipe['title'].lower()
            ]
        
        if category_filter != "All Categories":
            filtered_recipes = [
                recipe for recipe in filtered_recipes 
                if recipe['category_name'] == category_filter
            ]
        
        if not filtered_recipes:
            st.info("No recipes found matching your search criteria.")
        
        # Use columns for grid layout on larger screens
        cols = st.columns(2)
        for idx, recipe in enumerate(filtered_recipes):
            with cols[idx % 2]:
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

elif page == "Unit Converter":
    st.subheader("Measurement Converter")
    st.write("Convert between different units of measurement commonly used in recipes.")
    
    # Get supported units
    supported_units = UnitConverter.get_supported_units()
    
    # Create conversion form
    with st.form("converter_form"):
        # Select measurement type
        measurement_type = st.selectbox(
            "Select measurement type",
            list(supported_units.keys())
        )
        
        # Create three columns for the conversion inputs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            value = st.number_input("Value", min_value=0.0, step=0.1)
        
        with col2:
            from_unit = st.selectbox(
                "From unit",
                supported_units[measurement_type]
            )
        
        with col3:
            to_unit = st.selectbox(
                "To unit",
                supported_units[measurement_type]
            )
        
        convert_button = st.form_submit_button("Convert")
        
        if convert_button:
            try:
                result = UnitConverter.convert(value, from_unit, to_unit)
                st.success(f"{value} {from_unit} = {result:.2f} {to_unit}")
            except ValueError as e:
                st.error(str(e))
    
    # Add conversion table
    st.subheader("Common Conversion Reference")
    st.write("Here are some common recipe measurement conversions:")
    
    conversion_table = """
    | From | To | Conversion |
    |------|-----|------------|
    | 1 cup | milliliters | 236.59 ml |
    | 1 tablespoon | milliliters | 14.79 ml |
    | 1 teaspoon | milliliters | 4.93 ml |
    | 1 gram | ounces | 0.035 oz |
    | 1 pound | grams | 453.59 g |
    | 1 ounce | grams | 28.35 g |
    """
    st.markdown(conversion_table)

# Add PWA install prompt
install_prompt = """
<div id="install-prompt" style="display: none; position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); 
     background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 1000;">
    <p style="margin: 0;">Install Recipe App on your device!</p>
    <button onclick="installPWA()" style="background-color: #f63366; color: white; border: none; 
            padding: 8px 16px; border-radius: 5px; margin-top: 10px; cursor: pointer;">
        Install
    </button>
</div>
<script>
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    document.getElementById('install-prompt').style.display = 'block';
});

function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
            }
            deferredPrompt = null;
            document.getElementById('install-prompt').style.display = 'none';
        });
    }
}
</script>
"""

st.components.v1.html(install_prompt, height=100)
