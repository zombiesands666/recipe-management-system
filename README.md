# Recipe Management System

A Streamlit-based recipe management application with PostgreSQL database integration. This application allows users to organize, store, and maintain cooking recipes with features for adding, editing, viewing, and searching recipes.

## Features

- User Authentication (Registration and Login)
- Recipe Management (Add, View, Search)
- Category-based Organization
- Ingredient Management
- Measurement Unit Converter
- PWA Support for Mobile Access
- Responsive Design

## Technical Stack

- Frontend: Streamlit
- Backend: Python
- Database: PostgreSQL
- Authentication: Custom implementation with password hashing
- PWA: Service Worker implementation for offline capabilities

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install streamlit psycopg2-binary pillow
```

3. Set up PostgreSQL database and configure environment variables:
- PGHOST
- PGPORT
- PGUSER
- PGPASSWORD
- PGDATABASE

4. Run the application:
```bash
streamlit run main.py
```

## Project Structure

- `main.py`: Main application file with Streamlit UI
- `database.py`: Database connection and operations
- `auth.py`: Authentication functionality
- `conversions.py`: Unit conversion utilities
- `schema.sql`: Database schema
- `static/`: PWA assets and service worker
- `templates/`: HTML templates for PWA

## Features in Detail

1. Recipe Management
   - Add new recipes with title, description, ingredients, and instructions
   - View all recipes with search and category filtering
   - Organize recipes by categories

2. User Authentication
   - Secure user registration and login
   - Password hashing for security
   - User-specific recipe management

3. Unit Converter
   - Convert between metric and imperial measurements
   - Common conversion reference table
   - Support for volume, weight, and temperature

4. PWA Features
   - Mobile-responsive design
   - Offline capability
   - Install prompt for easy access

## License

MIT License
