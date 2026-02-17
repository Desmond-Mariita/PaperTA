# PaperTA Local Dev Setup (Cross-OS)

This setup is designed for Windows, macOS, and Linux using Docker.

## 1. Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine + Compose plugin (Linux)
- Git

Windows note:
- Enable WSL2 backend in Docker Desktop for best compatibility.

## 2. First-Time Setup

1. Create local env file:

```bash
cp .env.example .env
```

2. Start infrastructure services (works now with current repo):

```bash
docker compose up -d
```

This starts:
- Postgres (`localhost:5432`)
- Redis (`localhost:6379`)
- Qdrant (`localhost:6333`)
- MinIO API (`localhost:9000`)
- MinIO Console (`localhost:9001`)

## 3. Optional Full App Startup

When `backend/` and `frontend/` are added, start app containers with:

```bash
docker compose --profile app up -d --build
```

Expected app endpoints:
- Backend API: `http://localhost:8000`
- Frontend UI: `http://localhost:3000`

## 4. Day-to-Day Commands

Start services:

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f
```

Stop services:

```bash
docker compose down
```

Stop and remove volumes (resets local data):

```bash
docker compose down -v
```

## 5. Why This Works Across OS

- Docker Compose gives the same runtime on Windows/macOS/Linux.
- Browser-based UI avoids OS-specific installers during early development.
- The same containers can later be deployed to cloud environments.
