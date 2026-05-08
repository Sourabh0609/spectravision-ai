import cv2
import numpy as np
from pathlib import Path

ROOT_DIR = Path(__file__).parent
MODELS_DIR = ROOT_DIR / 'models'

class Colorizer:
    def __init__(self):
        # Load the model files
        prototxt = str(MODELS_DIR / 'colorization_deploy_v2.prototxt')
        caffemodel = str(MODELS_DIR / 'colorization_release_v2.caffemodel')
        pts_npy = str(MODELS_DIR / 'pts_in_hull.npy')
        
        # Load the colorization network
        self.net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
        
        # Load cluster centers
        pts = np.load(pts_npy)
        
        # Add the cluster centers as 1x1 convolutions to the model
        class8 = self.net.getLayerId("class8_ab")
        conv8 = self.net.getLayerId("conv8_313_rh")
        pts = pts.transpose().reshape(2, 313, 1, 1)
        self.net.getLayer(class8).blobs = [pts.astype("float32")]
        self.net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]
    
    def colorize(self, image_path, output_path):
        # Load the input image
        image = cv2.imread(image_path)
        
        # Convert to grayscale if not already
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # Scale the pixel intensities to the range [0, 1]
        scaled = gray.astype("float32") / 255.0
        
        # Convert from BGR to LAB color space
        lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)
        
        # Resize to 224x224 (expected input size)
        resized = cv2.resize(lab, (224, 224))
        
        # Extract L channel
        L = cv2.split(resized)[0]
        L -= 50  # Mean centering
        
        # Predict a and b channels
        self.net.setInput(cv2.dnn.blobFromImage(L))
        ab = self.net.forward()[0, :, :, :].transpose((1, 2, 0))
        
        # Resize predicted ab channels back to original image size
        ab = cv2.resize(ab, (image.shape[1], image.shape[0]))
        
        # Extract L channel from original image
        L = cv2.split(lab)[0]
        
        # Concatenate L channel with predicted ab channels
        colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
        
        # Convert from LAB to BGR
        colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
        colorized = np.clip(colorized, 0, 1)
        
        # Convert back to 0-255 range
        colorized = (255 * colorized).astype("uint8")
        
        # Save the output image
        cv2.imwrite(output_path, colorized)
        
        return output_path