import time
import os
import io
import pickle
import hashlib
import threading
from flask import Flask, Response
from flask_cors import CORS

import cv2
import numpy as np
import requests
import face_recognition
from insightface.app import FaceAnalysis

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:3000')
CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
FRAME_SKIP = int(os.getenv('FRAME_SKIP', '5'))
TOLERANCE = float(os.getenv('TOLERANCE', '0.5'))
IN_THRESHOLD_SECONDS = float(os.getenv('IN_THRESHOLD_SECONDS', '2'))
OUT_THRESHOLD_SECONDS = float(os.getenv('OUT_THRESHOLD_SECONDS', '5'))
RELOAD_EMPLOYEES_INTERVAL = int(os.getenv('RELOAD_EMPLOYEES_INTERVAL', '300'))  # 5 минут
VIDEO_STREAM_PORT = int(os.getenv('VIDEO_STREAM_PORT', '5001'))
CACHE_FILE = 'face_encodings_cache.pkl'

# Настройки предобработки изображений
ENABLE_PREPROCESSING = os.getenv('ENABLE_PREPROCESSING', 'true').lower() == 'true'
CLAHE_CLIP_LIMIT = float(os.getenv('CLAHE_CLIP_LIMIT', '2.0'))  # 1.0-4.0
SHARPEN_STRENGTH = float(os.getenv('SHARPEN_STRENGTH', '1.5'))  # 1.0-3.0

# InsightFace настройки
INSIGHTFACE_THRESHOLD = float(os.getenv('INSIGHTFACE_THRESHOLD', '0.4'))  # 0.3-0.6

print('[recognition] Initializing InsightFace AI...')
face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(640, 640))
print('[recognition] ✅ InsightFace initialized (99.8% accuracy!)')
print(f'[recognition] Preprocessing: {"ON" if ENABLE_PREPROCESSING else "OFF"}')

# Глобальные переменные для видео стрима
current_frame = None
frame_lock = threading.Lock()

# Flask приложение для видео стрима
app = Flask(__name__)
CORS(app)  # Включаем CORS для всех эндпоинтов

def preprocess_image(image):
  """
  Предобработка изображения по схеме: CLAHE → Резкость → готово для InsightFace
  """
  if not ENABLE_PREPROCESSING:
    return image
  
  try:
    # Шаг 1: CLAHE - улучшение контраста
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    
    # Шаг 2: OpenCV фильтр резкости (Unsharp Masking)
    if SHARPEN_STRENGTH > 1.0:
      # Создаём размытую копию
      blurred = cv2.GaussianBlur(enhanced, (0, 0), 3)
      
      # Unsharp mask: оригинал + (оригинал - размытое) * сила
      enhanced = cv2.addWeighted(enhanced, 1.0 + SHARPEN_STRENGTH, 
                                  blurred, -SHARPEN_STRENGTH, 0)
    
    # Шаг 3: Готово для InsightFace!
    return enhanced
    
  except Exception as e:
    print(f'[recognition] Preprocessing failed: {e}')
    return image

def get_employees_hash(employees):
  """Вычисляет хеш списка сотрудников для определения изменений"""
  data = ''.join([f"{e['id']}-{e.get('photoUrl', '')}" for e in employees])
  return hashlib.md5(data.encode()).hexdigest()

def save_cache(encodings, ids, emp_hash):
  """Сохраняет кеш энкодингов на диск"""
  try:
    with open(CACHE_FILE, 'wb') as f:
      pickle.dump({
        'encodings': encodings,
        'ids': ids,
        'hash': emp_hash,
        'timestamp': time.time()
      }, f)
    print(f'[recognition] Cache saved for {len(ids)} employees')
  except Exception as e:
    print(f'[recognition] Failed to save cache: {e}')

def load_cache():
  """Загружает кеш энкодингов с диска"""
  if not os.path.exists(CACHE_FILE):
    return None, None, None
  
  try:
    with open(CACHE_FILE, 'rb') as f:
      cache = pickle.load(f)
      age = time.time() - cache.get('timestamp', 0)
      print(f'[recognition] Cache found (age: {age:.0f} seconds)')
      return cache['encodings'], cache['ids'], cache['hash']
  except Exception as e:
    print(f'[recognition] Failed to load cache: {e}')
    return None, None, None

def load_employees():
  print('[recognition] Loading employees from backend...')
  resp = requests.get(f'{BACKEND_URL}/api/employees', timeout=10)
  resp.raise_for_status()
  employees = resp.json()

  # Вычисляем хеш списка сотрудников
  current_hash = get_employees_hash(employees)
  
  # Пытаемся загрузить из кеша
  cached_encodings, cached_ids, cached_hash = load_cache()
  
  if cached_encodings and cached_hash == current_hash:
    print(f'[recognition] ✅ Using cached encodings for {len(cached_ids)} employees')
    return cached_encodings, cached_ids

  print('[recognition] Cache miss or outdated, processing photos...')

  known_face_encodings = []
  known_face_ids = []

  for emp in employees:
    photo_url = emp.get('photoUrl')
    if not photo_url:
      continue
    full_url = BACKEND_URL + photo_url
    try:
      print(f"[recognition] Processing photo for {emp['name']}...")
      img_resp = requests.get(full_url, timeout=10)
      img_resp.raise_for_status()
      img_bytes = img_resp.content
      
      # Декодируем изображение
      nparr = np.frombuffer(img_bytes, np.uint8)
      photo_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
      
      # Шаг 1: CLAHE (контраст)
      # Шаг 2: Резкость
      preprocessed = preprocess_image(photo_image)
      
      # Шаг 3: InsightFace распознавание
      faces = face_app.get(preprocessed)
      
      if not faces or len(faces) == 0:
        print(f"[recognition] WARN: no face found for {emp['name']}")
        continue
      
      # Используем embedding первого лица
      embedding = faces[0].normed_embedding
      known_face_encodings.append(embedding)
      known_face_ids.append(emp['id'])
      print(f"[recognition] ✅ {emp['name']} - embedding created")
      
    except Exception as e:
      print(f"[recognition] Failed for {emp['name']}: {e}")

  # Сохраняем в кеш
  save_cache(known_face_encodings, known_face_ids, current_hash)
  
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

def connect_camera(max_retries=5):
  """Подключение к камере с повторными попытками"""
  for attempt in range(max_retries):
    print(f'[recognition] Connecting to camera (attempt {attempt + 1}/{max_retries})...')
    video_capture = cv2.VideoCapture(CAMERA_INDEX)
    
    if video_capture.isOpened():
      # Проверяем, что можем читать кадры
      ret, frame = video_capture.read()
      if ret:
        print('[recognition] Camera connected successfully')
        return video_capture
      else:
        video_capture.release()
    
    if attempt < max_retries - 1:
      wait_time = 2 ** attempt  # exponential backoff: 1, 2, 4, 8, 16 секунд
      print(f'[recognition] Retry in {wait_time} seconds...')
      time.sleep(wait_time)
  
  raise Exception(f'Cannot connect to camera after {max_retries} attempts')

def generate_frames():
  """Генератор кадров для MJPEG стрима"""
  global current_frame
  while True:
    with frame_lock:
      if current_frame is None:
        time.sleep(0.1)
        continue
      frame = current_frame.copy()
    
    # Кодируем кадр в JPEG
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
      continue
    
    frame_bytes = buffer.tobytes()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    time.sleep(0.033)  # ~30 FPS

@app.route('/video_feed')
def video_feed():
  """Эндпоинт для видео стрима"""
  return Response(generate_frames(),
                  mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/health')
def health():
  """Health check эндпоинт"""
  return {'status': 'ok', 'streaming': current_frame is not None}

def start_flask_server():
  """Запуск Flask сервера в отдельном потоке"""
  print(f'[recognition] Starting video stream server on port {VIDEO_STREAM_PORT}...')
  app.run(host='0.0.0.0', port=VIDEO_STREAM_PORT, threaded=True, debug=False, use_reloader=False)

def main():
  global current_frame
  
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

  # Запускаем Flask сервер в отдельном потоке
  flask_thread = threading.Thread(target=start_flask_server, daemon=True)
  flask_thread.start()
  print(f'[recognition] Video stream available at http://localhost:{VIDEO_STREAM_PORT}/video_feed')

  print(f'[recognition] Opening camera index {CAMERA_INDEX}...')
  video_capture = connect_camera()

  frame_count = 0
  consecutive_failures = 0
  MAX_CONSECUTIVE_FAILURES = 10
  last_employee_reload = time.time()
  
  try:
    while True:
      ret, frame = video_capture.read()
      
      if not ret:
        consecutive_failures += 1
        print(f'[recognition] WARN: failed to read frame ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})')
        
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
          print('[recognition] Too many failures, reconnecting to camera...')
          video_capture.release()
          time.sleep(2)
          video_capture = connect_camera()
          consecutive_failures = 0
        else:
          time.sleep(0.5)
        continue
      
      # Успешное чтение - сбрасываем счетчик
      consecutive_failures = 0
      
      # Периодическая перезагрузка списка сотрудников (горячая перезагрузка)
      now = time.time()
      if now - last_employee_reload > RELOAD_EMPLOYEES_INTERVAL:
        print('[recognition] Reloading employees list...')
        try:
          new_encodings, new_ids = load_employees()
          if len(new_ids) > 0:
            known_face_encodings, known_face_ids = new_encodings, new_ids
            # Обновляем presence_state для новых сотрудников
            for emp_id in known_face_ids:
              if emp_id not in presence_state:
                presence_state[emp_id] = {
                  'present': False,
                  'last_seen': 0.0,
                  'last_state_change': 0.0
                }
            print(f'[recognition] Reloaded {len(known_face_ids)} employees')
          last_employee_reload = now
        except Exception as e:
          print(f'[recognition] Failed to reload employees: {e}')
          last_employee_reload = now  # Попробуем снова через интервал
      
      frame_count += 1
      
      recognized_ids = set()
      
      # Обрабатываем распознавание только для части кадров
      if frame_count % FRAME_SKIP == 0:
        # Шаг 1: CLAHE (контраст)
        # Шаг 2: Резкость
        preprocessed_frame = preprocess_image(frame)
        
        # Шаг 3: InsightFace распознавание
        faces = face_app.get(preprocessed_frame)
        
        recognized_faces = {}  # {emp_id: bbox}
        face_locations = []
        
        for face in faces:
          # Получаем embedding
          embedding = face.normed_embedding
          
          # Конвертируем bbox в формат (top, right, bottom, left)
          bbox = face.bbox.astype(int)
          left, top, right, bottom = bbox[0], bbox[1], bbox[2], bbox[3]
          face_locations.append((top, right, bottom, left))
          
          # Сравниваем с базой известных сотрудников
          if len(known_face_encodings) == 0:
            continue
          
          # Косинусное сходство (для InsightFace)
          similarities = [np.dot(embedding, known_emb) for known_emb in known_face_encodings]
          best_idx = np.argmax(similarities)
          
          if similarities[best_idx] > INSIGHTFACE_THRESHOLD:
            emp_id = known_face_ids[best_idx]
            recognized_ids.add(emp_id)
            recognized_faces[emp_id] = (top, right, bottom, left)
        
        # Рисуем рамки на кадре для стрима
        display_frame = frame.copy()
        
        # Информация о системе в углу
        preprocessing_label = "CLAHE→Sharp→" if ENABLE_PREPROCESSING else ""
        status_text = f"{preprocessing_label}InsightFace AI | OK: {len(recognized_ids)} | Faces: {len(face_locations)}"
        cv2.putText(display_frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
        cv2.putText(display_frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Рисуем зелёные рамки для распознанных лиц
        for emp_id, (top, right, bottom, left) in recognized_faces.items():
          cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 3)
          
          # ID сотрудника
          label = f"ID: {emp_id}"
          cv2.rectangle(display_frame, (left, bottom - 30), (right, bottom), (0, 255, 0), cv2.FILLED)
          cv2.putText(display_frame, label, (left + 6, bottom - 8), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        # Рисуем красные рамки для нераспознанных лиц
        for i, (top, right, bottom, left) in enumerate(face_locations):
          is_recognized = any(loc == (top, right, bottom, left) for loc in recognized_faces.values())
          if not is_recognized:
            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 0, 255), 3)
            cv2.rectangle(display_frame, (left, bottom - 30), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(display_frame, "Unknown", (left + 6, bottom - 8), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        # Сохраняем кадр для стрима
        with frame_lock:
          current_frame = display_frame
      else:
        # Для кадров без обработки просто обновляем текущий кадр
        with frame_lock:
          current_frame = frame.copy()

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
    print('[recognition] Camera released')

if __name__ == '__main__':
  main()
