import requests
from bs4 import BeautifulSoup
import re
import json

def extract_recipe_from_url(url):
    """Extract recipe information from a given URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find recipe data in JSON-LD format
        json_ld = soup.find('script', {'type': 'application/ld+json'})
        if json_ld:
            data = json.loads(json_ld.string)
            if isinstance(data, list):
                data = next((item for item in data if '@type' in item and item['@type'] == 'Recipe'), None)
            if data and data.get('@type') == 'Recipe':
                return {
                    'title': data.get('name', ''),
                    'description': data.get('description', ''),
                    'instructions': data.get('recipeInstructions', ''),
                    'ingredients': data.get('recipeIngredient', []),
                    'cooking_time': parse_cooking_time(data.get('cookTime', '')),
                    'servings': parse_servings(data.get('recipeYield', '')),
                }
        
        # Fallback to basic HTML parsing
        return {
            'title': extract_text(soup.find(['h1', 'h2'], class_=re.compile('title|heading', re.I))),
            'description': extract_text(soup.find(['p', 'div'], class_=re.compile('description|summary', re.I))),
            'instructions': extract_instructions(soup),
            'ingredients': extract_ingredients(soup),
            'cooking_time': 0,
            'servings': 0,
        }
    except Exception as e:
        print(f"Error extracting recipe from URL: {e}")
        return None

def parse_cooking_time(time_str):
    """Parse cooking time from ISO duration or text."""
    if not time_str:
        return 0
    
    # Try to parse ISO duration
    match = re.search(r'PT(\d+)M', time_str)
    if match:
        return int(match.group(1))
    
    # Try to parse numeric value
    match = re.search(r'(\d+)\s*(?:min|minute)', time_str, re.I)
    if match:
        return int(match.group(1))
    
    return 0

def parse_servings(servings_str):
    """Parse number of servings from string."""
    if not servings_str:
        return 0
    
    # Try to extract numeric value
    match = re.search(r'(\d+)', str(servings_str))
    if match:
        return int(match.group(1))
    
    return 0

def extract_text(element):
    """Extract text from a BeautifulSoup element safely."""
    return element.get_text(strip=True) if element else ''

def extract_instructions(soup):
    """Extract cooking instructions from HTML."""
    instructions = []
    
    # Look for common instruction containers
    instruction_elements = soup.find_all(['ol', 'ul'], class_=re.compile('instruction|direction|step', re.I))
    if not instruction_elements:
        instruction_elements = soup.find_all(['li', 'p'], class_=re.compile('instruction|direction|step', re.I))
    
    for element in instruction_elements:
        text = extract_text(element)
        if text:
            instructions.append(text)
    
    return '\n'.join(instructions) if instructions else ''

def extract_ingredients(soup):
    """Extract ingredients from HTML."""
    ingredients = []
    
    # Look for ingredient lists
    ingredient_elements = soup.find_all(['li', 'p'], class_=re.compile('ingredient', re.I))
    
    for element in ingredient_elements:
        text = extract_text(element)
        if text:
            ingredients.append(text)
    
    return ingredients
