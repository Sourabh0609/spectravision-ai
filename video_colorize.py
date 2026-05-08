import cv2
import numpy as np
from pathlib import Path

__all__ = ["colorize_video"]

def colorize_video(input_path, output_path, progress_callback=None):
    """
    Colorize a video file frame by frame
    
    Args:
        input_path: Path to input video
        output_path: Path to save colorized video
        progress_callback: Optional callback function for progress updates
    """
    # Delay importing the Colorizer class so import-time failures don't hide the function
    try:
        from colorize import Colorizer
    except Exception as e:
        raise ImportError("Failed to import Colorizer from colorize module: " + str(e))

    # Initialize colorizer
    colorizer = Colorizer()
    
    # Open input video
    cap = cv2.VideoCapture(input_path)
    
    if not cap.isOpened():
        raise ValueError("Could not open video file")
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Define the codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert frame to grayscale and back to BGR
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # Scale pixel intensities
        scaled = gray.astype("float32") / 255.0
        
        # Convert to LAB color space
        lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)
        
        # Resize to 224x224 for the model
        resized = cv2.resize(lab, (224, 224))
        
        # Extract L channel
        L = cv2.split(resized)[0]
        L -= 50  # Mean centering
        
        # Predict a and b channels
        colorizer.net.setInput(cv2.dnn.blobFromImage(L))
        ab = colorizer.net.forward()[0, :, :, :].transpose((1, 2, 0))
        
        # Resize back to original frame size
        ab = cv2.resize(ab, (width, height))
        
        # Extract L channel from original frame
        L = cv2.split(lab)[0]
        
        # Concatenate L with predicted ab
        colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
        
        # Convert from LAB to BGR
        colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
        colorized = np.clip(colorized, 0, 1)
        
        # Convert back to 0-255 range
        colorized_frame = (255 * colorized).astype("uint8")
        
        # Write the frame
        out.write(colorized_frame)
        
        frame_count += 1
        
        # Progress update (optional)
        if progress_callback and frame_count % 10 == 0:
            progress = (frame_count / total_frames) * 100
            progress_callback(progress)
    
    # Release everything
    cap.release()
    out.release()
    
    return output_path