from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import os
import joblib
import requests
import numpy as np
import pandas as pd


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Weather Forecast API",
    description="Weather forecasting API using ML + Open-Meteo",
    version="1.0"
)


# =========================================================
# CORS
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# MODEL PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)


# =========================================================
# LOAD MODELS
# =========================================================

def load_model(filename):

    path = os.path.join(
        MODEL_DIR,
        filename
    )

    if not os.path.exists(path):
        print(f"WARNING: Model not found: {path}")
        return None

    return joblib.load(path)


temp_model = load_model("temp_model.pkl")
rain_model = load_model("rain_model.pkl")
humidity_model = load_model("humidity_model.pkl")
feature_cols = load_model("feature_cols.pkl")


print("Temperature model:", temp_model is not None)
print("Rain model:", rain_model is not None)
print("Humidity model:", humidity_model is not None)
print("Feature columns:", feature_cols)


# =========================================================
# WEATHER DESCRIPTION
# =========================================================

def get_weather_description(code):

    descriptions = {

        0: "Clear sky",

        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",

        45: "Fog",
        48: "Depositing rime fog",

        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",

        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",

        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",

        66: "Light freezing rain",
        67: "Heavy freezing rain",

        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",

        77: "Snow grains",

        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",

        85: "Slight snow showers",
        86: "Heavy snow showers",

        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }

    return descriptions.get(
        int(code),
        "Unknown weather"
    )


# =========================================================
# WEATHER TIP
# =========================================================

def get_weather_tip(
    temperature,
    humidity,
    rain_probability,
    windspeed
):

    if rain_probability >= 0.75:
        return (
            "Rain is quite likely. "
            "Carry an umbrella and plan accordingly."
        )

    if rain_probability >= 0.45:
        return (
            "There is a moderate chance of rain. "
            "Keeping an umbrella nearby is a good idea."
        )

    if temperature >= 35:
        return (
            "It may feel hot today. "
            "Stay hydrated and avoid prolonged afternoon exposure."
        )

    if temperature >= 32:
        return (
            "It may feel warm today. "
            "Drink enough water and use sun protection."
        )

    if humidity >= 80:
        return (
            "Humidity is high. "
            "Light clothing and good hydration may help."
        )

    if windspeed >= 30:
        return (
            "Strong winds are expected. "
            "Be careful around trees and loose objects."
        )

    return (
        "Weather conditions look relatively comfortable. "
        "Have a great day!"
    )


# =========================================================
# ALERT GENERATION
# =========================================================

def generate_alerts(current, forecast):

    alerts = []


    # -----------------------------------------------------
    # RAIN
    # -----------------------------------------------------

    max_rain_probability = max(
        [
            float(
                day.get(
                    "rain_probability",
                    0
                )
            )
            for day in forecast
        ],
        default=0
    )

    # Only show a rain alert for genuinely high probability.
    # This avoids treating 40-60% rain chances as warnings.

    if max_rain_probability >= 0.75:

        alerts.append({
            "type": "rain",
            "severity": "medium",
            "title": "High Chance of Rain",
            "message": (
                "The forecast shows a high probability "
                "of precipitation during the upcoming period."
            ),
            "official": False
        })


    # -----------------------------------------------------
    # EXTREME HEAT
    # -----------------------------------------------------

    max_temperature = max(
        [
            float(
                day.get(
                    "temperature",
                    0
                )
            )
            for day in forecast
        ],
        default=0
    )

    if max_temperature >= 40:

        alerts.append({
            "type": "heat",
            "severity": "high",
            "title": "Extreme Heat",
            "message": (
                "Very high temperatures are possible. "
                "Stay hydrated and avoid prolonged exposure "
                "to heat."
            ),
            "official": False
        })


    # -----------------------------------------------------
    # STRONG WIND
    # -----------------------------------------------------

    max_wind = max(
        [
            float(
                day.get(
                    "windspeed",
                    0
                )
            )
            for day in forecast
        ],
        default=0
    )

    if max_wind >= 40:

        alerts.append({
            "type": "wind",
            "severity": "high",
            "title": "Strong Winds",
            "message": (
                "Strong winds may occur. "
                "Be careful around trees and unsecured objects."
            ),
            "official": False
        })


    # -----------------------------------------------------
    # HIGH HUMIDITY
    # -----------------------------------------------------

    current_humidity = float(
        current.get(
            "humidity",
            0
        )
    )

    if current_humidity >= 90:

        alerts.append({
            "type": "humidity",
            "severity": "medium",
            "title": "Very High Humidity",
            "message": (
                "Humidity is currently very high "
                "and may make the weather feel uncomfortable."
            ),
            "official": False
        })


    # -----------------------------------------------------
    # IMPORTANT:
    # NO AUTOMATIC THUNDERSTORM WARNING
    # -----------------------------------------------------
    #
    # Weather code 95/96/99 describes forecast conditions,
    # but it should NOT automatically be presented as a
    # serious weather warning.
    #
    # Official warnings should come from an official
    # meteorological/disaster-management source.
    #
    # Therefore we intentionally do NOT create a
    # "Thunderstorm Possible" alert here.


    # -----------------------------------------------------
    # IMPORTANT:
    # NO AUTOMATIC FLOOD ALERT
    # -----------------------------------------------------
    #
    # Rain probability alone cannot establish a flood warning.
    #
    # Flood alerts require additional information such as:
    # - rainfall amount
    # - rainfall duration
    # - river/water levels
    # - drainage conditions
    # - official warnings
    #
    # Therefore no flood alert is generated here.


    # -----------------------------------------------------
    # IMPORTANT:
    # NO AUTOMATIC LANDSLIDE ALERT
    # -----------------------------------------------------
    #
    # A weather forecast alone cannot reliably determine
    # landslide risk for a city.
    #
    # Therefore no landslide alert is generated here.


    # -----------------------------------------------------
    # NORMAL WEATHER
    # -----------------------------------------------------

    if not alerts:

        alerts.append({
            "type": "normal",
            "severity": "low",
            "title": "No Major Weather Alerts",
            "message": (
                "No major forecast-based weather indicators "
                "were detected."
            ),
            "official": False
        })


    return alerts


# =========================================================
# GEOCODING
# =========================================================

def get_coordinates(city):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("results"):

        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' not found."
        )

    result = data["results"][0]

    return {
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "name": result.get(
            "name",
            city
        ),
        "country": result.get(
            "country",
            ""
        )
    }


# =========================================================
# CURRENT WEATHER
# =========================================================

def get_current_weather(
    latitude,
    longitude
):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "rain",
            "showers",
            "snowfall",
            "weather_code",
            "wind_speed_10m"
        ]),

        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    current = data.get("current", {})

    temperature = float(
        current.get("temperature_2m", 0)
    )

    humidity = float(
        current.get("relative_humidity_2m", 0)
    )

    feels_like = float(
        current.get("apparent_temperature", 0)
    )

    precipitation = float(
        current.get("precipitation", 0)
    )

    rain = float(
        current.get("rain", 0)
    )

    showers = float(
        current.get("showers", 0)
    )

    snowfall = float(
        current.get("snowfall", 0)
    )

    weather_code = int(
        current.get("weather_code", 0)
    )

    windspeed = float(
        current.get("wind_speed_10m", 0)
    )

    # =====================================================
    # CURRENT WEATHER CONDITION
    # =====================================================

    # Actual precipitation takes priority.
    if snowfall > 0:
        description = "Snow"

    elif rain > 0:
        description = "Rain"

    elif showers > 0:
        description = "Rain showers"

    elif precipitation > 0:
        description = "Drizzle"

    # No actual precipitation: use cloud condition.
    elif weather_code == 0:
        description = "Clear sky"

    elif weather_code == 1:
        description = "Mainly clear"

    elif weather_code == 2:
        description = "Partly cloudy"

    elif weather_code == 3:
        description = "Overcast"

    elif weather_code in [45, 48]:
        description = "Foggy"

    else:
        description = get_weather_description(
            weather_code
        )

    return {

        "temperature": temperature,

        "humidity": humidity,

        "feels_like": feels_like,

        "precipitation": precipitation,

        "rain": rain,

        "showers": showers,

        "snowfall": snowfall,

        "weather_code": weather_code,

        "windspeed": windspeed,

        "time": current.get(
            "time",
            ""
        ),

        "description": description
    }
# =========================================================
# OPEN-METEO DAILY FORECAST
# =========================================================

def get_open_meteo_forecast(
    latitude,
    longitude,
    days=7
):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": ",".join([
            "temperature_2m_mean",
            "precipitation_probability_max",
            "precipitation_probability_mean",
            "relative_humidity_2m_mean",
            "wind_speed_10m_max",
            "weather_code"
        ]),

        "forecast_days": days,

        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    daily = data.get(
        "daily",
        {}
    )


    dates = daily.get(
        "time",
        []
    )

    temperatures = daily.get(
        "temperature_2m_mean",
        []
    )

    rain_max = daily.get(
        "precipitation_probability_max",
        []
    )

    rain_mean = daily.get(
        "precipitation_probability_mean",
        []
    )

    humidity = daily.get(
        "relative_humidity_2m_mean",
        []
    )

    wind = daily.get(
        "wind_speed_10m_max",
        []
    )

    weather_codes = daily.get(
        "weather_code",
        []
    )


    forecast = []


    for i in range(len(dates)):

        temperature = (
            temperatures[i]
            if i < len(temperatures)
            and temperatures[i] is not None
            else 0
        )


        probability = (
            rain_max[i]
            if i < len(rain_max)
            and rain_max[i] is not None
            else 0
        )


        probability_mean = (
            rain_mean[i]
            if i < len(rain_mean)
            and rain_mean[i] is not None
            else probability
        )


        humidity_value = (
            humidity[i]
            if i < len(humidity)
            and humidity[i] is not None
            else 0
        )


        wind_value = (
            wind[i]
            if i < len(wind)
            and wind[i] is not None
            else 0
        )


        weather_code = (
            weather_codes[i]
            if i < len(weather_codes)
            and weather_codes[i] is not None
            else 0
        )


        # -------------------------------------------------
        # RAIN PROBABILITY
        # -------------------------------------------------
        #
        # Open-Meteo returns precipitation probability
        # as a percentage such as 45.
        #
        # We expose:
        #
        # rain_probability = 0.45
        # rain_probability_percent = 45
        #
        # This prevents accidental 100% display caused
        # by incorrect percentage conversion.
        # -------------------------------------------------

        probability = max(
            0,
            min(
                100,
                float(probability)
            )
        )

        probability_mean = max(
            0,
            min(
                100,
                float(probability_mean)
            )
        )


        rain_probability = (
            probability / 100.0
        )


        forecast.append({

            "date": dates[i],

            "temperature": round(
                float(temperature),
                1
            ),

            "humidity": round(
                float(humidity_value)
            ),

            "rain_probability": round(
                rain_probability,
                2
            ),

            "rain_probability_percent": round(
                probability
            ),

            "rain_probability_mean_percent": round(
                probability_mean
            ),

            "windspeed": round(
                float(wind_value),
                1
            ),

            "weather_code": int(
                weather_code
            ),

            "description": get_weather_description(
                weather_code
            ),

            "source": "Open-Meteo"
        })


    return forecast


# =========================================================
# OPTIONAL ML PREDICTION
# =========================================================

def get_ml_prediction():

    """
    The ML models remain loaded for the project.

    Rain probability is intentionally NOT taken
    from rain_model.predict_proba() for the dashboard.

    The dashboard uses Open-Meteo precipitation
    probability because it provides an actual
    precipitation-probability forecast.
    """

    result = {

        "temperature_model_available":
            temp_model is not None,

        "humidity_model_available":
            humidity_model is not None,

        "rain_model_available":
            rain_model is not None
    }

    return result


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {

        "message":
            "Weather Forecast API is running",

        "rain_probability_source":
            "Open-Meteo precipitation probability",

        "ml_models":
            get_ml_prediction(),

        "alerts_source":
            "Forecast-based indicators only",

        "official_alerts":
            False
    }


# =========================================================
# FORECAST ENDPOINT
# =========================================================

@app.get("/forecast")
def forecast(
    city: str,
    days: int = 7
):

    try:

        # ---------------------------------------------
        # LIMIT DAYS
        # ---------------------------------------------

        if days < 1:
            days = 1

        if days > 16:
            days = 16


        # ---------------------------------------------
        # GET CITY COORDINATES
        # ---------------------------------------------

        location = get_coordinates(
            city
        )

        latitude = location["latitude"]

        longitude = location["longitude"]


        # ---------------------------------------------
        # CURRENT WEATHER
        # ---------------------------------------------

        current = get_current_weather(
            latitude,
            longitude
        )


        # ---------------------------------------------
        # DAILY FORECAST
        # ---------------------------------------------

        forecast_data = get_open_meteo_forecast(
            latitude,
            longitude,
            days
        )


        # ---------------------------------------------
        # ADD WEATHER TIPS
        # ---------------------------------------------

        for day in forecast_data:

            day["tip"] = get_weather_tip(

                day["temperature"],

                day["humidity"],

                day["rain_probability"],

                day["windspeed"]
            )


        # ---------------------------------------------
        # ALERTS
        # ---------------------------------------------

        alerts = generate_alerts(
            current,
            forecast_data
        )


        # ---------------------------------------------
        # RESPONSE
        # ---------------------------------------------

        return {

            "city": location["name"],

            "country": location["country"],

            "latitude": latitude,

            "longitude": longitude,

            "current": {

                **current,

                "description":
                    get_weather_description(
                        current["weather_code"]
                    )
            },

            "forecast": forecast_data,

            "alerts": alerts,

            "rain_probability_source":
                "Open-Meteo",

            "notice": (
                "Weather alerts are forecast-based indicators "
                "and are not official government warnings. "
                "For official warnings, refer to the relevant "
                "government meteorological or disaster-management "
                "authority."
            )
        }


    except requests.RequestException as e:

        raise HTTPException(

            status_code=502,

            detail=(
                "Unable to retrieve weather data "
                f"from Open-Meteo: {str(e)}"
            )
        )


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# =========================================================
# ALERTS ENDPOINT
# =========================================================

@app.get("/alerts")
def alerts(
    city: str
):

    try:

        location = get_coordinates(
            city
        )


        current = get_current_weather(

            location["latitude"],

            location["longitude"]
        )


        forecast_data = get_open_meteo_forecast(

            location["latitude"],

            location["longitude"],

            7
        )


        generated_alerts = generate_alerts(

            current,

            forecast_data
        )


        return {

            "city": location["name"],

            "alerts": generated_alerts,

            "official": False,

            "notice": (
                "These are forecast-based indicators, "
                "not official government weather warnings."
            )
        }


    except requests.RequestException as e:

        raise HTTPException(

            status_code=502,

            detail=(
                "Unable to retrieve weather data "
                f"from Open-Meteo: {str(e)}"
            )
        )


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )

