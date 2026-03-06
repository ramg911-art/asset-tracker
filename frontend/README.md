# Asset Tracker – Frontend

React + TypeScript + Vite frontend for the Enterprise Asset Management API.

## Stack

- **React 18** + **TypeScript**
- **Vite**
- **React Router 6**
- **Tailwind CSS**

## Setup

```bash
cd frontend
npm install
```

## Run

Start the backend first (e.g. `uvicorn app.main:app --reload` on port 8000), then:

```bash
npm run dev
```

App: http://localhost:3000  
API requests are proxied from `/api` to `http://127.0.0.1:8000` (see `vite.config.ts`).  
To use a different backend URL, set `VITE_API_URL` in `.env` (e.g. `VITE_API_URL=http://127.0.0.1:8000`).

## Build

```bash
npm run build
npm run preview   # preview production build
```

## Features

- **Auth**: Login, Register, JWT in `localStorage`, protected routes
- **Dashboard**: Summary counts from `/reports/summary`
- **Lists**: Assets, Locations, Categories, Departments (paginated)

All other backend routes (vendors, repairs, movements, maintenance, verification, documents, labels, reports) can be added as new pages and API modules following the same pattern.
