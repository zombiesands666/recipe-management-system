import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Create a database connection using environment variables."""
    conn = psycopg2.connect(
        host=os.getenv('PGHOST'),
        database=os.getenv('PGDATABASE'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        port=os.getenv('PGPORT')
    )
    return conn

def init_db():
    """Initialize the database with the schema."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Drop existing tables in correct order
        cur.execute("""
            DROP TABLE IF EXISTS recipe_ingredients CASCADE;
            DROP TABLE IF EXISTS recipes CASCADE;
            DROP TABLE IF EXISTS ingredients CASCADE;
            DROP TABLE IF EXISTS categories CASCADE;
        """)
        
        # Read and execute the schema file
        with open('schema.sql', 'r') as f:
            cur.execute(f.read())
        
        conn.commit()
        print("Database schema successfully initialized")
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to initialize database: {str(e)}")
    finally:
        cur.close()
        conn.close()

def get_categories():
    """Get all categories from the database."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM categories ORDER BY name")
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return categories

def add_recipe(title, description, instructions, cooking_time, servings, category_id, ingredients_data):
    """Add a new recipe with ingredients."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Insert recipe
        cur.execute("""
            INSERT INTO recipes (title, description, instructions, cooking_time, servings, category_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (title, description, instructions, cooking_time, servings, category_id))
        
        result = cur.fetchone()
        if not result:
            raise Exception("Failed to create recipe")
        recipe_id = result['id']
        
        # Process ingredients
        for ingredient in ingredients_data:
            # Check if ingredient exists, if not create it
            cur.execute("SELECT id FROM ingredients WHERE name = %s", (ingredient['name'],))
            result = cur.fetchone()
            
            if result is None:
                cur.execute("INSERT INTO ingredients (name) VALUES (%s) RETURNING id", 
                          (ingredient['name'],))
                result = cur.fetchone()
                if not result:
                    raise Exception("Failed to create ingredient")
                ingredient_id = result['id']
            else:
                ingredient_id = result['id']
            
            # Add to recipe_ingredients
            cur.execute("""
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit)
                VALUES (%s, %s, %s, %s)
            """, (recipe_id, ingredient_id, ingredient['quantity'], ingredient['unit']))
        
        conn.commit()
        return recipe_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_recipes():
    """Get all recipes with their categories."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT r.*, c.name as category_name
        FROM recipes r
        LEFT JOIN categories c ON r.category_id = c.id
        ORDER BY r.title
    """)
    recipes = cur.fetchall()
    
    cur.close()
    conn.close()
    return recipes

def get_recipe_ingredients(recipe_id):
    """Get ingredients for a specific recipe."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT i.name, ri.quantity, ri.unit
        FROM recipe_ingredients ri
        JOIN ingredients i ON ri.ingredient_id = i.id
        WHERE ri.recipe_id = %s
    """, (recipe_id,))
    ingredients = cur.fetchall()
    
    cur.close()
    conn.close()
    return ingredients

def get_recipe(recipe_id):
    """Get a specific recipe with all its details."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT r.*, c.name as category_name
        FROM recipes r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.id = %s
    """, (recipe_id,))
    recipe = cur.fetchone()
    
    if recipe:
        recipe['ingredients'] = get_recipe_ingredients(recipe_id)
    
    cur.close()
    conn.close()
    return recipe
