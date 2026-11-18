# SentinelAPI

A monitoring tool that checks whether APIs are working, measures how fast
they respond, and raises an incident when one keeps failing.

## Features
- Register multiple API endpoints
- Automatic checks every 30 seconds (status code and response time)
- Timeouts, connection errors and error codes detected
- Incident opens after 3 consecutive failures, closes on recovery
- Uptime and response-time history
- JSON API for other apps (`/status`, `/history`, `/incidents`, `/health-report`)
- Streamlit dashboard

## Tech stack
Python, httpx, SQLite, APScheduler, FastAPI, Streamlit, pandas

## Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run (two terminals)
```bash
uvicorn api:app --reload
streamlit run dashboard.py
```
API docs: http://127.0.0.1:8000/docs  |  Dashboard: http://localhost:8501

## Screenshots
Add your dashboard screenshots here.

## Author
Harmi Pansuriya, B.Tech CSE, Amity University Rajasthan