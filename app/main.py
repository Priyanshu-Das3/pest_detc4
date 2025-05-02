from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .pest_detection import PestDetectionSystem
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

app = FastAPI(title="Pest Detection API")
system = PestDetectionSystem()

def detection_job():
    system.process_new_entries()

@app.on_event("startup")
def startup_event():
    scheduler = BackgroundScheduler()
    scheduler.add_job(detection_job, 'interval', minutes=5)
    scheduler.start()

@app.post("/detect")
async def detect_pest(data: dict):
    try:
        required_sensors = os.getenv("SENSORS").split(',')
        for sensor in required_sensors:
            if sensor not in data:
                raise ValueError(f"Missing {sensor} data")
        row_data = [datetime.now().isoformat()] + [str(data[sensor]) for sensor in required_sensors]
        system.append_to_sheet(row_data)
        system.process_new_entries()
        return JSONResponse({
            "status": "success",
            "sensors_used": required_sensors,
            "row_number": len(system.sheet.get_all_values())
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "active", "sensors": os.getenv("SENSORS").split(',')}
