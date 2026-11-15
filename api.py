from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from checker import check_url
from db import (add_endpoint, delete_endpoint, get_checks, get_endpoints, get_history, get_incidents, get_status, init_db, save_check, update_incident)

class EndpointIn(BaseModel):
    name : str
    url : str
    timeout_s: float=5
    slow_ms : int =  4000

def run_checks():
    for ep in get_endpoints():
        result =  check_url(ep["url"], ep["timeout_s"], ep["slow_ms"])
        save_check(result)
        update_incident(ep["url"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler=BackgroundScheduler()
    scheduler.add_job(run_checks, "interval", seconds=60, max_instances=1)
    scheduler.start()
    yield
    scheduler.shutdown()

app=FastAPI(title="SentinelAPI", lifespan=lifespan)

@app.get("/")
def home():
    return{"message":"SentinelAPI is running"}

@app.post("/endpoints", status_code=201)
def register_endpoint(body: EndpointIn):
    if not add_endpoint(body.name, body.url, body.timeout_s, body.slow_ms):
        raise HTTPException(staus_code=409, detail="URL already registered")
    return {"message":"Endpoint added", "url": body.url}

@app.get("/endpoints")
def list_endpoints():
    return get_endpoints()

@app.delete("/endpoints/{endpoint_id}")
def remove_endpoint(endpoint_id: int):
    if not delete_endpoint(endpoint_id):
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return {"deleted": endpoint_id}

@app.post("/check-now")
def check_now():
    run_checks()
    return {"message": "Checks completed"}

@app.get("/status")
def status():
    return get_status()


@app.get("/checks")
def checks(limit: int = 20):
    return get_checks(limit)


@app.get("/history")
def history(url: str, limit: int = 50):
    return get_history(url, limit)


@app.get("/incidents")
def incidents():
    return get_incidents()
           