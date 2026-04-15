# Handcraft Marketplace

Full-stack handmade marketplace app built with:

- `frontend/`: Next.js App Router + JavaScript
- `backend/`: FastAPI + SQLAlchemy + MySQL

The app supports:

- login and register
- customer, maker, and admin roles
- product browsing and product management
- commissions, wishlist, and reviews
- admin moderation

## Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8+

## Backend Environment

```env
APP_NAME=Handcraft Marketplace API
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=43200
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=handcraft_marketplace
MYSQL_ECHO=false
```

Frontend:

```env
NEXT_PUBLIC_APP_NAME=Handcraft Marketplace
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Run the App

### 1. Create the MySQL database

Open MySQL and create the database:

```sql
CREATE DATABASE handcraft_marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Run the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

### 3. Run the frontend

```powershell
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open:

- `http://localhost:3000`

## Seed Demo Data

### Main sample data

```powershell
cd backend
.\.venv\Scripts\python seed_products.py
```

This creates:

- sample makers and maker profiles
- sample products with customization options
- sample customer orders and commissions

Sample customer login:

- customer: `mina.customer@example.com`
- password: `password123`

### Existing user data

```powershell
cd backend
.\.venv\Scripts\python seed_existing_users.py
```

This adds sample products, orders, commissions, and wishlist items for existing maker and customer accounts already stored in the database.

## Tests

Backend tests:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests -q
```

Frontend checks:

```powershell
cd frontend
npm run lint
npm run build
```

## Notes

- The backend expects MySQL, not SQLite.
- Admin users should be created manually.
