import os
import sys

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.schemas import BikePredictionInput, BikePredictionResponse
from src.prediction.predict import PredictionPipeline
from src.logger import logging as log
from configs.paths import Paths

# Global variables for model and preprocessor
prediction_pipeline = None
model = None
preprocessor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global prediction_pipeline, model, preprocessor
    log.info("Initializing PredictionPipeline and loading model resources...")
    try:
        prediction_pipeline = PredictionPipeline()
        model, preprocessor, _ = prediction_pipeline.read_resources()
        log.info("Model and preprocessor loaded successfully for FastAPI server.")
    except Exception as e:
        log.error(f"Failed to load model resources during app startup: {e}")
        raise RuntimeError(f"Could not load ML model or preprocessor: {e}")
    yield
    log.info("Shutting down FastAPI application.")

app = FastAPI(
    title="Bike Rental Prediction API",
    description="REST API for predicting hourly bike rental demand using trained ML model.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for external frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """Serves the main application web interface."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h2>Bike Rental Prediction App Frontend is loading...</h2>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API and model status."""
    is_ready = model is not None and preprocessor is not None
    return {
        "status": "healthy" if is_ready else "unhealthy",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None
    }


@app.post("/predict", response_model=BikePredictionResponse)
async def predict_bike_rentals(input_data: BikePredictionInput):
    """
    Predicts the hourly rented bike count based on meteorological and calendar inputs.
    """
    global prediction_pipeline, model, preprocessor

    if model is None or preprocessor is None:
        raise HTTPException(
            status_code=503,
            detail="Machine learning model or preprocessor is not loaded."
        )

    try:
        # Convert input payload into DataFrame matching raw dataset feature column names
        raw_data = {
            "Date": input_data.Date,
            "Hour": input_data.Hour,
            "Temperature": input_data.Temperature,
            "Humidity": input_data.Humidity,
            "Wind speed": input_data.Wind_speed,
            "Visibility": input_data.Visibility,
            "Dew point temperature": input_data.Dew_point_temperature,
            "Solar Radiation": input_data.Solar_Radiation,
            "Rainfall": input_data.Rainfall,
            "Snowfall": input_data.Snowfall,
            "Seasons": input_data.Seasons,
            "Holiday": input_data.Holiday,
            "Functioning Day": input_data.Functioning_Day
        }

        input_df = pd.DataFrame([raw_data])

        # Preprocess input using PredictionPipeline logic
        processed_df, _ = prediction_pipeline.apply_preprocessing(
            preprocessor=preprocessor,
            sample_data=input_df
        )

        # Generate prediction
        raw_pred = float(model.predict(processed_df)[0])
        
        # Ensure count is non-negative integer
        predicted_count = max(0, int(round(raw_pred)))

        # Determine demand level category
        if input_data.Functioning_Day == "No":
            demand_level = "No Operation (Facility Closed)"
        elif predicted_count == 0:
            demand_level = "Zero Demand"
        elif predicted_count < 300:
            demand_level = "Low Demand"
        elif predicted_count < 800:
            demand_level = "Moderate Demand"
        elif predicted_count < 1400:
            demand_level = "High Demand"
        else:
            demand_level = "Peak Demand"

        log.info(f"Successfully processed prediction request: {predicted_count} bikes ({demand_level})")

        return BikePredictionResponse(
            status="success",
            predicted_rented_bike_count=predicted_count,
            raw_prediction=round(raw_pred, 2),
            demand_level=demand_level,
            inputs=raw_data
        )

    except Exception as e:
        log.error(f"Prediction failed with error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during prediction: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)