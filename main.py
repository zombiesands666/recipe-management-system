import streamlit as st
from database import init_db, get_categories

# Initialize the database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

st.title("Recipe Management System")
st.write("Welcome to your personal recipe collection!")

# Display categories to test database connection
try:
    categories = get_categories()
    st.subheader("Available Categories")
    for category in categories:
        st.write(f"- {category['name']}")
except Exception as e:
    st.error(f"Failed to fetch categories: {e}")
