from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import requests
import os
app = FastAPI(title="Weather Forecast API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"],
    allow_headers=["*"],
)
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "..", "models")
temp_model = joblib.load(os.path.join(models_dir, "temp_model.pkl"))
rain_model = joblib.load(os.path.join(models_dir, "rain_model.pkl"))
feature_cols = joblib.load(os.path.join(models_dir, "feature_cols.pkl"))
class ForecastRequest(BaseModel):
    city: str
    days: int = 7
def get_coordinates(city_name: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"Couldn't find '{city_name}'")
    result = data["results"][0]
    return result["latitude"], result["longitude"], result["name"], result.get("country", "")
def get_recent_weather(lat, lon):
    """Get the last ~14 days of real weather so we have enough history to build lag/rolling features."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    end_date = pd.Timestamp.today().normalize() - pd.Timedelta(days=1)
    start_date = end_date - pd.Timedelta(days=14)
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily": [
            "temperature_2m_mean", "precipitation_sum",
            "windspeed_10m_max", "relative_humidity_2m_mean"
        ],
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data["daily"])
    df.rename(columns={"time": "date"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    return df
@app.get("/")
def root():
    return {"message": "Weather Forecast API is running"}
@app.post("/forecast")
def forecast(request: ForecastRequest):
    try:
        lat, lon, resolved_name, country = get_coordinates(request.city)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    recent = get_recent_weather(lat, lon)
    predictions = []
    history = recent.copy()
    for i in range(request.days):
        last_row = history.iloc[-1]
        recent_7 = history.tail(7)
        day_of_year = (history["date"].max() + pd.Timedelta(days=1)).dayofyear
        features = pd.DataFrame([{
            "temp_mean_lag1": last_row["temperature_2m_mean"],
            "rain_lag1": last_row["precipitation_sum"],
            "humidity_lag1": last_row["relative_humidity_2m_mean"],
            "temp_mean_roll7": recent_7["temperature_2m_mean"].mean(),
            "rain_sum_roll7": recent_7["precipitation_sum"].sum(),
            "season_sin": np.sin(2 * np.pi * day_of_year / 365),
            "season_cos": np.cos(2 * np.pi * day_of_year / 365),
            "windspeed_10m_max": last_row["windspeed_10m_max"],
            "relative_humidity_2m_mean": last_row["relative_humidity_2m_mean"],
        }])[feature_cols]
        pred_temp = float(temp_model.predict(features)[0])
        pred_rain_prob = float(rain_model.predict_proba(features)[0][1])
        next_date = history["date"].max() + pd.Timedelta(days=1)
        predictions.append({
            "date": next_date.strftime("%Y-%m-%d"),
            "temperature": round(pred_temp, 1),
            "rain_probability": round(pred_rain_prob, 2),
            "windspeed": round(float(last_row["windspeed_10m_max"]), 1)
        })
        new_row = pd.DataFrame([{
            "date": next_date,
            "temperature_2m_mean": pred_temp,
            "precipitation_sum": pred_rain_prob * 5,  # rough estimate for rolling calc
            "windspeed_10m_max": last_row["windspeed_10m_max"],
            "relative_humidity_2m_mean": last_row["relative_humidity_2m_mean"],
        }])
        history = pd.concat([history, new_row], ignore_index=True)
    return {
        "city": resolved_name,
        "country": country,
        "forecast": predictions
    }