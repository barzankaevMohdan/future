# Backend API

Node.js + TypeScript + Express + Prisma + PostgreSQL backend for attendance system.

## Setup

```bash
npm install
npm run prisma:generate
npm run prisma:migrate
npm run prisma:seed
```

## Development

```bash
npm run dev
```

## Production

```bash
npm run build
npm start
```

## Environment Variables

See `env.example` for all options.

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token

### Companies (SUPERADMIN only)
- `GET /api/companies` - List all
- `POST /api/companies` - Create
- `GET /api/companies/:id` - Get by ID
- `PUT /api/companies/:id` - Update
- `DELETE /api/companies/:id` - Delete

### Users
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `GET /api/users/:id` - Get user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Employees
- `GET /api/employees` - List employees
- `POST /api/employees` - Create employee (with photo upload)
- `GET /api/employees/:id` - Get employee
- `PUT /api/employees/:id` - Update employee
- `DELETE /api/employees/:id` - Delete employee

### Cameras
- `GET /api/cameras` - List cameras
- `POST /api/cameras` - Create camera
- `GET /api/cameras/:id` - Get camera
- `GET /api/cameras/:id/stream-url` - Get stream URL
- `PUT /api/cameras/:id` - Update camera
- `DELETE /api/cameras/:id` - Delete camera

### Events
- `POST /api/events` - Create event (for recognition service)
- `GET /api/events` - Get events with filters

### Presence
- `GET /api/presence` - Get current presence status

### Statistics
- `GET /api/statistics` - Get analytics

### Health
- `GET /api/health` - Health check

## Database

### Migrations

```bash
# Create migration
npm run prisma:migrate

# Deploy migrations
npm run prisma:deploy

# Prisma Studio (GUI)
npm run prisma:studio
```

### Seed

```bash
npm run prisma:seed
```

Creates:
- SuperAdmin: `admin@system.com` / `admin123`
- Company Admin: `admin@demo.com` / `admin123`
- User: `user@demo.com` / `user123`








