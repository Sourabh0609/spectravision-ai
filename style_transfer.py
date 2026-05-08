import cv2
import numpy as np

def apply_style_transfer(input_path, output_path, style='pencil'):
    """
    Apply artistic filters to images (works on BOTH B&W and Color images)
    """
    # Load image
    image = cv2.imread(input_path)
    
    # If image is grayscale (2D), convert to 3-channel BGR
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    # ============================================
    # FILTER 1: PENCIL SKETCH (Black & White drawing)
    # ============================================
    if style == 'pencil':
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        inverted_blur = cv2.bitwise_not(blurred)
        sketch = cv2.divide(gray, inverted_blur, scale=256.0)
        result = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    # ============================================
    # FILTER 2: CARTOON (Preserves colors + strong edges)
    # ============================================
    elif style == 'cartoon':
        # Step 1: Smooth colors while keeping edges
        color = cv2.bilateralFilter(image, 9, 300, 300)
        
        # Step 2: Create strong edge mask
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, 
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)
        
        # Step 3: Combine smooth color with edges
        result = cv2.bitwise_and(color, color, mask=edges)
    
    # ============================================
    # FILTER 3: WATERCOLOR (Painterly effect)
    # ============================================
    elif style == 'watercolor':
        result = cv2.stylization(image, sigma_s=60, sigma_r=0.6)
    
    # ============================================
    # FILTER 4: OIL PAINTING (Impressionist style)
    # ============================================
    elif style == 'oil_painting':
        result = cv2.edgePreservingFilter(image, flags=2, sigma_s=60, sigma_r=0.4)
    
    # ============================================
    # FILTER 5: HDR EFFECT (Enhances colors and details)
    # ============================================
    elif style == 'hdr':
        result = cv2.detailEnhance(image, sigma_s=12, sigma_r=0.15)
    
    # ============================================
    # FILTER 6: SEPIA (Vintage brown tone)
    # ============================================
    elif style == 'sepia':
        # Sepia kernel matrix
        sepia_kernel = np.array([[0.272, 0.534, 0.131],
                                  [0.349, 0.686, 0.168],
                                  [0.393, 0.769, 0.189]])
        result = cv2.transform(image, sepia_kernel)
        result = np.clip(result, 0, 255).astype(np.uint8)
    
    # ============================================
    # FILTER 7: BLUR EFFECT (Soft focus)
    # ============================================
    elif style == 'blur':
        result = cv2.GaussianBlur(image, (15, 15), 0)
    
    # ============================================
    # FILTER 8: EDGE DETECTION (Line art)
    # ============================================
    elif style == 'edge':
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        result = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # ============================================
    # DEFAULT: Pencil sketch
    # ============================================
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        inverted_blur = cv2.bitwise_not(blurred)
        sketch = cv2.divide(gray, inverted_blur, scale=256.0)
        result = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    # Save result
    cv2.imwrite(output_path, result)
