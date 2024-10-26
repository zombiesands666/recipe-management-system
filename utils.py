import re

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

def parse_ingredient_line(line):
    """Parse an ingredient line into quantity, unit, and ingredient name."""
    # Regular expression to match quantity, unit, and ingredient
    pattern = r'^([\d./\s]+)?\s*([a-zA-Z]+\s+|)(.+)$'
    match = re.match(pattern, line.strip())
    
    if not match:
        return None, None, line.strip()
    
    qty_str, unit, ingredient = match.groups()
    
    # Convert quantity string to float
    try:
        if qty_str:
            # Handle fractions like "1/2"
            if '/' in qty_str:
                num, denom = map(float, qty_str.split('/'))
                quantity = num / denom
            else:
                quantity = float(qty_str)
        else:
            quantity = None
    except ValueError:
        quantity = None
    
    return quantity, unit.strip(), ingredient.strip()

def scale_ingredient_line(line, scale_factor):
    """Scale an ingredient line by the given factor."""
    quantity, unit, ingredient = parse_ingredient_line(line)
    
    if quantity is None:
        return line
    
    scaled_qty = quantity * scale_factor
    
    # Format the scaled quantity
    if scaled_qty.is_integer():
        qty_str = str(int(scaled_qty))
    else:
        # Round to 2 decimal places
        qty_str = f"{scaled_qty:.2f}".rstrip('0').rstrip('.')
    
    # Reconstruct the ingredient line
    if unit:
        return f"{qty_str} {unit} {ingredient}"
    return f"{qty_str} {ingredient}"

def scale_ingredients(ingredients_text, scale_factor):
    """Scale all ingredients in a recipe by the given factor."""
    if not ingredients_text:
        return ingredients_text
        
    lines = ingredients_text.split('\n')
    scaled_lines = [scale_ingredient_line(line, scale_factor) for line in lines if line.strip()]
    return '\n'.join(scaled_lines)
