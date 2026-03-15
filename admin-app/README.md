# Company Admin (Create React App)

Admin panel for the notification backend. Built with **Create React App** (React 18 + TypeScript).

## Run locally (no Docker)

1. Install dependencies:
   ```bash
   cd admin-app
   npm install
   ```

2. Ensure the API is running on **http://localhost:8000**.

3. Create `.env` (or copy from `.env.example`) so the frontend calls the API on port 8000:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

4. Start the admin app:
   ```bash
   npm start
   ```
   Opens at **http://localhost:3000**. API requests go to **http://localhost:8000/api** (see `REACT_APP_API_URL` in `.env`).

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
