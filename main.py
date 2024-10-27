import streamlit as st
from database import (
    init_db, get_categories, add_recipe, get_recipes,
    get_recipe, get_recipe_ingredients
)
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
    #pwa-install {
        background-color: #f63366;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
        text-align: center;
    }
    #pwa-install button {
        background-color: white;
        color: #f63366;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Add PWA install prompt in sidebar
install_prompt = """
<div id="pwa-install" style="display: none;">
    <p style="margin: 0;">📱 Install Recipe App on your device!</p>
    <p style="font-size: 12px; margin: 5px 0;">Access your recipes offline and get a better mobile experience</p>
    <button onclick="installPWA()">Install App</button>
</div>
<script>
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    document.getElementById('pwa-install').style.display = 'block';
});

function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
            }
            deferredPrompt = null;
            document.getElementById('pwa-install').style.display = 'none';
        });
    }
}

// Register service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(error => {
                console.error('ServiceWorker registration failed:', error);
            });
    });
}
</script>
"""

# Add the install prompt to the sidebar at the top
st.sidebar.markdown(install_prompt, unsafe_allow_html=True)

st.title("Recipe Management System")
st.write("Welcome to your personal recipe collection!")

# Sidebar navigation
page = st.sidebar.selectbox("Choose an action", ["View Recipes", "Add New Recipe"])

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
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add recipe: {e}")