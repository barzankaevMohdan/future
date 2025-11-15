import time
import os
import io

import cv2
import numpy as np
import requests
import face_recognition

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:3000')
CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
FRAME_SKIP = int(os.getenv('FRAME_SKIP', '5'))
TOLERANCE = float(os.getenv('TOLERANCE', '0.5'))
IN_THRESHOLD_SECONDS = float(os.getenv('IN_THRESHOLD_SECONDS', '2'))
OUT_THRESHOLD_SECONDS = float(os.getenv('OUT_THRESHOLD_SECONDS', '5'))

def load_employees():
  print('[recognition] Loading employees from backend...')
  resp = requests.get(f'{BACKEND_URL}/api/employees', timeout=10)
  resp.raise_for_status()
  employees = resp.json()

  known_face_encodings = []
  known_face_ids = []

  for emp in employees:
    photo_url = emp.get('photoUrl')
    if not photo_url:
      continue
    full_url = BACKEND_URL + photo_url
    try:
      print(f"[recognition] Downloading photo for {emp['name']} from {full_url}")
      img_resp = requests.get(full_url, timeout=10)
      img_resp.raise_for_status()
      img_bytes = img_resp.content
      image = face_recognition.load_image_file(io.BytesIO(img_bytes))
      encodings = face_recognition.face_encodings(image)
      if not encodings:
        print(f"[recognition] WARN: no face found in image for employee {emp['id']}")
        continue
      known_face_encodings.append(encodings[0])
      known_face_ids.append(emp['id'])
    except Exception as e:
      print(f"[recognition] Failed to load photo for employee {emp['id']}: {e}")

  print(f'[recognition] Loaded {len(known_face_ids)} employees with photos')
  return known_face_encodings, known_face_ids

def send_event(employee_id, event_type):
  try:
    print(f'[recognition] Sending event {event_type} for employee {employee_id}')
    resp = requests.post(
      f'{BACKEND_URL}/api/events',
      json={'employeeId': employee_id, 'type': event_type},
      timeout=5
    )
    if not resp.ok:
      print('[recognition] Failed to send event:', resp.status_code, resp.text)
  except Exception as e:
    print('[recognition] Error sending event:', e)

def main():
  known_face_encodings, known_face_ids = load_employees()
  if not known_face_ids:
    print('[recognition] No employees with photos found. Add employees via frontend and restart this service.')
    return

  presence_state = {
    emp_id: {
      'present': False,
      'last_seen': 0.0,
      'last_state_change': 0.0
    } for emp_id in known_face_ids
  }

  print(f'[recognition] Opening camera index {CAMERA_INDEX}...')
  video_capture = cv2.VideoCapture(CAMERA_INDEX)
  if not video_capture.isOpened():
    print('[recognition] ERROR: cannot open camera')
    return

  frame_count = 0
  try:
    while True:
      ret, frame = video_capture.read()
      if not ret:
        print('[recognition] WARN: failed to read frame')
        time.sleep(0.5)
        continue

      frame_count += 1
      if frame_count % FRAME_SKIP != 0:
        continue

      rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])

      face_locations = face_recognition.face_locations(rgb_frame)
      face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

      recognized_ids = set()
      for encoding in face_encodings:
        distances = face_recognition.face_distance(known_face_encodings, encoding)
        if len(distances) == 0:
          continue
        best_idx = np.argmin(distances)
        if distances[best_idx] < TOLERANCE:
          emp_id = known_face_ids[best_idx]
          recognized_ids.add(emp_id)

      now = time.time()

      for emp_id, state in presence_state.items():
        if emp_id in recognized_ids:
          state['last_seen'] = now
          if not state['present'] and (now - state['last_state_change'] > IN_THRESHOLD_SECONDS):
            state['present'] = True
            state['last_state_change'] = now
            send_event(emp_id, 'IN')
        else:
          if state['present'] and (now - state['last_seen'] > OUT_THRESHOLD_SECONDS):
            state['present'] = False
            state['last_state_change'] = now
            send_event(emp_id, 'OUT')

      time.sleep(0.05)
  finally:
    video_capture.release()

if __name__ == '__main__':
  main()
