from fastapi import FastAPI

from db import get_checks, get_history ,get_incidents, update_incident, get_status, init_db

app =  FastAPI(title="SentinelAPI")
init_db()

@app.get("/")
def home():
    return {"message": "SentinelAPI is running."}

@app.get("/status")
def status():
    return get_status()

@app.get("/checks")
def checks(limit: int=20):
    return get_checks(limit)

@app.get("/history")
def history(url:str, limit: int=50):
    return get_history(url, limit)

@app.get("/incidents")
def incidents():
    return get_incidents()