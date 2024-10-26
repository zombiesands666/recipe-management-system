CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    cooking_time INTEGER NOT NULL,
    image_data BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
