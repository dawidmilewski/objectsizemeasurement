import base64
import cv2
import numpy as np

MAX_IMAGE_SIDE = 3200


def decode_and_resize_image(file_bytes: bytes) -> np.ndarray:
    buffer = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Nie udało się odczytać pliku obrazu.")

    height, width = image.shape[:2]
    longest_side = max(height, width)
    if longest_side > MAX_IMAGE_SIDE:
        scale = MAX_IMAGE_SIDE / float(longest_side)
        new_size = (max(1, int(round(width * scale))), max(1, int(round(height * scale))))
        image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    return image


def encode_image_to_base64(image: np.ndarray) -> str:
    success, buffer = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    if not success:
        raise RuntimeError("Błąd kodowania podglądu obrazu.")
    encoded = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"