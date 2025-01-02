import cv2
import numpy as np


def pencil_sketch(image_bytes: bytes) -> bytes:
    """Convert an image to a pencil sketch effect using OpenCV and return the sketch as bytes."""
    # Decode the image bytes into an OpenCV image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode the image.")

    # Convert to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image
    img_inverted = cv2.bitwise_not(img_gray)

    # Apply Gaussian Blur to the inverted image
    img_blur = cv2.GaussianBlur(img_inverted, (21, 21), sigmaX=0, sigmaY=0)

    # Blend grayscale and blurred inverted image using the dodge technique
    def dodge(front, back):
        return cv2.divide(front, 255 - back, scale=256)

    img_sketch = dodge(img_gray, img_blur)

    # Encode the resulting sketch back to bytes
    _, buffer = cv2.imencode('.jpg', img_sketch)
    return buffer.tobytes()
