from PIL import Image, ImageDraw, ImageFont
import os

def generate_icon(size):
    # Create a new image with a white background
    image = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a colored rectangle as background
    draw.rectangle([0, 0, size, size], fill='#f63366')
    
    # Use default font since custom fonts might not be available
    font = ImageFont.load_default()
    
    text = "R"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    draw.text((x, y), text, fill='white', font=font)
    
    # Save the image
    if not os.path.exists('static'):
        os.makedirs('static')
    image.save(f'static/icon-{size}x{size}.png')

if __name__ == "__main__":
    generate_icon(192)
    generate_icon(512)
