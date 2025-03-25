import base64
import numpy as np
import io
from PIL import Image


class Base64_Transcoder():
    @staticmethod
    def base64_to_nparray(base64_image: str) -> np.ndarray :
        return np.array(Image.open(io.BytesIO(base64.b64decode(base64_image))))[:, :, ::-1] # The additional array shift at the end is to swap the blue and red channels. It still needs further testing.
    @staticmethod
    def nparray_to_base64(nparr_image: np.ndarray) -> str :
        return base64.b64encode(Image.fromarray(nparr_image).tobytes()).decode()