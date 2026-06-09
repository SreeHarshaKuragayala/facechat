import face_recognition
import numpy as np
from database.models import get_all_users_with_encodings

TOLERANCE = 0.55


def encode_face(image_bgr):
    # Convert BGR (OpenCV) to RGB (face_recognition expects RGB)
    rgb = image_bgr[:, :, ::-1]

    # Make sure image is uint8 and contiguous in memory
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)

    # First detect face locations, then encode only those locations
    face_locations = face_recognition.face_locations(rgb, model="hog")

    if not face_locations:
        return None

    # Pass locations explicitly — fixes the argument mismatch error
    encodings = face_recognition.face_encodings(rgb, known_face_locations=face_locations)

    return encodings[0] if encodings else None


def identify_face(unknown_encoding):
    known_users = get_all_users_with_encodings()
    if not known_users:
        return None

    known_encodings = [u["encoding"] for u in known_users]
    distances = face_recognition.face_distance(known_encodings, unknown_encoding)
    min_idx = np.argmin(distances)

    if distances[min_idx] < TOLERANCE:
        return known_users[min_idx]
    return None