import requests
import pandas as pd
import os

# Pull ~3 years of daily historical weather
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"

def get_coordinates(city_name):
    """Turn a city name into latitude/longitude using Open-Meteo's free geocoding API."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"Couldn't find a location called '{city_name}'. Try a different spelling.")

    result = data["results"][0]
    return result["latitude"], result["longitude"], result["name"], result.get("country", "")

def fetch_weather_data(city_name):
    lat, lon, resolved_name, country = get_coordinates(city_name)
    print(f"Found: {resolved_name}, {country} ({lat}, {lon})")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "precipitation_probability_max",
            "windspeed_10m_max",
            "relative_humidity_2m_mean"
        ],
        "timezone": "auto"
    }

    print("Fetching historical weather...")
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["daily"])
    df.rename(columns={"time": "date"}, inplace=True)
    df["city"] = resolved_name

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", "data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    safe_name = resolved_name.lower().replace(" ", "_")
    output_path = os.path.join(output_dir, f"{safe_name}_weather.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    city = input("Enter a city name (anywhere in the world): ")
    fetch_weather_data(city)