import base64
import numpy as np
import io
from PIL import Image


class Base64_Transcoder():
    
    # Converts image encoded as base64 to numpy image array
    @staticmethod
    def base64_to_nparray(base64_image: str) -> np.ndarray :
        return np.array(Image.open(io.BytesIO(base64.b64decode(base64_image))))[:, :, ::-1] # The additional array shift at the end is to swap the blue and red channels. It still needs further testing.
    
    # Converts numpy image array to webp image encoded as base64
    @staticmethod
    def nparray_to_base64(nparr_image: np.ndarray) -> str :
        img = Image.fromarray(nparr_image[:, :, ::-1])
        buffered = io.BytesIO()
        img.save(buffered, format="webp")
        return base64.b64encode(buffered.getvalue()).decode()