import cv2
from style_transfer import apply_style_transfer

# Test with a color image
input_img = "path/to/your/color_image.jpg"  # Change this
output_img = "test_output.jpg"

apply_style_transfer(input_img, output_img, style='cartoon')
print(f"Filter applied! Check {output_img}")
