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
    
    # Read and execute the schema file
    with open('schema.sql', 'r') as f:
        cur.execute(f.read())
    
    conn.commit()
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
