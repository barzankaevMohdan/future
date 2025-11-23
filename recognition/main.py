#!/usr/bin/env python3
"""
Recognition Service - Рефакторенная версия
Архитектура: Quality Check → Preprocessing → InsightFace → Tracking → Presence Logic
"""

import time
import os
import io
import pickle
import hashlib
import threading
import logging
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass
from flask import Flask, Response
from flask_cors import CORS

import cv2
import numpy as np
import requests
from insightface.app import FaceAnalysis


# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

@dataclass
class Config:
    """Централизованная конфигурация системы"""
    
    # Backend
    backend_url: str = os.getenv('BACKEND_URL', 'http://localhost:3000')
    
    # Camera
    camera_source: str = os.getenv('CAMERA_SOURCE', '0')
    frame_skip: int = int(os.getenv('FRAME_SKIP', '3'))
    
    # Quality thresholds
    min_face_height_pixels: int = int(os.getenv('MIN_FACE_HEIGHT', '20'))
    min_blur_variance: float = float(os.getenv('MIN_BLUR_VAR', '50.0'))
    
    # Preprocessing
    enable_preprocessing: bool = os.getenv('ENABLE_PREPROCESSING', 'true').lower() == 'true'
    clahe_clip_limit: float = float(os.getenv('CLAHE_CLIP', '2.0'))
    denoise_strength: int = int(os.getenv('DENOISE_STRENGTH', '5'))
    
    # InsightFace
    insightface_threshold: float = float(os.getenv('INSIGHTFACE_THRESHOLD', '0.2'))
    insightface_det_size: Tuple[int, int] = (640, 640)
    
    # Tracking
    min_good_embeddings_per_track: int = int(os.getenv('MIN_EMBEDDINGS', '2'))
    track_max_age_seconds: float = float(os.getenv('TRACK_MAX_AGE', '2.0'))
    iou_threshold: float = 0.3
    
    # Presence logic
    in_threshold_seconds: float = float(os.getenv('IN_THRESHOLD', '1.0'))
    out_threshold_seconds: float = float(os.getenv('OUT_THRESHOLD', '10.0'))
    
    # System
    reload_employees_interval: int = int(os.getenv('RELOAD_INTERVAL', '300'))
    video_stream_port: int = int(os.getenv('VIDEO_PORT', '5001'))
    cache_file: str = 'face_encodings_cache.pkl'
    
    # Logging
    debug_mode: bool = os.getenv('DEBUG', 'true').lower() == 'true'


config = Config()

# ============================================================================
# ЛОГИРОВАНИЕ
# ============================================================================

logging.basicConfig(
    level=logging.DEBUG if config.debug_mode else logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger('recognition')


# ============================================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# ============================================================================

current_frame = None
frame_lock = threading.Lock()

# Flask приложение
app = Flask(__name__)
CORS(app)

# InsightFace инициализация
logger.info('Initializing InsightFace AI...')
face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=config.insightface_det_size)
logger.info(f'✅ InsightFace initialized (det_size={config.insightface_det_size})')


# ============================================================================
# 1. ОЦЕНКА КАЧЕСТВА ЛИЦА
# ============================================================================

def compute_blur_score(gray_face: np.ndarray) -> float:
    """
    Вычисляет метрику размытия через вариацию Лапласиана.
    Чем выше значение - тем резче изображение.
    """
    return cv2.Laplacian(gray_face, cv2.CV_64F).var()


def is_face_acceptable(face_img_bgr: np.ndarray, bbox: np.ndarray) -> Tuple[bool, Dict]:
    """
    Проверяет качество лица для распознавания.
    
    Returns:
        (acceptable, metrics) где metrics содержит height, blur_score и т.д.
    """
    try:
        # Метрика 1: Размер лица
        x1, y1, x2, y2 = bbox.astype(int)
        face_height = y2 - y1
        face_width = x2 - x1
        
        # Метрика 2: Размытие
        gray_face = cv2.cvtColor(face_img_bgr, cv2.COLOR_BGR2GRAY)
        blur_score = compute_blur_score(gray_face)
        
        # Метрика 3: Яркость (дополнительно)
        mean_brightness = np.mean(gray_face)
        
        metrics = {
            'height': face_height,
            'width': face_width,
            'blur_score': blur_score,
            'brightness': mean_brightness
        }
        
        # Проверка порогов
        if face_height < config.min_face_height_pixels:
            logger.debug(f'Face rejected: too small ({face_height}px < {config.min_face_height_pixels}px)')
            return False, metrics
        
        if blur_score < config.min_blur_variance:
            logger.debug(f'Face rejected: too blurry (score={blur_score:.1f} < {config.min_blur_variance})')
            return False, metrics
        
        logger.debug(f'Face accepted: h={face_height}px, blur={blur_score:.1f}, bright={mean_brightness:.1f}')
        return True, metrics
        
    except Exception as e:
        logger.error(f'Quality check failed: {e}')
        return False, {}


# ============================================================================
# 2. ПРЕПРОЦЕССИНГ ЛИЦА
# ============================================================================

def preprocess_face_for_insightface(face_bgr: np.ndarray) -> np.ndarray:
    """
    Подготавливает лицо для InsightFace:
    - Денойзинг (мягкий)
    - CLAHE (только по яркости)
    - Unsharp mask (мягкий)
    """
    if not config.enable_preprocessing:
        return face_bgr
    
    try:
        # Шаг 1: Мягкий денойзинг (сохраняем детали)
        denoised = cv2.fastNlMeansDenoisingColored(
            face_bgr, None,
            h=config.denoise_strength,
            hColor=config.denoise_strength,
            templateWindowSize=7,
            searchWindowSize=21
        )
        
        # Шаг 2: CLAHE только по яркости (не трогаем цвет)
        # Используем YCrCb для лучшего результата
        ycrcb = cv2.cvtColor(denoised, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        
        clahe = cv2.createCLAHE(
            clipLimit=config.clahe_clip_limit,
            tileGridSize=(8, 8)
        )
        y = clahe.apply(y)
        
        enhanced = cv2.cvtColor(cv2.merge([y, cr, cb]), cv2.COLOR_YCrCb2BGR)
        
        # Шаг 3: Мягкий unsharp mask (резкость без артефактов)
        gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
        sharpened = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
        
        return sharpened
        
    except Exception as e:
        logger.error(f'Preprocessing failed: {e}')
        return face_bgr


# ============================================================================
# 3. ТРЕКИНГ ЛИЦ
# ============================================================================

class FaceTrack:
    """Трек одного лица в видеопотоке"""
    
    def __init__(self, track_id: int):
        self.track_id = track_id
        self.embeddings: List[np.ndarray] = []
        self.quality_scores: List[Dict] = []
        self.last_bbox: Optional[np.ndarray] = None
        self.last_update_time: float = time.time()
        self.recognized_employee_id: Optional[int] = None
        self.recognition_confidence: float = 0.0
    
    def add_embedding(self, embedding: np.ndarray, quality: Dict, bbox: np.ndarray):
        """Добавляет хороший эмбеддинг в трек"""
        self.embeddings.append(embedding)
        self.quality_scores.append(quality)
        self.last_bbox = bbox
        self.last_update_time = time.time()
        logger.debug(f'Track {self.track_id}: added embedding (total: {len(self.embeddings)})')
    
    def is_ready_for_recognition(self) -> bool:
        """Достаточно ли эмбеддингов для надёжного распознавания"""
        return len(self.embeddings) >= config.min_good_embeddings_per_track
    
    def get_average_embedding(self) -> np.ndarray:
        """Усреднённый эмбеддинг (более надёжный чем один кадр)"""
        if not self.embeddings:
            return None
        return np.mean(self.embeddings, axis=0)
    
    def is_alive(self) -> bool:
        """Жив ли трек (недавно обновлялся)"""
        return (time.time() - self.last_update_time) < config.track_max_age_seconds


def compute_iou(bbox1: np.ndarray, bbox2: np.ndarray) -> float:
    """Intersection over Union для bounding boxes"""
    x1_min, y1_min, x1_max, y1_max = bbox1
    x2_min, y2_min, x2_max, y2_max = bbox2
    
    # Пересечение
    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)
    
    inter_area = max(0, inter_x_max - inter_x_min) * max(0, inter_y_max - inter_y_min)
    
    # Объединение
    bbox1_area = (x1_max - x1_min) * (y1_max - y1_min)
    bbox2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = bbox1_area + bbox2_area - inter_area
    
    if union_area == 0:
        return 0.0
    
    return inter_area / union_area


class FaceTracker:
    """Менеджер треков лиц"""
    
    def __init__(self):
        self.tracks: List[FaceTrack] = []
        self.next_track_id = 1
    
    def update(self, faces, known_embeddings, known_ids) -> List[FaceTrack]:
        """
        Обновляет треки на основе детектированных лиц.
        
        Returns:
            List активных треков с распознанными сотрудниками
        """
        current_time = time.time()
        
        # Удаляем мёртвые треки
        self.tracks = [t for t in self.tracks if t.is_alive()]
        
        # Сопоставляем детектированные лица с существующими треками
        matched_track_ids = set()
        
        for face in faces:
            bbox = face.bbox
            embedding = face.normed_embedding
            
            # Проверяем качество лица
            x1, y1, x2, y2 = bbox.astype(int)
            face_crop = current_frame[y1:y2, x1:x2] if current_frame is not None else None
            
            if face_crop is None or face_crop.size == 0:
                continue
            
            acceptable, quality = is_face_acceptable(face_crop, bbox)
            
            if not acceptable:
                # Плохое качество - пропускаем
                continue
            
            # Ищем подходящий существующий трек
            best_track = None
            best_iou = 0.0
            
            for track in self.tracks:
                if track.track_id in matched_track_ids:
                    continue
                if track.last_bbox is None:
                    continue
                
                iou = compute_iou(bbox, track.last_bbox)
                if iou > config.iou_threshold and iou > best_iou:
                    best_iou = iou
                    best_track = track
            
            # Обновляем существующий трек или создаём новый
            if best_track:
                # Препроцессинг лица
                preprocessed = preprocess_face_for_insightface(face_crop)
                
                best_track.add_embedding(embedding, quality, bbox)
                matched_track_ids.add(best_track.track_id)
                
                # Пытаемся распознать если достаточно эмбеддингов
                if best_track.is_ready_for_recognition() and not best_track.recognized_employee_id:
                    avg_embedding = best_track.get_average_embedding()
                    emp_id, confidence = match_embedding_to_employee(
                        avg_embedding, known_embeddings, known_ids
                    )
                    
                    if emp_id:
                        best_track.recognized_employee_id = emp_id
                        best_track.recognition_confidence = confidence
                        logger.info(
                            f'Track {best_track.track_id} → Employee {emp_id} '
                            f'(confidence: {confidence:.3f}, embeddings: {len(best_track.embeddings)})'
                        )
            else:
                # Создаём новый трек
                new_track = FaceTrack(self.next_track_id)
                self.next_track_id += 1
                
                # Препроцессинг
                preprocessed = preprocess_face_for_insightface(face_crop)
                
                new_track.add_embedding(embedding, quality, bbox)
                self.tracks.append(new_track)
                logger.debug(f'Created new track {new_track.track_id}')
        
        # Возвращаем распознанные треки
        return [t for t in self.tracks if t.recognized_employee_id is not None]


def match_embedding_to_employee(
    embedding: np.ndarray,
    known_embeddings: List[np.ndarray],
    known_ids: List[int]
) -> Tuple[Optional[int], float]:
    """
    Сравнивает эмбеддинг с базой сотрудников.
    
    Returns:
        (employee_id, confidence) или (None, 0.0)
    """
    if len(known_embeddings) == 0:
        return None, 0.0
    
    # Косинусное сходство (для InsightFace normalized embeddings)
    similarities = [np.dot(embedding, known_emb) for known_emb in known_embeddings]
    best_idx = np.argmax(similarities)
    best_similarity = similarities[best_idx]
    
    if best_similarity > config.insightface_threshold:
        return known_ids[best_idx], best_similarity
    
    logger.debug(f'No match: best similarity {best_similarity:.3f} < threshold {config.insightface_threshold}')
    return None, 0.0


# ============================================================================
# 4. ЛОГИКА ПРИСУТСТВИЯ (IN/OUT)
# ============================================================================

class PresenceManager:
    """Управление состоянием присутствия сотрудников"""
    
    def __init__(self, employee_ids: List[int]):
        self.state = {
            emp_id: {
                'present': False,
                'last_seen': 0.0,
                'last_state_change': 0.0
            }
            for emp_id in employee_ids
        }
    
    def update(self, recognized_employee_ids: List[int]):
        """
        Обновляет состояния на основе распознанных лиц.
        
        Returns:
            List[Tuple[employee_id, event_type]] - события для отправки
        """
        now = time.time()
        events = []
        
        # Обновляем last_seen для распознанных
        for emp_id in recognized_employee_ids:
            if emp_id in self.state:
                self.state[emp_id]['last_seen'] = now
        
        # Проверяем логику IN/OUT для каждого сотрудника
        for emp_id, state in self.state.items():
            if emp_id in recognized_employee_ids:
                # Сотрудник виден в кадре
                if not state['present']:
                    # Был отсутствующим, проверяем порог
                    time_since_change = now - state['last_state_change']
                    if time_since_change > config.in_threshold_seconds:
                        # Достаточно времени прошло - фиксируем приход
                        state['present'] = True
                        state['last_state_change'] = now
                        events.append((emp_id, 'IN'))
                        logger.info(
                            f'✅ Employee {emp_id} marked as IN '
                            f'(stable presence {time_since_change:.1f}s)'
                        )
            else:
                # Сотрудник не виден
                if state['present']:
                    time_since_seen = now - state['last_seen']
                    if time_since_seen > config.out_threshold_seconds:
                        # Давно не видели - фиксируем уход
                        state['present'] = False
                        state['last_state_change'] = now
                        events.append((emp_id, 'OUT'))
                        logger.info(
                            f'✅ Employee {emp_id} marked as OUT '
                            f'(absent {time_since_seen:.1f}s)'
                        )
        
        return events
    
    def add_employee(self, emp_id: int):
        """Добавляет нового сотрудника в отслеживание"""
        if emp_id not in self.state:
            self.state[emp_id] = {
                'present': False,
                'last_seen': 0.0,
                'last_state_change': 0.0
            }


# ============================================================================
# УТИЛИТЫ
# ============================================================================

def get_employees_hash(employees: List[Dict]) -> str:
    """Хеш списка сотрудников для определения изменений"""
    data = ''.join([f"{e['id']}-{e.get('photoUrl', '')}" for e in employees])
    return hashlib.md5(data.encode()).hexdigest()


def save_cache(encodings: List, ids: List, emp_hash: str):
    """Сохраняет кеш эмбеддингов"""
    try:
        with open(config.cache_file, 'wb') as f:
            pickle.dump({
                'encodings': encodings,
                'ids': ids,
                'hash': emp_hash,
                'timestamp': time.time()
            }, f)
        logger.info(f'Cache saved for {len(ids)} employees')
    except Exception as e:
        logger.error(f'Failed to save cache: {e}')


def load_cache() -> Tuple[Optional[List], Optional[List], Optional[str]]:
    """Загружает кеш эмбеддингов"""
    if not os.path.exists(config.cache_file):
        return None, None, None
    
    try:
        with open(config.cache_file, 'rb') as f:
            cache = pickle.load(f)
            age = time.time() - cache.get('timestamp', 0)
            logger.info(f'Cache found (age: {age:.0f} seconds)')
            return cache['encodings'], cache['ids'], cache['hash']
    except Exception as e:
        logger.error(f'Failed to load cache: {e}')
        return None, None, None


def load_employees() -> Tuple[List[np.ndarray], List[int]]:
    """Загружает сотрудников из backend и создаёт эмбеддинги"""
    logger.info('Loading employees from backend...')
    resp = requests.get(f'{config.backend_url}/api/employees', timeout=10)
    resp.raise_for_status()
    employees = resp.json()
    
    # Проверяем кеш
    current_hash = get_employees_hash(employees)
    cached_encodings, cached_ids, cached_hash = load_cache()
    
    if cached_encodings and cached_hash == current_hash:
        logger.info(f'✅ Using cached encodings for {len(cached_ids)} employees')
        return cached_encodings, cached_ids
    
    logger.info('Cache miss, processing photos...')
    
    known_embeddings = []
    known_ids = []
    
    for emp in employees:
        photo_url = emp.get('photoUrl')
        if not photo_url:
            continue
        
        full_url = config.backend_url + photo_url
        
        try:
            logger.info(f"Processing photo for {emp['name']}...")
            img_resp = requests.get(full_url, timeout=10)
            img_resp.raise_for_status()
            
            # Декодируем изображение
            nparr = np.frombuffer(img_resp.content, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Препроцессинг
            preprocessed = preprocess_face_for_insightface(image)
            
            # InsightFace детекция и эмбеддинг
            faces = face_app.get(preprocessed)
            
            if not faces:
                logger.warning(f"No face found for {emp['name']}")
                continue
            
            # Проверяем качество
            face = faces[0]
            face_crop = image  # Для проверки качества берём оригинал
            acceptable, quality = is_face_acceptable(face_crop, face.bbox)
            
            if not acceptable:
                logger.warning(
                    f"Face quality too low for {emp['name']}: "
                    f"height={quality.get('height')}px, blur={quality.get('blur_score', 0):.1f}"
                )
                continue
            
            # Сохраняем эмбеддинг
            embedding = face.normed_embedding
            known_embeddings.append(embedding)
            known_ids.append(emp['id'])
            
            logger.info(
                f"✅ {emp['name']} - embedding created "
                f"(quality: h={quality.get('height')}px, blur={quality.get('blur_score', 0):.1f})"
            )
            
        except Exception as e:
            logger.error(f"Failed for {emp.get('name', 'unknown')}: {e}")
    
    # Сохраняем кеш
    save_cache(known_embeddings, known_ids, current_hash)
    
    logger.info(f'Loaded {len(known_ids)} employees with photos')
    return known_embeddings, known_ids


def send_event(employee_id: int, event_type: str):
    """Отправляет событие IN/OUT в backend"""
    try:
        logger.info(f'📤 Sending event {event_type} for employee {employee_id}')
        resp = requests.post(
            f'{config.backend_url}/api/events',
            json={'employeeId': employee_id, 'type': event_type},
            timeout=5
        )
        if not resp.ok:
            logger.error(f'Failed to send event: {resp.status_code} {resp.text}')
    except Exception as e:
        logger.error(f'Error sending event: {e}')


def connect_camera(max_retries=5) -> cv2.VideoCapture:
    """Подключается к камере с повторными попытками"""
    
    # Определяем тип источника
    if config.camera_source.isdigit():
        camera_type = 'local'
        camera_index = int(config.camera_source)
    elif config.camera_source.startswith('rtsp://') or config.camera_source.startswith('http://'):
        camera_type = 'stream'
        camera_url = config.camera_source
    else:
        camera_type = 'local'
        camera_index = 0
    
    for attempt in range(max_retries):
        if camera_type == 'local':
            logger.info(f'Connecting to local camera {camera_index} (attempt {attempt + 1}/{max_retries})...')
            video_capture = cv2.VideoCapture(camera_index)
        else:
            logger.info(f'Connecting to remote camera (attempt {attempt + 1}/{max_retries})...')
            logger.info(f'URL: {camera_url}')
            video_capture = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)
            
            # Настройки для минимальной задержки RTSP
            video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if video_capture.isOpened():
            ret, frame = video_capture.read()
            if ret:
                logger.info(f'✅ Camera connected ({camera_type})')
                logger.info(f'Frame size: {frame.shape[1]}x{frame.shape[0]}')
                
                # Для RTSP - сбрасываем начальный буфер
                if camera_type == 'stream':
                    logger.info('Flushing initial buffer...')
                    for _ in range(5):
                        video_capture.grab()
                    logger.info('Low latency mode active')
                
                return video_capture
            else:
                video_capture.release()
        
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            logger.warning(f'Retry in {wait_time} seconds...')
            time.sleep(wait_time)
    
    raise Exception(f'Cannot connect to camera after {max_retries} attempts')


# ============================================================================
# ВИДЕО СТРИМ
# ============================================================================

def generate_frames():
    """Генератор кадров для MJPEG стрима"""
    global current_frame
    while True:
        with frame_lock:
            if current_frame is None:
                time.sleep(0.1)
                continue
            frame = current_frame.copy()
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.033)


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/health')
def health():
    return {'status': 'ok', 'streaming': current_frame is not None}


def start_flask_server():
    """Запуск Flask сервера в отдельном потоке"""
    logger.info(f'Starting video stream server on port {config.video_stream_port}...')
    app.run(host='0.0.0.0', port=config.video_stream_port, threaded=True, 
            debug=False, use_reloader=False)


# ============================================================================
# MAIN
# ============================================================================

def main():
    global current_frame
    
    # Загружаем сотрудников
    known_embeddings, known_ids = load_employees()
    
    if not known_ids:
        logger.error('No employees with photos found!')
        return
    
    # Инициализируем менеджеры
    tracker = FaceTracker()
    presence_manager = PresenceManager(known_ids)
    
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()
    logger.info(f'Video stream: http://localhost:{config.video_stream_port}/video_feed')
    
    # Подключаемся к камере
    video_capture = connect_camera()
    
    frame_count = 0
    consecutive_failures = 0
    MAX_FAILURES = 10
    last_reload = time.time()
    
    logger.info('🎬 Starting main loop...')
    
    try:
        while True:
            # Для RTSP минимизируем задержку
            camera_type = 'stream' if config.camera_source.startswith('rtsp://') else 'local'
            if camera_type == 'stream' and frame_count % 2 == 0:
                video_capture.grab()
            
            ret, frame = video_capture.read()
            
            if not ret:
                consecutive_failures += 1
                logger.warning(f'Failed to read frame ({consecutive_failures}/{MAX_FAILURES})')
                
                if consecutive_failures >= MAX_FAILURES:
                    logger.error('Too many failures, reconnecting...')
                    video_capture.release()
                    time.sleep(2)
                    video_capture = connect_camera()
                    consecutive_failures = 0
                else:
                    time.sleep(0.5)
                continue
            
            consecutive_failures = 0
            
            # Горячая перезагрузка сотрудников
            if time.time() - last_reload > config.reload_employees_interval:
                logger.info('Reloading employees...')
                try:
                    new_embeddings, new_ids = load_employees()
                    if new_ids:
                        known_embeddings, known_ids = new_embeddings, new_ids
                        
                        # Добавляем новых в presence manager
                        for emp_id in new_ids:
                            presence_manager.add_employee(emp_id)
                        
                        logger.info(f'Reloaded {len(new_ids)} employees')
                    last_reload = time.time()
                except Exception as e:
                    logger.error(f'Reload failed: {e}')
                    last_reload = time.time()
            
            frame_count += 1
            
            # Обрабатываем только каждый N-й кадр
            if frame_count % config.frame_skip != 0:
                # Обновляем видео стрим
                with frame_lock:
                    current_frame = frame.copy()
                continue
            
            # Детекция и распознавание
            faces = face_app.get(frame)
            
            # Обновляем треки
            recognized_tracks = tracker.update(faces, known_embeddings, known_ids)
            
            # Получаем ID распознанных сотрудников
            recognized_emp_ids = [t.recognized_employee_id for t in recognized_tracks]
            
            # Обновляем состояния присутствия
            events = presence_manager.update(recognized_emp_ids)
            
            # Отправляем события
            for emp_id, event_type in events:
                send_event(emp_id, event_type)
            
            # Визуализация
            display_frame = frame.copy()
            
            # Статус в углу
            preprocessing_status = "CLAHE→Sharp→" if config.enable_preprocessing else ""
            status_text = (
                f"{preprocessing_status}InsightFace | "
                f"Tracks: {len(tracker.tracks)} | "
                f"Recognized: {len(recognized_emp_ids)}"
            )
            cv2.putText(display_frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
            cv2.putText(display_frame, status_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Рисуем рамки
            for track in recognized_tracks:
                if track.last_bbox is not None:
                    x1, y1, x2, y2 = track.last_bbox.astype(int)
                    
                    # Зелёная рамка для распознанных
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    
                    # Label с ID и уверенностью
                    label = f"ID: {track.recognized_employee_id} ({track.recognition_confidence:.0%})"
                    cv2.rectangle(display_frame, (x1, y2 - 30), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(display_frame, label, (x1 + 6, y2 - 8),
                               cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
            
            # Нераспознанные лица (треки без employee_id)
            for track in tracker.tracks:
                if track.recognized_employee_id is None and track.last_bbox is not None:
                    x1, y1, x2, y2 = track.last_bbox.astype(int)
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    
                    label = f"Track {track.track_id} ({len(track.embeddings)}/{config.min_good_embeddings_per_track})"
                    cv2.rectangle(display_frame, (x1, y2 - 30), (x2, y2), (0, 0, 255), cv2.FILLED)
                    cv2.putText(display_frame, label, (x1 + 6, y2 - 8),
                               cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
            
            # Сохраняем для стрима
            with frame_lock:
                current_frame = display_frame
            
            time.sleep(0.05)
    
    finally:
        video_capture.release()
        logger.info('Camera released')


if __name__ == '__main__':
    logger.info('='*60)
    logger.info('Recognition Service - AI-Powered')
    logger.info('='*60)
    logger.info(f'Backend: {config.backend_url}')
    logger.info(f'Camera: {config.camera_source}')
    logger.info(f'Preprocessing: {config.enable_preprocessing}')
    logger.info(f'Min face height: {config.min_face_height_pixels}px')
    logger.info(f'Min blur variance: {config.min_blur_variance}')
    logger.info(f'Embeddings per track: {config.min_good_embeddings_per_track}')
    logger.info('='*60)
    
    main()

