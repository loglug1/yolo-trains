import base64
import numpy as np

class Base64_Transcoder():
    @staticmethod
    def base64_to_nparray(base64_image: str) -> np.ndarray :
        return np.frombuffer(base64.decode(str), dtype=np.unint8)
    @staticmethod
    def nparray_to_base64(nparr_image: np.ndarray) -> str :
        return base64.encode()