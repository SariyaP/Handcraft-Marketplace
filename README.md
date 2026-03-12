# Handcraft Marketplace

Full-stack starter project with:

- `frontend/`: Next.js App Router + JavaScript
- `backend/`: FastAPI + MySQL configuration

This repo only includes project structure and starter setup. No app features are built yet.

## Structure

```text
frontend/
  app/
  components/
  lib/
  types/

backend/
  app/
    main.py
    database.py
    models/
    schemas/
    routers/
    services/
    utils/
```

## Frontend Setup

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open 

`http://localhost:3000`

## Backend Setup

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then run:

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

`http://127.0.0.1:8000/`

`http://127.0.0.1:8000/docs`

## Environment Files

- Frontend example: [frontend/.env.example](/c:/Users/User/OneDrive/Desktop/Proj-Arch/Handcraft-Marketplace/frontend/.env.example)
- Backend example: [backend/.env.example](/c:/Users/User/OneDrive/Desktop/Proj-Arch/Handcraft-Marketplace/backend/.env.example)

## Notes

- Frontend connects to the backend using `NEXT_PUBLIC_API_BASE_URL`
- Backend reads MySQL settings from `.env`
- MySQL connection is configured, but no models or tables are created yet
