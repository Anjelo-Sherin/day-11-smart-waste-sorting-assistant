# Setup & Installation Guide

This guide walks you through setting up and running **EcoSort AI** on macOS, Linux, or Windows (WSL2), either via a local Python virtual environment or Docker Compose.

---

## 1. Prerequisites

- **Python:** Version 3.9 or newer
- **Pip:** Latest package manager
- **Git:** Version 2.20+
- **Docker & Docker Compose** (Optional, for containerized deployments)

---

## 2. Option A: Local Python Setup (Recommended for Development)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Anjelo-Sherin/day-11-smart-waste-sorting-assistant.git
cd day-11-smart-waste-sorting-assistant
```

### Step 2: Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
```
*(The defaults in `.env` are ready out-of-the-box and require no paid external keys)*

### Step 5: Run Automated Tests
```bash
python -m pytest tests/ -v
```

### Step 6: Launch the Application
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8011 --reload
```

Open your browser to: **`http://localhost:8011`**

---

## 3. Option B: Docker Setup (Zero Configuration)

Build and run the entire application stack in an isolated container:

```bash
docker compose up --build
```

To run in the background (detached mode):
```bash
docker compose up -d
```

To stop:
```bash
docker compose down
```

---

## 4. Troubleshooting Common Issues

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| **Port 8011 in use** | Another process is bound to 8011 | Set `PORT=8012` in `.env` or run `uvicorn src.main:app --port 8012` |
| **Camera permission error** | Browser blocked webcam access | Click the lock/camera icon in your browser URL bar and allow permissions, or use the **Benchmark Test Gallery** |
| **Leaflet Map blank** | Offline / restricted internet | OpenStreetMap tiles require internet access; local fallback facilities still calculate distances and routes offline |
