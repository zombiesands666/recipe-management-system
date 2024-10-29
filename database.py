import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

# Global connection pool
_pool = None

def init_connection_pool():
    """Initialize the connection pool."""
    global _pool
    try:
        required_env_vars = ['PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD', 'PGPORT']
        
        # Check if all required environment variables are present
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv('PGHOST'),
            database=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            port=os.getenv('PGPORT')
        )
    except Exception as e:
        raise ConnectionError(f"Failed to initialize connection pool: {str(e)}")

@contextmanager
def get_db_connection():
    """Get a database connection from the pool."""
    global _pool
    if _pool is None:
        init_connection_pool()
    
    conn = None
    try:
        conn = _pool.getconn()
        yield conn
    except psycopg2.Error as e:
        raise ConnectionError(f"Database connection error: {str(e)}")
    finally:
        if conn:
            _pool.putconn(conn)

def init_db():
    """Initialize the database with the schema."""
    with get_db_connection() as conn:
        try:
            with conn.cursor() as cur:
                # Read and execute the schema file
                with open('schema.sql', 'r') as f:
                    cur.execute(f.read())
                conn.commit()
                print("Database schema successfully initialized")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to initialize database: {str(e)}")

def get_categories():
    """Get all categories from the database."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM categories ORDER BY name")
            return cur.fetchall()

def add_recipe(title, description, instructions, cooking_time, servings, category_id, ingredients_data):
    """Add a new recipe with ingredients."""
    with get_db_connection() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
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
            raise Exception(f"Failed to add recipe: {str(e)}")

def get_recipes():
    """Get all recipes with their categories."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT r.*, c.name as category_name
                FROM recipes r
                LEFT JOIN categories c ON r.category_id = c.id
                ORDER BY r.title
            """)
            return cur.fetchall()

def get_recipe_ingredients(recipe_id):
    """Get ingredients for a specific recipe."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT i.name, ri.quantity, ri.unit
                FROM recipe_ingredients ri
                JOIN ingredients i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = %s
            """, (recipe_id,))
            return cur.fetchall()

def get_recipe(recipe_id):
    """Get a specific recipe with all its details."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT r.*, c.name as category_name
                FROM recipes r
                LEFT JOIN categories c ON r.category_id = c.id
                WHERE r.id = %s
            """, (recipe_id,))
            recipe = cur.fetchone()
            
            if recipe:
                recipe['ingredients'] = get_recipe_ingredients(recipe_id)
            
            return recipe
