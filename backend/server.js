const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const sqlite3 = require('sqlite3').verbose();
const rateLimit = require('express-rate-limit');
const http = require('http');
const { Server } = require('socket.io');
const sharp = require('sharp');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Rate limiting
const apiLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 минута
  max: 100, // максимум 100 запросов в минуту
  message: { error: 'Too many requests, please try again later' },
  standardHeaders: true,
  legacyHeaders: false
});

const eventLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 минута
  max: 200, // максимум 200 событий в минуту (для recognition service)
  message: { error: 'Too many events' },
  standardHeaders: true,
  legacyHeaders: false
});

// Применяем общий лимит ко всем API эндпоинтам
app.use('/api/', apiLimiter);

// Static for uploads
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}
app.use('/uploads', express.static(uploadsDir));

// Multer setup with validation
const storage = multer.memoryStorage(); // Используем память для обработки sharp
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB максимум
    files: 1
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Неподдерживаемый формат. Используйте JPEG, PNG или WebP'));
    }
  }
});

// Обработчик ошибок multer
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'Файл слишком большой (максимум 10MB)' });
    }
    return res.status(400).json({ error: err.message });
  }
  if (err) {
    return res.status(400).json({ error: err.message });
  }
  next();
});

// DB setup (SQLite)
const dbPath = path.join(__dirname, 'db.sqlite');
const db = new sqlite3.Database(dbPath);

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT,
    photoFilename TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employeeId INTEGER NOT NULL,
    type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(employeeId) REFERENCES employees(id)
  )`);

  // Индексы для оптимизации запросов
  db.run(`CREATE INDEX IF NOT EXISTS idx_events_employeeId ON events(employeeId)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_events_employeeId_timestamp ON events(employeeId, timestamp DESC)`);
});

// Helper: async wrappers
function allAsync(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

function getAsync(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

function runAsync(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) reject(err);
      else resolve(this);
    });
  });
}

// Routes

// Metrics tracking
const metrics = {
  startTime: Date.now(),
  requestCount: 0,
  eventCount: 0,
  employeeCount: 0,
  lastEventTime: null
};

// Middleware to track requests
app.use((req, res, next) => {
  if (req.path.startsWith('/api/')) {
    metrics.requestCount++;
  }
  next();
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Statistics endpoint
app.get('/api/statistics', async (req, res) => {
  try {
    const dateFrom = req.query.dateFrom || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const dateTo = req.query.dateTo || new Date().toISOString().split('T')[0];
    
    // События по дням
    const eventsByDay = await allAsync(
      `SELECT DATE(timestamp) as date, 
              COUNT(*) as count,
              SUM(CASE WHEN type = 'IN' THEN 1 ELSE 0 END) as ins,
              SUM(CASE WHEN type = 'OUT' THEN 1 ELSE 0 END) as outs
       FROM events
       WHERE DATE(timestamp) BETWEEN DATE(?) AND DATE(?)
       GROUP BY DATE(timestamp)
       ORDER BY date DESC`,
      [dateFrom, dateTo]
    );
    
    // Топ сотрудников по событиям
    const topEmployees = await allAsync(
      `SELECT employees.id, employees.name, COUNT(*) as eventCount
       FROM events
       JOIN employees ON events.employeeId = employees.id
       WHERE DATE(events.timestamp) BETWEEN DATE(?) AND DATE(?)
       GROUP BY employees.id, employees.name
       ORDER BY eventCount DESC
       LIMIT 10`,
      [dateFrom, dateTo]
    );
    
    // Среднее время на работе (примерная оценка)
    const workHours = await allAsync(
      `SELECT employees.id, employees.name,
              COUNT(CASE WHEN events.type = 'IN' THEN 1 END) as totalDays,
              AVG(
                CASE 
                  WHEN events.type = 'OUT' THEN
                    (julianday(events.timestamp) - julianday(
                      (SELECT timestamp FROM events e2 
                       WHERE e2.employeeId = employees.id 
                       AND e2.type = 'IN' 
                       AND e2.timestamp < events.timestamp 
                       ORDER BY e2.timestamp DESC LIMIT 1)
                    )) * 24
                  ELSE NULL
                END
              ) as avgHoursPerDay
       FROM employees
       LEFT JOIN events ON employees.id = events.employeeId
       WHERE DATE(events.timestamp) BETWEEN DATE(?) AND DATE(?)
       GROUP BY employees.id, employees.name
       HAVING avgHoursPerDay IS NOT NULL
       ORDER BY avgHoursPerDay DESC`,
      [dateFrom, dateTo]
    );
    
    // Общая статистика
    const totalEvents = await getAsync(
      `SELECT COUNT(*) as count FROM events 
       WHERE DATE(timestamp) BETWEEN DATE(?) AND DATE(?)`,
      [dateFrom, dateTo]
    );
    
    const uniqueEmployees = await getAsync(
      `SELECT COUNT(DISTINCT employeeId) as count FROM events
       WHERE DATE(timestamp) BETWEEN DATE(?) AND DATE(?)`,
      [dateFrom, dateTo]
    );
    
    res.json({
      period: { from: dateFrom, to: dateTo },
      summary: {
        totalEvents: totalEvents.count,
        uniqueEmployees: uniqueEmployees.count,
        avgEventsPerDay: eventsByDay.length > 0 
          ? (totalEvents.count / eventsByDay.length).toFixed(1)
          : 0
      },
      eventsByDay,
      topEmployees,
      workHours: workHours.map(w => ({
        ...w,
        avgHoursPerDay: w.avgHoursPerDay ? parseFloat(w.avgHoursPerDay.toFixed(1)) : 0
      }))
    });
  } catch (err) {
    console.error('[backend] Error getting statistics:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Metrics endpoint
app.get('/api/metrics', async (req, res) => {
  try {
    const employeesCount = await getAsync('SELECT COUNT(*) as count FROM employees');
    const eventsCount = await getAsync('SELECT COUNT(*) as count FROM events');
    const eventsToday = await getAsync(
      `SELECT COUNT(*) as count FROM events WHERE DATE(timestamp) = DATE('now')`
    );
    const presentCount = await getAsync(
      `SELECT COUNT(DISTINCT e.employeeId) as count
       FROM events e
       WHERE e.timestamp = (
         SELECT MAX(ev.timestamp)
         FROM events ev
         WHERE ev.employeeId = e.employeeId
       ) AND e.type = 'IN'`
    );
    
    const uptime = Math.floor((Date.now() - metrics.startTime) / 1000);
    
    res.json({
      status: 'ok',
      uptime: uptime,
      uptimeFormatted: formatUptime(uptime),
      employees: {
        total: employeesCount.count,
        present: presentCount.count,
        absent: employeesCount.count - presentCount.count
      },
      events: {
        total: eventsCount.count,
        today: eventsToday.count
      },
      requests: {
        total: metrics.requestCount
      },
      websocket: {
        connections: io.engine.clientsCount
      }
    });
  } catch (err) {
    console.error('[backend] Error getting metrics:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

function formatUptime(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  parts.push(`${secs}s`);
  
  return parts.join(' ');
}

// Create employee (with photo)
app.post('/api/employees', upload.single('photo'), async (req, res) => {
  try {
    const { name, role } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Name is required' });
    }
    
    let photoFilename = null;
    
    // Обработка и оптимизация фото
    if (req.file) {
      const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
      photoFilename = `photo-${uniqueSuffix}.jpg`;
      const photoPath = path.join(uploadsDir, photoFilename);
      
      // Оптимизация изображения с помощью sharp
      await sharp(req.file.buffer)
        .resize(800, 800, {
          fit: 'inside',
          withoutEnlargement: true
        })
        .jpeg({ quality: 85 })
        .toFile(photoPath);
      
      console.log(`[backend] Photo optimized and saved: ${photoFilename}`);
    }

    const insertResult = await runAsync(
      'INSERT INTO employees (name, role, photoFilename) VALUES (?, ?, ?)',
      [name, role || null, photoFilename]
    );

    const id = insertResult.lastID;
    const employee = await getAsync('SELECT * FROM employees WHERE id = ?', [id]);

    const employeeData = {
      ...employee,
      photoUrl: employee.photoFilename ? `/uploads/${employee.photoFilename}` : null
    };
    
    // Broadcast new employee via WebSocket
    broadcastUpdate('employee:added', employeeData);
    
    res.json(employeeData);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all employees
app.get('/api/employees', async (req, res) => {
  try {
    const rows = await allAsync('SELECT * FROM employees', []);
    const result = rows.map(e => ({
      ...e,
      photoUrl: e.photoFilename ? `/uploads/${e.photoFilename}` : null
    }));
    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get events for a specific employee
app.get('/api/employees/:id/events', async (req, res) => {
  try {
    const { id } = req.params;
    const rows = await allAsync(
      'SELECT * FROM events WHERE employeeId = ? ORDER BY timestamp DESC',
      [id]
    );
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all events (joined with employees) with pagination and filters
app.get('/api/events', async (req, res) => {
  try {
    const page = parseInt(req.query.page || '1', 10);
    const limit = Math.min(parseInt(req.query.limit || '50', 10), 200);
    const offset = (page - 1) * limit;
    
    // Фильтры
    const employeeId = req.query.employeeId;
    const type = req.query.type; // IN или OUT
    const dateFrom = req.query.dateFrom;
    const dateTo = req.query.dateTo;
    const search = req.query.search; // поиск по имени
    
    let whereConditions = [];
    let params = [];
    
    if (employeeId) {
      whereConditions.push('events.employeeId = ?');
      params.push(employeeId);
    }
    
    if (type && ['IN', 'OUT'].includes(type)) {
      whereConditions.push('events.type = ?');
      params.push(type);
    }
    
    if (dateFrom) {
      whereConditions.push('DATE(events.timestamp) >= DATE(?)');
      params.push(dateFrom);
    }
    
    if (dateTo) {
      whereConditions.push('DATE(events.timestamp) <= DATE(?)');
      params.push(dateTo);
    }
    
    if (search) {
      whereConditions.push('employees.name LIKE ?');
      params.push(`%${search}%`);
    }
    
    const whereClause = whereConditions.length > 0 
      ? 'WHERE ' + whereConditions.join(' AND ')
      : '';
    
    // Получаем общее количество для пагинации
    const countResult = await getAsync(
      `SELECT COUNT(*) as count
       FROM events
       JOIN employees ON events.employeeId = employees.id
       ${whereClause}`,
      params
    );
    
    const total = countResult.count;
    const totalPages = Math.ceil(total / limit);
    
    // Получаем события с пагинацией
    const rows = await allAsync(
      `SELECT events.id, events.employeeId, events.type, events.timestamp,
              employees.name, employees.role
       FROM events
       JOIN employees ON events.employeeId = employees.id
       ${whereClause}
       ORDER BY events.timestamp DESC
       LIMIT ? OFFSET ?`,
      [...params, limit, offset]
    );
    
    res.json({
      events: rows,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1
      }
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Presence summary for all employees
app.get('/api/presence', async (req, res) => {
  try {
    // Оптимизированный запрос с LEFT JOIN и подзапросом для последнего события
    const result = await allAsync(`
      SELECT 
        e.id,
        e.name,
        e.role,
        e.photoFilename,
        le.type as lastEventType,
        le.timestamp as lastEventTime,
        CASE WHEN le.type = 'IN' THEN 1 ELSE 0 END as present
      FROM employees e
      LEFT JOIN (
        SELECT ev1.employeeId, ev1.type, ev1.timestamp
        FROM events ev1
        WHERE ev1.timestamp = (
          SELECT MAX(ev2.timestamp)
          FROM events ev2
          WHERE ev2.employeeId = ev1.employeeId
        )
      ) le ON e.id = le.employeeId
    `);

    const formatted = result.map(row => ({
      id: row.id,
      name: row.name,
      role: row.role,
      photoUrl: row.photoFilename ? `/uploads/${row.photoFilename}` : null,
      lastEventType: row.lastEventType || null,
      lastEventTime: row.lastEventTime || null,
      present: Boolean(row.present)
    }));

    res.json(formatted);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Export events to CSV or JSON
app.get('/api/export/events', async (req, res) => {
  try {
    const format = req.query.format || 'json'; // json or csv
    const dateFrom = req.query.dateFrom;
    const dateTo = req.query.dateTo;
    const employeeId = req.query.employeeId;
    
    let whereConditions = [];
    let params = [];
    
    if (dateFrom) {
      whereConditions.push('DATE(events.timestamp) >= DATE(?)');
      params.push(dateFrom);
    }
    
    if (dateTo) {
      whereConditions.push('DATE(events.timestamp) <= DATE(?)');
      params.push(dateTo);
    }
    
    if (employeeId) {
      whereConditions.push('events.employeeId = ?');
      params.push(employeeId);
    }
    
    const whereClause = whereConditions.length > 0 
      ? 'WHERE ' + whereConditions.join(' AND ')
      : '';
    
    const events = await allAsync(
      `SELECT events.id, events.employeeId, employees.name, employees.role,
              events.type, events.timestamp
       FROM events
       JOIN employees ON events.employeeId = employees.id
       ${whereClause}
       ORDER BY events.timestamp DESC`,
      params
    );
    
    if (format === 'csv') {
      // Генерация CSV
      const csv = [
        'ID,Employee ID,Name,Role,Type,Timestamp',
        ...events.map(e => 
          `${e.id},${e.employeeId},"${e.name}","${e.role || ''}",${e.type},${e.timestamp}`
        )
      ].join('\n');
      
      res.setHeader('Content-Type', 'text/csv; charset=utf-8');
      res.setHeader('Content-Disposition', `attachment; filename=events-export-${Date.now()}.csv`);
      res.send('\ufeff' + csv); // BOM для правильной кодировки в Excel
    } else {
      // JSON формат
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Content-Disposition', `attachment; filename=events-export-${Date.now()}.json`);
      res.json({
        exportDate: new Date().toISOString(),
        filters: { dateFrom, dateTo, employeeId },
        totalRecords: events.length,
        events
      });
    }
  } catch (err) {
    console.error('[backend] Error exporting events:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete employee
app.delete('/api/employees/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Проверяем существование
    const emp = await getAsync('SELECT * FROM employees WHERE id = ?', [id]);
    if (!emp) {
      return res.status(404).json({ error: 'Employee not found' });
    }
    
    // Удаляем фото с диска
    if (emp.photoFilename) {
      const photoPath = path.join(uploadsDir, emp.photoFilename);
      try {
        if (fs.existsSync(photoPath)) {
          fs.unlinkSync(photoPath);
          console.log(`[backend] Deleted photo: ${emp.photoFilename}`);
        }
      } catch (err) {
        console.error('[backend] Failed to delete photo:', err);
      }
    }
    
    // Удаляем события сотрудника
    await runAsync('DELETE FROM events WHERE employeeId = ?', [id]);
    
    // Удаляем сотрудника
    await runAsync('DELETE FROM employees WHERE id = ?', [id]);
    
    console.log(`[backend] Employee ${id} deleted`);
    
    // Broadcast deletion via WebSocket
    broadcastUpdate('employee:deleted', { id, name: emp.name });
    
    res.json({ ok: true });
  } catch (err) {
    console.error('[backend] Error deleting employee:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create event (called by recognition service)
app.post('/api/events', eventLimiter, async (req, res) => {
  try {
    const { employeeId, type, timestamp } = req.body;
    if (!employeeId || !type) {
      return res.status(400).json({ error: 'employeeId and type are required' });
    }
    if (!['IN', 'OUT'].includes(type)) {
      return res.status(400).json({ error: 'Invalid type' });
    }
    const ts = timestamp || new Date().toISOString();

    const emp = await getAsync('SELECT * FROM employees WHERE id = ?', [employeeId]);
    if (!emp) {
      return res.status(404).json({ error: 'Employee not found' });
    }

    // Защита от дубликатов событий
    const lastEvent = await getAsync(
      'SELECT type, timestamp FROM events WHERE employeeId = ? ORDER BY timestamp DESC LIMIT 1',
      [employeeId]
    );
    
    if (lastEvent && lastEvent.type === type) {
      const timeDiff = Date.now() - new Date(lastEvent.timestamp).getTime();
      if (timeDiff < 60000) { // меньше минуты
        console.log(`[backend] Skipping duplicate ${type} event for employee ${employeeId}`);
        return res.json({ ok: true, skipped: true, reason: 'duplicate' });
      }
    }

    await runAsync(
      'INSERT INTO events (employeeId, type, timestamp) VALUES (?, ?, ?)',
      [employeeId, type, ts]
    );

    console.log(`[backend] Event ${type} created for employee ${employeeId}`);
    
    // Broadcast event via WebSocket
    broadcastUpdate('event:created', {
      employeeId,
      type,
      timestamp: ts,
      employeeName: emp.name
    });
    
    res.json({ ok: true });
  } catch (err) {
    console.error('[backend] Error creating event:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log('[backend] Client connected:', socket.id);
  
  socket.on('disconnect', () => {
    console.log('[backend] Client disconnected:', socket.id);
  });
});

// Helper to broadcast updates
function broadcastUpdate(eventType, data) {
  io.emit(eventType, data);
  console.log(`[backend] Broadcasted ${eventType} to all clients`);
}

server.listen(PORT, () => {
  console.log(`Backend listening on http://localhost:${PORT}`);
  console.log('WebSocket server is ready');
});
