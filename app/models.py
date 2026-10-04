from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from app.database import Base

class PredictionRecord(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Input Features
    date_val = Column(String(20), nullable=False)
    hour = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    visibility = Column(Float, nullable=False)
    dew_point_temp = Column(Float, nullable=False)
    solar_radiation = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False)
    snowfall = Column(Float, nullable=False)
    seasons = Column(String(20), nullable=False)
    holiday = Column(String(20), nullable=False)
    functioning_day = Column(String(10), nullable=False)
    
    # Output Predictions
    predicted_count = Column(Integer, nullable=False)
    raw_prediction = Column(Float, nullable=False)
    demand_level = Column(String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "date": self.date_val,
            "hour": self.hour,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "seasons": self.seasons,
            "predicted_count": self.predicted_count,
            "demand_level": self.demand_level
        }
