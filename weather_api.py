# ============================================================
# WEATHER API MODULE
# Smart Irrigation Advisory System
# Location restricted to Uttarakhand, India
# ============================================================

import requests


# ------------------------------------------------------------
# Uttarakhand locations
# These are the locations available for weather selection.
# ------------------------------------------------------------

UTTARAKHAND_LOCATIONS = {
    "Dehradun": "Dehradun,Uttarakhand,IN",
    "Haridwar": "Haridwar,Uttarakhand,IN",
    "Nainital": "Nainital,Uttarakhand,IN",
    "Almora": "Almora,Uttarakhand,IN",
    "Pauri": "Pauri,Uttarakhand,IN",
    "Tehri": "Tehri,Uttarakhand,IN",
    "Uttarkashi": "Uttarkashi,Uttarakhand,IN",
    "Chamoli": "Chamoli,Uttarakhand,IN",
    "Rudraprayag": "Rudraprayag,Uttarakhand,IN",
    "Pithoragarh": "Pithoragarh,Uttarakhand,IN",
    "Bageshwar": "Bageshwar,Uttarakhand,IN",
    "Champawat": "Champawat,Uttarakhand,IN",
    "Rudrapur": "Rudrapur,Uttarakhand,IN"
}


# ------------------------------------------------------------
# Get current weather
# ------------------------------------------------------------

def get_current_weather(api_key, location):

    if location not in UTTARAKHAND_LOCATIONS:
        raise ValueError(
            "Invalid location. Please select a location from Uttarakhand."
        )

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": UTTARAKHAND_LOCATIONS[location],
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=15)

    if response.status_code != 200:
        try:
            error_message = response.json().get("message", "Unknown API error")
        except Exception:
            error_message = "Unable to connect to weather service."

        raise RuntimeError(
            f"OpenWeather API Error: {error_message}"
        )

    data = response.json()

    weather = {
        "location": location,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "description": data["weather"][0]["description"],
        "weather_main": data["weather"][0]["main"]
    }

    # Current rainfall, if available
    if "rain" in data:
        weather["current_rainfall"] = (
            data["rain"].get("1h", 0)
            if isinstance(data["rain"], dict)
            else 0
        )
    else:
        weather["current_rainfall"] = 0.0

    return weather


# ------------------------------------------------------------
# Get next 24-hour rainfall forecast
# OpenWeather forecast gives 3-hour intervals.
# 8 intervals ≈ next 24 hours.
# ------------------------------------------------------------

def get_rainfall_forecast(api_key, location):

    if location not in UTTARAKHAND_LOCATIONS:
        raise ValueError(
            "Invalid location. Please select a location from Uttarakhand."
        )

    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": UTTARAKHAND_LOCATIONS[location],
        "appid": api_key,
        "units": "metric",
        "cnt": 8
    }

    response = requests.get(url, params=params, timeout=15)

    if response.status_code != 200:
        try:
            error_message = response.json().get("message", "Unknown API error")
        except Exception:
            error_message = "Unable to connect to weather service."

        raise RuntimeError(
            f"OpenWeather Forecast Error: {error_message}"
        )

    data = response.json()

    total_rainfall = 0.0
    maximum_rain_probability = 0.0

    for item in data.get("list", []):

        # Rainfall during that 3-hour period
        rain_data = item.get("rain", {})

        if isinstance(rain_data, dict):
            total_rainfall += rain_data.get("3h", 0.0)

        # Probability of precipitation
        probability = item.get("pop", 0.0)

        if probability > maximum_rain_probability:
            maximum_rain_probability = probability

    return {
        "next_24h_rainfall": round(total_rainfall, 2),
        "rain_probability": round(maximum_rain_probability * 100, 1)
    }


# ------------------------------------------------------------
# Get complete weather information
# ------------------------------------------------------------

def get_weather_data(api_key, location):

    current = get_current_weather(api_key, location)

    forecast = get_rainfall_forecast(api_key, location)

    weather_data = {
        "location": location,
        "temperature": current["temperature"],
        "humidity": current["humidity"],
        "wind_speed": current["wind_speed"],
        "description": current["description"],
        "weather_main": current["weather_main"],
        "current_rainfall": current["current_rainfall"],
        "next_24h_rainfall": forecast["next_24h_rainfall"],
        "rain_probability": forecast["rain_probability"]
    }

    return weather_data