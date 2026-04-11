import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)

class VideoPreprocessor:
    """
    Implements the visual pre-processing pipeline described in Paper 2.
    Specifically, it applies Contrast Limited Adaptive Histogram Equalization (CLAHE)
    to handle variable lighting conditions (e.g., projector glare, dimmed lights)
    typical in lecture halls.
    """
    
    def __init__(self, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Initializes the CLAHE processor.
        
        Args:
            clip_limit (float): Threshold for contrast limiting.
            tile_grid_size (tuple): Size of grid for histogram equalization.
        """
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        logger.info(f"✅ VideoPreprocessor (CLAHE) initialized: clip_limit={clip_limit}, tile={tile_grid_size}")
        
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Applies CLAHE to the input RGB frame.
        
        Args:
            frame (np.ndarray): Original RGB frame.
            
        Returns:
            np.ndarray: Contrast-enhanced RGB frame.
        """
        # CLAHE is typically applied to the Lightness channel in LAB color space
        # to enhance contrast without altering color balance.
        try:
            lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            
            # Apply CLAHE to L-channel
            cl = self.clahe.apply(l_channel)
            
            # Merge back and convert to RGB
            merged = cv2.merge((cl, a_channel, b_channel))
            enhanced_frame = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
            return enhanced_frame
        except Exception as e:
            logger.error(f"⚠️ CLAHE processing failed: {e}. Returning original frame.")
            return frame
