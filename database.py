import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise EnvironmentError(error_msg)
        
        logger.info("Initializing database connection pool")
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv('PGHOST'),
            database=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            port=os.getenv('PGPORT')
        )
        logger.info("Database connection pool initialized successfully")
    except Exception as e:
        error_msg = f"Failed to initialize connection pool: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg)

@contextmanager
def get_db_connection():
    """Get a database connection from the pool."""
    global _pool
    if _pool is None:
        init_connection_pool()
    
    conn = None
    try:
        conn = _pool.getconn()
        logger.debug("Acquired database connection from pool")
        yield conn
    except psycopg2.Error as e:
        error_msg = f"Database connection error: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg)
    finally:
        if conn:
            _pool.putconn(conn)
            logger.debug("Released database connection back to pool")

def init_db():
    """Initialize the database with the schema."""
    logger.info("Starting database initialization")
    with get_db_connection() as conn:
        try:
            with conn.cursor() as cur:
                with open('schema.sql', 'r') as f:
                    cur.execute(f.read())
                conn.commit()
                logger.info("Database schema successfully initialized")
        except Exception as e:
            error_msg = f"Failed to initialize database: {str(e)}"
            logger.error(error_msg)
            conn.rollback()
            raise Exception(error_msg)

def get_categories():
    """Get all categories from the database."""
    logger.debug("Fetching categories from database")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM categories ORDER BY name")
            categories = cur.fetchall()
            logger.debug(f"Retrieved {len(categories)} categories")
            return categories

def add_recipe(title, description, instructions, cooking_time, servings, category_id, ingredients_data):
    """Add a new recipe with ingredients."""
    logger.info(f"Adding new recipe: {title}")
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
                    error_msg = "Failed to create recipe: no id returned"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                recipe_id = result['id']
                logger.debug(f"Created recipe with id: {recipe_id}")
                
                # Process ingredients
                for ingredient in ingredients_data:
                    cur.execute("SELECT id FROM ingredients WHERE name = %s", (ingredient['name'],))
                    result = cur.fetchone()
                    
                    if result is None:
                        cur.execute("INSERT INTO ingredients (name) VALUES (%s) RETURNING id", 
                                  (ingredient['name'],))
                        result = cur.fetchone()
                        if not result:
                            error_msg = f"Failed to create ingredient: {ingredient['name']}"
                            logger.error(error_msg)
                            raise Exception(error_msg)
                        ingredient_id = result['id']
                    else:
                        ingredient_id = result['id']
                    
                    cur.execute("""
                        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit)
                        VALUES (%s, %s, %s, %s)
                    """, (recipe_id, ingredient_id, ingredient['quantity'], ingredient['unit']))
                
                conn.commit()
                logger.info(f"Successfully added recipe {title} with id {recipe_id}")
                return recipe_id
        except Exception as e:
            error_msg = f"Failed to add recipe: {str(e)}"
            logger.error(error_msg)
            conn.rollback()
            raise Exception(error_msg)

def get_recipes():
    """Get all recipes with their categories."""
    logger.debug("Fetching all recipes")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT r.*, c.name as category_name
                FROM recipes r
                LEFT JOIN categories c ON r.category_id = c.id
                ORDER BY r.title
            """)
            recipes = cur.fetchall()
            logger.debug(f"Retrieved {len(recipes)} recipes")
            return recipes

def get_recipe_ingredients(recipe_id):
    """Get ingredients for a specific recipe."""
    logger.debug(f"Fetching ingredients for recipe {recipe_id}")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT i.name, ri.quantity, ri.unit
                FROM recipe_ingredients ri
                JOIN ingredients i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = %s
            """, (recipe_id,))
            ingredients = cur.fetchall()
            logger.debug(f"Retrieved {len(ingredients)} ingredients for recipe {recipe_id}")
            return ingredients

def get_recipe(recipe_id):
    """Get a specific recipe with all its details."""
    logger.debug(f"Fetching recipe {recipe_id}")
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
                logger.debug(f"Successfully retrieved recipe {recipe_id}")
            else:
                logger.warning(f"Recipe {recipe_id} not found")
            
            return recipe
