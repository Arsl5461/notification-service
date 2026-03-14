# Company Admin (Create React App)

Admin panel for the notification backend. Built with **Create React App** (React 18 + TypeScript).

## Run locally (no Docker)

1. Install dependencies:
   ```bash
   cd admin-app
   npm install
   ```

2. Start the API backend (from project root):
   ```bash
   # Ensure API is running on http://localhost:8000
   ```

3. Start the admin app:
   ```bash
   npm start
   ```
   Opens at **http://localhost:3000**. API requests are proxied to `http://localhost:8000` (see `package.json` "proxy" and `src/setupProxy.js`).

## Run with Docker

From project root:

```bash
docker compose up -d admin
```

Admin runs at **http://localhost:3000**. The container uses `REACT_APP_PROXY_TARGET=http://api:8000` so `/api` is proxied to the API service.

## Login

- Email: `admin@example.com`
- Password: `admin123`

(After running the backend seed: `docker compose exec api python scripts/seed_admin.py`)
