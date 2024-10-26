import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Create database connection using environment variables."""
    try:
        conn = psycopg2.connect(
            host=os.environ['PGHOST'],
            database=os.environ['PGDATABASE'],
            user=os.environ['PGUSER'],
            password=os.environ['PGPASSWORD'],
            port=os.environ['PGPORT']
        )
        return conn
    except Exception as e:
        raise Exception(f"Database connection error: {str(e)}")

def init_db():
    """Initialize database with schema."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    with open('schema.sql', 'r') as f:
        cur.execute(f.read())
    
    conn.commit()
    cur.close()
    conn.close()

def add_recipe(title, category, ingredients, instructions, cooking_time):
    """Add a new recipe to the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO recipes (title, category, ingredients, instructions, cooking_time)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (title, category, ingredients, instructions, cooking_time))
        recipe_id = cur.fetchone()[0]
        conn.commit()
        return recipe_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_all_recipes():
    """Retrieve all recipes from the database."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM recipes ORDER BY created_at DESC")
    recipes = cur.fetchall()
    
    cur.close()
    conn.close()
    return recipes

def search_recipes(search_term):
    """Search recipes by title or ingredients."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT * FROM recipes 
        WHERE title ILIKE %s OR ingredients ILIKE %s 
        ORDER BY created_at DESC
    """, (f'%{search_term}%', f'%{search_term}%'))
    
    recipes = cur.fetchall()
    cur.close()
    conn.close()
    return recipes

def update_recipe(recipe_id, title, category, ingredients, instructions, cooking_time):
    """Update an existing recipe."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE recipes 
            SET title=%s, category=%s, ingredients=%s, instructions=%s, cooking_time=%s
            WHERE id=%s
        """, (title, category, ingredients, instructions, cooking_time, recipe_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def delete_recipe(recipe_id):
    """Delete a recipe by ID."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM recipes WHERE id=%s", (recipe_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_recipe_by_id(recipe_id):
    """Retrieve a specific recipe by ID."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM recipes WHERE id=%s", (recipe_id,))
    recipe = cur.fetchone()
    
    cur.close()
    conn.close()
    return recipe
