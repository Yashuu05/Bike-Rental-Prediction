import os
import random
from datetime import datetime, timedelta
import pandas as pd

def generate_sample_dataset(
    num_samples: int = 100,
    input_features_path: str = "data/raw/input_features.csv",
    output_path: str = "data/raw/sample_dataset.csv"
):
    """
    Generates a synthetic sample dataset for bike sharing / climate loan analytics.
    Guarantees equal list lengths for all features per row.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    #os.makedirs(os.path.dirname(input_features_path), exist_ok=True)

    # Define features and their respective value choices / ranges
    seasons = ["Winter", "Spring", "Summer", "Autumn"]
    holidays = ["No Holiday", "Holiday"]
    functioning_days = ["Yes", "No"]

    start_date = datetime(2025, 1, 1)

    # Initialize lists to store row values
    records = []

    for i in range(num_samples):
        current_date = start_date + timedelta(days=i)
        month = current_date.month

        # Assign season based on month
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Autumn"

        # Simulating realistic correlated features
        is_holiday = "Holiday" if random.random() < 0.05 else "No Holiday"
        is_functioning = "No" if (is_holiday == "Holiday" and random.random() < 0.6) else "Yes"

        # Continuous meteorological features
        if season == "Winter":
            temp = round(random.uniform(-10.0, 8.0), 1)
        elif season == "Spring":
            temp = round(random.uniform(8.0, 22.0), 1)
        elif season == "Summer":
            temp = round(random.uniform(22.0, 38.0), 1)
        else: # Autumn
            temp = round(random.uniform(10.0, 24.0), 1)

        humidity = random.randint(20, 95)
        wind_speed = round(random.uniform(0.5, 7.5), 1)
        visibility = random.randint(300, 2000)
        solar_radiation = round(random.uniform(0.0, 3.5), 2)
        rainfall = round(random.expovariate(1/0.5), 1) if random.random() < 0.2 else 0.0
        snowfall = round(random.expovariate(1/0.8), 1) if (season == "Winter" and temp < 2.0 and random.random() < 0.3) else 0.0

        # Target metric: Rented Bike Count
        if is_functioning == "No":
            rented_bike_count = 0
        else:
            base_count = 500 + int(temp * 25) + int(solar_radiation * 150) - int(humidity * 3)
            if is_holiday == "Holiday":
                base_count = int(base_count * 0.7)
            rented_bike_count = max(0, base_count + random.randint(-150, 150))

        row = {
            "Date": current_date.strftime("%Y-%m-%d"),
            "Rented Bike Count": rented_bike_count,
            "Hour": random.randint(0, 23),
            "Temperature(°C)": temp,
            "Humidity(%)": humidity,
            "Wind speed (m/s)": wind_speed,
            "Visibility (10m)": visibility,
            "Solar Radiation (MJ/m2)": solar_radiation,
            "Rainfall(mm)": rainfall,
            "Snowfall (cm)": snowfall,
            "Seasons": season,
            "Holiday": is_holiday,
            "Functioning Day": is_functioning
        }
        records.append(row)

    df = pd.DataFrame(records)

    # Save generated sample dataset
    df.to_csv(output_path, index=False)
    
    # Also save the template/input_features.csv for reference
    #df.head(10).to_csv(input_features_path, index=False)

    print(f"Successfully generated dataset with shape: {df.shape}")
    print(f"Dataset saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    import os 
    import sys
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    from configs.paths import Paths
    os.path.exists(Paths.INPUT_FEATURES_FILE)
    df = generate_sample_dataset(num_samples=1000,
                            input_features_path=Paths.INPUT_FEATURES_FILE,
                            output_path=Paths.SAMPLE_DATASET_PATH)

    print(df.head())