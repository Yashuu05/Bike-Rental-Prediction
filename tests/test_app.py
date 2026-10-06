import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import BikePredictionInput

client = TestClient(app)


def test_home_page():
    """Verify that the home page endpoint serves HTML properly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Bike Rental" in response.text or "text/html" in response.headers.get("content-type", "")


def test_health_endpoint():
    """Verify health endpoint structure and availability."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "database_connected" in data


def test_prediction_input_schema_valid():
    """Verify Pydantic input schema with valid data."""
    sample_payload = {
        "Date": "2025-07-15",
        "Hour": 18,
        "Temperature": 28.5,
        "Humidity": 45.0,
        "Wind speed": 2.5,
        "Visibility": 1950.0,
        "Dew point temperature": 16.0,
        "Solar Radiation": 2.45,
        "Rainfall": 0.0,
        "Snowfall": 0.0,
        "Seasons": "Summer",
        "Holiday": "No Holiday",
        "Functioning Day": "Yes"
    }
    input_obj = BikePredictionInput(**sample_payload)
    assert input_obj.Hour == 18
    assert input_obj.Seasons == "Summer"


def test_prediction_input_schema_invalid():
    """Verify Pydantic input schema rejects invalid hour range."""
    invalid_payload = {
        "Date": "2025-07-15",
        "Hour": 28,  # Invalid hour > 23
        "Temperature": 28.5,
        "Humidity": 45.0,
        "Wind speed": 2.5,
        "Visibility": 1950.0,
        "Dew point temperature": 16.0,
        "Solar Radiation": 2.45,
        "Rainfall": 0.0,
        "Snowfall": 0.0,
        "Seasons": "Summer",
        "Holiday": "No Holiday",
        "Functioning Day": "Yes"
    }
    with pytest.raises(Exception):
        BikePredictionInput(**invalid_payload)
