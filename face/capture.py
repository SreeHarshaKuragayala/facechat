import cv2
import os
import time
import random
from datetime import datetime
from config.settings import SNAPSHOTS_DIR
from database.models import save_snapshot

try:
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
except FileExistsError:
    pass

def capture_frame(cap):
    ret, frame = cap.read()
    return frame if ret else None

def save_face_photo(frame, user_name, faces_dir):
    os.makedirs(faces_dir, exist_ok=True)
    filename = f"{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    path = os.path.join(faces_dir, filename)
    cv2.imwrite(path, frame)
    return path

class RandomSnapshotter:
    def __init__(self, session_id, interval_range=(30, 90)):
        self.session_id = session_id
        self.interval_range = interval_range
        self.next_snap_time = time.time() + random.randint(*interval_range)

    def check_and_snap(self, frame):
        if time.time() >= self.next_snap_time:
            filename = f"snap_{self.session_id}_{datetime.now().strftime('%H%M%S')}.jpg"
            path = os.path.join(SNAPSHOTS_DIR, filename)
            cv2.imwrite(path, frame)
            save_snapshot(self.session_id, path)
            self.next_snap_time = time.time() + random.randint(*self.interval_range)
            print(f"[📸 Snapshot saved: {path}]")