from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Literal
from datetime import datetime

class BikePredictionInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    Date: str = Field(..., description="Date in YYYY-MM-DD format", examples=["2025-06-15"])
    Hour: int = Field(..., ge=0, le=23, description="Hour of the day (0-23)", examples=[17])
    Temperature: float = Field(..., description="Temperature in °C", examples=[24.5])
    Humidity: float = Field(..., ge=0, le=100, description="Relative humidity percentage (0-100)", examples=[55.0])
    Wind_speed: float = Field(..., alias="Wind speed", ge=0.0, description="Wind speed in m/s", examples=[2.1])
    Visibility: float = Field(..., ge=0.0, description="Visibility in 10m unit", examples=[1800.0])
    Dew_point_temperature: float = Field(default=0.0, alias="Dew point temperature", description="Dew point temperature in °C", examples=[12.5])
    Solar_Radiation: float = Field(..., alias="Solar Radiation", ge=0.0, description="Solar Radiation in MJ/m2", examples=[1.85])
    Rainfall: float = Field(..., ge=0.0, description="Rainfall in mm", examples=[0.0])
    Snowfall: float = Field(..., ge=0.0, description="Snowfall in cm", examples=[0.0])
    Seasons: Literal["Winter", "Spring", "Summer", "Autumn"] = Field(..., description="Season of the year")
    Holiday: Literal["No Holiday", "Holiday"] = Field(..., description="Holiday indicator")
    Functioning_Day: Literal["Yes", "No"] = Field(..., alias="Functioning Day", description="Functioning day indicator")

    @field_validator("Date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be a valid date string in YYYY-MM-DD format")

class BikePredictionResponse(BaseModel):
    status: str
    predicted_rented_bike_count: int
    raw_prediction: float
    demand_level: str
    inputs: dict
