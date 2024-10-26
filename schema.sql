-- Create tables for recipe management system

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    instructions TEXT NOT NULL,
    cooking_time INTEGER,
    servings INTEGER,
    category_id INTEGER REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ingredients table
CREATE TABLE IF NOT EXISTS ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Recipe_ingredients junction table
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
    quantity DECIMAL NOT NULL,
    unit VARCHAR(50),
    PRIMARY KEY (recipe_id, ingredient_id)
);

-- Insert some default categories
INSERT INTO categories (name) VALUES 
    ('Breakfast'),
    ('Lunch'),
    ('Dinner'),
    ('Dessert'),
    ('Snack')
ON CONFLICT (name) DO NOTHING;
