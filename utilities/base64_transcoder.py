import base64
import numpy as np
import io
from PIL import Image


class Base64_Transcoder():
    
    @staticmethod
    def data_url_to_nparray(data_url: str) -> np.ndarray :
        data_url_array = data_url.split(',')
        if len(data_url_array) < 2:
            raise Exception("Invalid Data URL Format")
        if "base64" not in data_url_array[0]:
            raise Exception("Data URL Does not Contain Base64")
        return Base64_Transcoder.base64_to_nparray(data_url_array[1])

    # Converts image encoded as base64 to numpy image array
    @staticmethod
    def base64_to_nparray(base64_image: str) -> np.ndarray :
        return np.array(Image.open(io.BytesIO(base64.b64decode(base64_image))))#[:, :, ::-1] # This extra array magic could be used to swap the Red and Blue color channels? Just use cv2.cvtColor(image, cv2.COLOR_BGR2RGB) from now on.
    
    # Converts numpy image array to webp image encoded as base64
    @staticmethod
    def nparray_to_base64(nparr_image: np.ndarray) -> str :
        img = Image.fromarray(nparr_image)#[:, :, ::-1])
        buffered = io.BytesIO()
        img.save(buffered, format="webp")
        return base64.b64encode(buffered.getvalue()).decode()
    
    @staticmethod
    def nparray_to_data_url(nparray: np.ndarray) -> str :
        base64 = Base64_Transcoder.nparray_to_base64(nparray)
        return "data:image/webp;base64," + base64