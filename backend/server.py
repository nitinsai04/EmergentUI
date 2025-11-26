from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from simulation import DigitalTwinSimulation
from models import SimulationParams, SimulationResult
import os
import numpy as np
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "*" # Allow all for prototype
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/")
def read_root():
    return {"message": "Digital Twin Simulation API Ready"}

@app.post("/api/simulate", response_model=SimulationResult)
def run_simulation(params: SimulationParams):
    try:
        sim = DigitalTwinSimulation(params.dict())
        results = sim.run()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-dataset")
def generate_dataset(count: int = 100):
    # Generate 'count' random simulations
    # This is a placeholder for the bulk generation feature
    # In a real app, this would stream a CSV or return a large JSON
    datasets = []
    for i in range(min(count, 10)): # Limit to 10 for quick prototype response
        params = {
            "Kt": 0.1 + np.random.normal(0, 0.01),
            "voltage": 12.0 + np.random.normal(0, 1.0),
            "duration": 5.0,
            "dt": 0.1
        }
        sim = DigitalTwinSimulation(params)
        res = sim.run()
        datasets.append(res)
    
    return {"message": f"Generated {count} samples (returned {len(datasets)} previews)", "preview": datasets}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
