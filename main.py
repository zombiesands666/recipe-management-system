import streamlit as st
import streamlit.components.v1 as components
from database import (
    init_db, get_categories, add_recipe, get_recipes,
    get_recipe, get_recipe_ingredients
)
from auth import (
    register_user, login_user, logout_user,
    is_authenticated, get_current_user_id
)
from conversions import UnitConverter
import os

# Configure the page
st.set_page_config(
    page_title="Recipe Management System",
    page_icon="🍳",
    layout="wide"
)

def load_template():
    with open('templates/base.html', 'r') as f:
        return components.html(f.read(), height=0)

# Load the PWA template
load_template()

# Initialize the database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

# Custom CSS
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

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Login"

st.title("Recipe Management System")

# Authentication section
if not is_authenticated():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    if login_user(username, password):
                        st.success("Successfully logged in!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")
            
            if submit:
                if new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords don't match")
                    elif register_user(new_username, new_password):
                        st.success("Registration successful! Please login.")
                        st.session_state.current_page = "Login"
                        st.rerun()
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Please fill in all fields")

else:
    # Sidebar navigation
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()
    
    selected_page = st.sidebar.radio(
        "Choose a page",
        ["View Recipes", "Add New Recipe", "Unit Converter"]
    )
    
    # Add install button to sidebar
    st.sidebar.markdown("""
    <div style="margin-top: 20px; padding: 10px; border-top: 1px solid #e6e6e6;">
        <h3 style="margin-bottom: 10px;">Install App</h3>
        <button id="installButton">
            Install Recipe App
        </button>
    </div>
    """, unsafe_allow_html=True)

    if selected_page == "View Recipes":
        st.subheader("Your Recipes")
        
        # Search functionality
        search_col1, search_col2 = st.columns(2)
        with search_col1:
            search_query = st.text_input("Search recipes by title")
        with search_col2:
            category_filter = st.selectbox(
                "Filter by category",
                ["All Categories"] + [cat['name'] for cat in get_categories()]
            )
        
        try:
            recipes = get_recipes(user_id=get_current_user_id())
            filtered_recipes = recipes
            
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

    elif selected_page == "Add New Recipe":
        st.subheader("Add New Recipe")
        
        with st.form("recipe_form"):
            title = st.text_input("Recipe Title")
            description = st.text_area("Description")
            
            col1, col2 = st.columns(2)
            with col1:
                cooking_time = st.number_input("Cooking Time (minutes)", min_value=1)
            with col2:
                servings = st.number_input("Servings", min_value=1)
            
            categories = get_categories()
            category_options = {cat['name']: cat['id'] for cat in categories}
            category = st.selectbox("Category", options=list(category_options.keys()))
            
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
                            ingredients_data=ingredients_data,
                            user_id=get_current_user_id()
                        )
                        st.success("Recipe added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add recipe: {e}")

    elif selected_page == "Unit Converter":
        st.subheader("Measurement Converter")
        st.write("Convert between different units of measurement commonly used in recipes.")
        
        supported_units = UnitConverter.get_supported_units()
        
        measurement_type = st.selectbox(
            "Select measurement type",
            list(supported_units.keys())
        )
        
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
        
        if st.button("Convert"):
            try:
                result = UnitConverter.convert(value, from_unit, to_unit)
                st.success(f"{value} {from_unit} = {result:.2f} {to_unit}")
            except ValueError as e:
                st.error(str(e))
        
        st.subheader("Common Conversion Reference")
        st.markdown("""
        | From | To | Conversion |
        |------|-----|------------|
        | 1 cup | milliliters | 236.59 ml |
        | 1 tablespoon | milliliters | 14.79 ml |
        | 1 teaspoon | milliliters | 4.93 ml |
        | 1 gram | ounces | 0.035 oz |
        | 1 pound | grams | 453.59 g |
        | 1 ounce | grams | 28.35 g |
        """)
