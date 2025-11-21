# 🎥 Подключение вашей CamHiPro камеры

**IP:** 192.168.50.235  
**Логин:** admin  
**Пароль:** admin  
**Статус:** ✅ Вы в одной сети - должно работать!

---

## 🚀 ЗАПУСК

### ⚠️ ВАЖНО: Используйте субстрим `/12` вместо `/11`

**Почему:**
- `/11` - основной стрим (1080p, **H.265/HEVC**) ← вызывает ошибки
- `/12` - субстрим (720p, **H.264**) ← стабильный!

**H.264 работает НАМНОГО лучше с OpenCV!**

---

### Команда для запуска:

```bash
cd /Users/mohdan/Desktop/future/recognition
source venv/bin/activate

# Используйте СУБСТРИМ /12 (H.264):
CAMERA_SOURCE="rtsp://admin:admin@192.168.50.235:554/12" FRAME_SKIP=5 python main.py
```

**В логах увидите:**
```
[recognition] Initializing InsightFace AI...
[recognition] ✅ InsightFace initialized (99.8% accuracy!)
[recognition] Preprocessing: ON
[recognition] Connecting to remote camera...
[recognition] URL: rtsp://admin:admin@192.168.50.235:554/12
[recognition] ✅ Camera connected successfully (stream)
[recognition] Frame size: 1280x720
[recognition] Flushing initial buffer...
[recognition] Low latency mode active
```

**Откройте:** http://localhost:5173

**Увидите видео с вашей камеры!** 📹✨

---

## 🎯 ЕСЛИ СУБСТРИМ НЕ РАБОТАЕТ

**Попробуйте другие варианты:**

```bash
# Вариант 1: /01
CAMERA_SOURCE="rtsp://admin:admin@192.168.50.235:554/01" python main.py

# Вариант 2: /02  
CAMERA_SOURCE="rtsp://admin:admin@192.168.50.235:554/02" python main.py

# Вариант 3: Основной стрим /11 (может быть HEVC ошибки)
CAMERA_SOURCE="rtsp://admin:admin@192.168.50.235:554/11" FRAME_SKIP=10 python main.py
```

---

## ⚡ ОПТИМИЗАЦИЯ ЗАДЕРЖКИ

### Для минимальной задержки:

```bash
CAMERA_SOURCE="rtsp://admin:admin@192.168.50.235:554/12" \
FRAME_SKIP=8 \
python main.py
```

**Это даст:**
- Задержка: ~1-2 секунды
- Распознавание: ~3-4 секунды
- Стабильная работа без HEVC ошибок

---

## 🏆 ПОЛНЫЙ ЗАПУСК СИСТЕМЫ

```bash
# Terminal 1: Backend
cd /Users/mohdan/Desktop/future/backend
npm start

# Terminal 2: Frontend
cd /Users/mohdan/Desktop/future/frontend  
npm run dev

# Terminal 3: Recognition с CamHiPro камерой
cd /Users/mohdan/Desktop/future/recognition
source venv/bin/activate
CAMERA_SOURCE="rtsp://admin:admin@192.168.50.235:554/12" python main.py
```

**Откройте:** http://localhost:5173

---

## 📊 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

**На видео увидите:**
```
CLAHE→Sharp→InsightFace AI | OK: X | Faces: Y
```

**Это значит:**
- ✅ Предобработка работает (CLAHE + резкость)
- ✅ InsightFace AI распознаёт (99.8%)
- ✅ Видео с офисной камеры в реальном времени
- ✅ Рамки вокруг лиц (зелёные/красные)

---

## 🐛 ЕСЛИ ПОЯВЯТСЯ ОШИБКИ

### Ошибка: `[hevc @ ...] Could not find ref`

**Значит используется /11 с HEVC кодеком**

**Решение:** Используйте `/12` или `/01`

### Ошибка: `Connection refused`

**Проверьте:**
- Backend запущен? `npm start`
- Камера доступна? `ping 192.168.50.235`
- В той же сети? Проверьте WiFi

### Большая задержка

**Увеличьте FRAME_SKIP:**
```bash
CAMERA_SOURCE="rtsp://admin:admin@192.168.50.235:554/12" FRAME_SKIP=10 python main.py
```

---

## 💡 БЫСТРЫЙ СТАРТ

**Одной командой (в терминале recognition):**

```bash
cd /Users/mohdan/Desktop/future/recognition && source venv/bin/activate && CAMERA_SOURCE="rtsp://admin:admin@192.168.50.235:554/12" python main.py
```

**ПОПРОБУЙТЕ ПРЯМО СЕЙЧАС!** 🚀📹✨

(Не забудьте запустить backend и frontend в других терминалах!)

