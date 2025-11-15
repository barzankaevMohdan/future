const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Static for uploads
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}
app.use('/uploads', express.static(uploadsDir));

// Multer setup
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadsDir);
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    const ext = path.extname(file.originalname);
    cb(null, file.fieldname + '-' + uniqueSuffix + ext);
  }
});
const upload = multer({ storage });

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

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Create employee (with photo)
app.post('/api/employees', upload.single('photo'), async (req, res) => {
  try {
    const { name, role } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Name is required' });
    }
    const photoFilename = req.file ? req.file.filename : null;

    const result = await runAsync(
      'INSERT INTO employees (name, role, photoFilename) VALUES (?, ?, ?)',
      [name, role || null, photoFilename]
    );

    const id = result.lastID;
    const employee = await getAsync('SELECT * FROM employees WHERE id = ?', [id]);

    res.json({
      ...employee,
      photoUrl: employee.photoFilename ? `/uploads/${employee.photoFilename}` : null
    });
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

// Get all events (joined with employees)
app.get('/api/events', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit || '100', 10);
    const rows = await allAsync(
      `SELECT events.id, events.employeeId, events.type, events.timestamp,
              employees.name, employees.role
       FROM events
       JOIN employees ON events.employeeId = employees.id
       ORDER BY events.timestamp DESC
       LIMIT ?`,
      [limit]
    );
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Presence summary for all employees
app.get('/api/presence', async (req, res) => {
  try {
    const employees = await allAsync('SELECT * FROM employees', []);

    const result = [];
    for (const emp of employees) {
      const lastEvent = await getAsync(
        'SELECT * FROM events WHERE employeeId = ? ORDER BY timestamp DESC LIMIT 1',
        [emp.id]
      );
      const present = lastEvent ? lastEvent.type === 'IN' : false;

      result.push({
        id: emp.id,
        name: emp.name,
        role: emp.role,
        photoUrl: emp.photoFilename ? `/uploads/${emp.photoFilename}` : null,
        lastEventType: lastEvent ? lastEvent.type : null,
        lastEventTime: lastEvent ? lastEvent.timestamp : null,
        present
      });
    }

    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create event (called by recognition service)
app.post('/api/events', async (req, res) => {
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

    await runAsync(
      'INSERT INTO events (employeeId, type, timestamp) VALUES (?, ?, ?)',
      [employeeId, type, ts]
    );

    res.json({ ok: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`Backend listening on http://localhost:${PORT}`);
});
