import os
import sys

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app.schemas import BikePredictionInput, BikePredictionResponse
from app.database import engine, get_db, Base
from app.models import PredictionRecord
from src.prediction.predict import PredictionPipeline
from src.logger import logging as log
from configs.paths import Paths

# Global variables for model and preprocessor
#prediction_pipeline = None
#model = None
#preprocessor = None

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

    # Attempt to initialize MySQL database tables if connected
    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
            log.info("Successfully connected to MySQL database and initialized tables.")
        except Exception as e:
            log.warning(f"Database table initialization skipped (DB may not be reachable yet): {e}")

    yield
    log.info("Shutting down FastAPI application.")

app = FastAPI(
    title="Bike Rental Prediction API with AWS RDS MySQL Integration",
    description="REST API for predicting hourly bike rental demand with database record persistence.",
    version="1.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Health check endpoint to verify API, model, and database connection status."""
    db_connected = False
    if engine is not None:
        try:
            with engine.connect() as conn:
                db_connected = True
        except Exception:
            db_connected = False

    return {
        "status": "healthy" if (model is not None and preprocessor is not None) else "unhealthy",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
        "database_connected": db_connected
    }


@app.post("/predict", response_model=BikePredictionResponse)
async def predict_bike_rentals(input_data: BikePredictionInput, db: Session = Depends(get_db)):
    """
    Predicts hourly bike rentals and persists the prediction record to MySQL database.
    """
    global prediction_pipeline, model, preprocessor

    if model is None or preprocessor is None:
        raise HTTPException(
            status_code=503,
            detail="Machine learning model or preprocessor is not loaded."
        )

    try:
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

        processed_df, _ = prediction_pipeline.apply_preprocessing(
            preprocessor=preprocessor,
            sample_data=input_df
        )

        raw_pred = float(model.predict(processed_df)[0])
        predicted_count = max(0, int(round(raw_pred)))

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

        # Save to MySQL Database if session is available
        if db is not None:
            try:
                record = PredictionRecord(
                    date_val=input_data.Date,
                    hour=input_data.Hour,
                    temperature=input_data.Temperature,
                    humidity=input_data.Humidity,
                    wind_speed=input_data.Wind_speed,
                    visibility=input_data.Visibility,
                    dew_point_temp=input_data.Dew_point_temperature,
                    solar_radiation=input_data.Solar_Radiation,
                    rainfall=input_data.Rainfall,
                    snowfall=input_data.Snowfall,
                    seasons=input_data.Seasons,
                    holiday=input_data.Holiday,
                    functioning_day=input_data.Functioning_Day,
                    predicted_count=predicted_count,
                    raw_prediction=round(raw_pred, 2),
                    demand_level=demand_level
                )
                db.add(record)
                db.commit()
                db.refresh(record)
                log.info(f"Prediction saved to MySQL database with Record ID #{record.id}")
            except Exception as db_err:
                log.warning(f"Could not save prediction to database: {db_err}")
                db.rollback()

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


@app.get("/api/history")
async def get_prediction_history(limit: int = 10, db: Session = Depends(get_db)):
    """Retrieves recent prediction history from MySQL database."""
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection is not available.")
    
    records = db.query(PredictionRecord).order_by(PredictionRecord.id.desc()).limit(limit).all()
    return {
        "count": len(records),
        "history": [record.to_dict() for record in records]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=True)