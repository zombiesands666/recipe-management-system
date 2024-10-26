def validate_recipe_input(title, category, ingredients, instructions, cooking_time):
    """Validate recipe input data."""
    errors = []
    
    if not title or len(title.strip()) < 3:
        errors.append("Title must be at least 3 characters long")
    
    if not category:
        errors.append("Category must be selected")
    
    if not ingredients or len(ingredients.strip()) < 10:
        errors.append("Ingredients must be at least 10 characters long")
    
    if not instructions or len(instructions.strip()) < 30:
        errors.append("Instructions must be at least 30 characters long")
    
    if not cooking_time or cooking_time < 1:
        errors.append("Cooking time must be at least 1 minute")
    
    return errors

def format_time(minutes):
    """Format cooking time from minutes to hours and minutes."""
    hours = minutes // 60
    mins = minutes % 60
    
    if hours > 0:
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    return f"{mins}m"
