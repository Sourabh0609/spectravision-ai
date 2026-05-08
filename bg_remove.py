from rembg import remove
from PIL import Image
import numpy as np

def remove_background(input_path, output_path):
    # Open input image (works for both B&W and Color)
    input_image = Image.open(input_path)
    
    # Convert to RGB if it's grayscale (rembg expects RGB)
    if input_image.mode == 'L':  # L = Grayscale
        input_image = input_image.convert('RGB')
    elif input_image.mode == 'RGBA':
        input_image = input_image.convert('RGB')
    
    # Remove background
    output_image = remove(input_image)
    
    # Save output image (PNG supports transparency)
    output_image.save(output_path, 'PNG')
    
    return output_path