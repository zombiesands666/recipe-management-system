import hashlib
import os
from database import get_db_connection
import streamlit as st

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    salt = os.environ.get('PGPASSWORD', 'default-salt')  # Using DB password as salt
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def register_user(username: str, password: str) -> bool:
    """Register a new user."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if username exists
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone() is not None:
            return False
        
        # Insert new user
        password_hash = hash_password(password)
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def login_user(username: str, password: str) -> bool:
    """Verify user credentials."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cur.execute(
            "SELECT id, username FROM users WHERE username = %s AND password_hash = %s",
            (username, password_hash)
        )
        user = cur.fetchone()
        if user:
            st.session_state['user_id'] = user[0]
            st.session_state['username'] = user[1]
            st.session_state['authenticated'] = True
            return True
        return False
    finally:
        cur.close()
        conn.close()

def logout_user():
    """Log out the current user."""
    for key in ['user_id', 'username', 'authenticated']:
        if key in st.session_state:
            del st.session_state[key]

def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get('authenticated', False)

def get_current_user_id() -> int:
    """Get the current user's ID."""
    return st.session_state.get('user_id', None)
