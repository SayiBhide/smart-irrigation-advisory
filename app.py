# ============================================================
# AI-ASSISTED SMART IRRIGATION ADVISORY SYSTEM
# For Multiple crops - Uttarakhand
#
# FINAL STREAMLIT DASHBOARD
# ============================================================

import streamlit as st
import pandas as pd
from pathlib import Path

from weather_api import (
    get_weather_data,
    UTTARAKHAND_LOCATIONS
)

from irrigation_predictor import (
    predict_irrigation,
    generate_advisory
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Smart Irrigation Advisory",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background:
        linear-gradient(
            135deg,
            #f3fff5 0%,
            #eefcf7 45%,
            #f7fff1 100%
        );
    }

    /* Main title */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        color: #14532d;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #3f6212;
        margin-bottom: 25px;
    }

    /* Section heading */
    .section-title {
        font-size: 25px;
        font-weight: 750;
        color: #166534;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    /* Cards */
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 18px;
        border-left: 6px solid #22c55e;
        box-shadow: 0px 5px 18px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }

    .weather-card {
        background: linear-gradient(
            135deg,
            #e0f2fe,
            #f0f9ff
        );
        padding: 20px;
        border-radius: 18px;
        border-left: 6px solid #0ea5e9;
        box-shadow: 0px 5px 18px rgba(0,0,0,0.08);
    }

    .prediction-card {
        background: linear-gradient(
            135deg,
            #dcfce7,
            #f0fdf4
        );
        padding: 30px;
        border-radius: 22px;
        border-left: 8px solid #16a34a;
        text-align: center;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.10);
    }

    .prediction-label {
        font-size: 18px;
        color: #166534;
        font-weight: 600;
    }

    .prediction-value {
        font-size: 48px;
        font-weight: 850;
        color: #15803d;
    }

    .advisory-card {
        background: linear-gradient(
            135deg,
            #fff7ed,
            #fffbeb
        );
        padding: 25px;
        border-radius: 18px;
        border-left: 7px solid #f59e0b;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.08);
    }

    .footer {
        text-align: center;
        padding: 25px;
        color: #64748b;
        font-size: 14px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background:
        linear-gradient(
            180deg,
            #14532d,
            #166534,
            #15803d
        );
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 700;
        padding: 12px;
    }

/* Normal text inputs */
[data-testid="stSidebar"] input:not([type="password"]) {
    color: #1b4332 !important;
    -webkit-text-fill-color: #1b4332 !important;
    background-color: white !important;
}

/* API key password box */
[data-testid="stSidebar"] input[type="password"] {
    color: #1b4332 !important;
    -webkit-text-fill-color: #1b4332 !important;
    background-color: white !important;
}

/* Dropdown text */
[data-testid="stSidebar"] [data-baseweb="select"] {
    color: #1b4332 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #1b4332 !important;
}
/* ============================================================
   MOBILE / FARMER-FRIENDLY DESIGN
   ============================================================ */

.block-container {
    padding-left: 5%;
    padding-right: 5%;
    padding-top: 1.5rem;
}

@media (max-width: 768px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
    }

    h1 {
        font-size: 1.8rem !important;
    }

    h2 {
        font-size: 1.4rem !important;
    }

    h3 {
        font-size: 1.15rem !important;
    }

    .stButton button {
        width: 100%;
        min-height: 3rem;
        font-size: 1rem;
    }
}
</style>
    
    """,
    unsafe_allow_html=True
)


# ============================================================
# PROJECT HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🌱 AI-Assisted Smart Irrigation Advisory System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Multi-Crop Irrigation Advisory using Machine Learning & Weather Forecasting'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-card">
        <b>🌾 Project Objective:</b>
        Provide an intelligent irrigation recommendation by combining
        agricultural parameters with current and forecast weather
        information for locations in Uttarakhand.
    </div>
    """,
    unsafe_allow_html=True
)
st.info(
    "🌾 Select your location, crop, growth stage and field area, then get your AI-based irrigation advisory."
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## 🌦️ Weather Configuration"
)

try:
    api_key = st.secrets["OPENWEATHER_API_KEY"]
except Exception:
    api_key = ""

if not api_key:
    st.sidebar.error("Weather service is not configured.")

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### 📍 Uttarakhand Location"
)

location = st.sidebar.selectbox(
    "Select location",
    list(UTTARAKHAND_LOCATIONS.keys())
)

st.sidebar.info(
    "Weather data is restricted to selected locations "
    "within Uttarakhand."
)


# ============================================================
# LOAD DATASET FOR INPUT OPTIONS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# Find Excel file automatically
excel_files = list(BASE_DIR.glob("*.xlsx"))

dataset = None

if len(excel_files) > 0:

    try:
        dataset = pd.read_excel(excel_files[0])

    except Exception:
        dataset = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_categories(column, fallback):

    if dataset is not None and column in dataset.columns:

        values = (
            dataset[column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if len(values) > 0:
            return sorted(values)

    return fallback


def get_numeric_default(column, fallback):

    if dataset is not None and column in dataset.columns:

        try:
            return float(dataset[column].median())
        except Exception:
            pass

    return fallback

# ============================================================
# FARMER-FRIENDLY AGRICULTURAL INPUTS
# ============================================================

st.markdown(
    '<div class="section-title">🌾 Farm Information</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)


with col1:

    crop_type = st.selectbox(
        "🌱 Crop Type",
        get_categories(
            "Crop_Type",
            [
                "Rice",
                "Maize",
                "Sugarcane",
                "Potato",
                "Wheat",
                "Cotton"
            ]
        )
    )


with col2:

    crop_growth_stage = st.selectbox(
        "🌿 Crop Growth Stage",
        get_categories(
            "Crop_Growth_Stage",
            [
                "Sowing",
                "Vegetative",
                "Flowering",
                "Harvest"
            ]
        )
    )


with col3:

    field_area = st.number_input(
        "📐 Field Area (hectare)",
        value=get_numeric_default(
            "Field_Area_hectare",
            1.0
        ),
        min_value=0.01,
        step=0.1
    )


# ============================================================
# BACKEND AGRICULTURAL PARAMETERS
# ============================================================
# These values are kept internally because the trained
# XGBoost model requires these features as inputs.
# They are not entered manually by the farmer in the
# current farmer-friendly prototype.

soil_type = get_categories(
    "Soil_Type",
    ["Loamy", "Clay", "Sandy", "Silty"]
)[0]

region = get_categories(
    "Region",
    ["Central", "East", "West", "North"]
)[0]

season = get_categories(
    "Season",
    [
        "Kharif",
        "Rabi",
        "Summer",
        "Winter",
        "Monsoon"
    ]
)[0]

irrigation_type = get_categories(
    "Irrigation_Type",
    [
        "Drip",
        "Sprinkler",
        "Flood",
        "Rainfed"
    ]
)[0]

water_source = get_categories(
    "Water_Source",
    [
        "Canal",
        "Groundwater",
        "Rainwater",
        "Reservoir"
    ]
)[0]

mulching = get_categories(
    "Mulching_Used",
    ["Yes", "No"]
)[0]

soil_ph = get_numeric_default(
    "Soil_pH",
    6.5
)

soil_moisture = get_numeric_default(
    "Soil_Moisture",
    50.0
)

organic_carbon = get_numeric_default(
    "Organic_Carbon",
    1.5
)

electrical_conductivity = get_numeric_default(
    "Electrical_Conductivity",
    1.0
)

sunlight_hours = get_numeric_default(
    "Sunlight_Hours",
    7.0
)

previous_irrigation = get_numeric_default(
    "Previous_Irrigation_mm",
    20.0
)
# ============================================================
# WEATHER BUTTON
# ============================================================

st.markdown(
    '<div class="section-title">🌦️ Live Weather Information</div>',
    unsafe_allow_html=True
)

if not api_key:

    st.warning(
        "🔑 Enter your OpenWeather API key in the sidebar "
        "to retrieve live weather information."
    )

else:

    if st.button(
        "🌦️ Get Live Uttarakhand Weather",
        use_container_width=True
    ):

        with st.spinner(
            f"Fetching weather data for {location}..."
        ):

            try:

                weather = get_weather_data(
                    api_key,
                    location
                )

                st.session_state["weather"] = weather

            except Exception as error:

                st.error(
                    f"Unable to retrieve weather data: {error}"
                )


# ============================================================
# DISPLAY WEATHER
# ============================================================

if "weather" in st.session_state:

    weather = st.session_state["weather"]

    st.markdown(
        f"""
        <div class="weather-card">
            <h3>📍 {weather['location']}, Uttarakhand</h3>
            <p>
            Current condition:
            <b>{weather['description'].title()}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    w1, w2, w3, w4 = st.columns(4)

    with w1:
        st.metric(
            "🌡️ Temperature",
            f"{weather['temperature']:.1f} °C"
        )

    with w2:
        st.metric(
            "💧 Humidity",
            f"{weather['humidity']} %"
        )

    with w3:
        st.metric(
            "🌧️ Next 24h Rain",
            f"{weather['next_24h_rainfall']:.1f} mm"
        )

    with w4:
        st.metric(
            "☔ Rain Probability",
            f"{weather['rain_probability']:.0f} %"
        )


# ============================================================
# PREDICTION SECTION
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">💧 Get Irrigation Advisory</div>',
    unsafe_allow_html=True
)

predict_button = st.button(
    "💧 GET IRRIGATION ADVISORY",
    use_container_width=True
)


if predict_button:

    # Weather must be available
    if "weather" not in st.session_state:

        st.error(
            "Please fetch the Uttarakhand weather data first."
        )

    else:

        weather = st.session_state["weather"]

        # ----------------------------------------------------
        # Model input
        # IMPORTANT:
        # State is NOT included because the trained model
        # was built using the model features from training.
        # ----------------------------------------------------

        model_input = {

            "Soil_Type": soil_type,

            "Soil_pH": soil_ph,

            "Soil_Moisture": soil_moisture,

            "Organic_Carbon": organic_carbon,

            "Electrical_Conductivity":
                electrical_conductivity,

            "Temperature_C":
                weather["temperature"],

            "Humidity":
                weather["humidity"],

            "Rainfall_mm":
                weather["next_24h_rainfall"],

            "Sunlight_Hours":
                sunlight_hours,

            "Wind_Speed_kmh":
                weather["wind_speed"] * 3.6,

            "Crop_Type":
                crop_type,

            "Crop_Growth_Stage":
                crop_growth_stage,

            "Season":
                season,

            "Irrigation_Type":
                irrigation_type,

            "Water_Source":
                water_source,

            "Field_Area_hectare":
                field_area,

            "Mulching_Used":
                mulching,

            "Previous_Irrigation_mm":
                previous_irrigation,

            "Region":
                region
        }

        try:

            with st.spinner(
                "Running the trained XGBoost model..."
            ):

                prediction, probabilities = (
                    predict_irrigation(model_input)
                )

            # ------------------------------------------------
            # Prediction result
            # ------------------------------------------------

            st.markdown("### 💧 Irrigation Requirement")

            if prediction.upper() == "HIGH":
              st.error(f"## {prediction.upper()}")
            elif prediction.upper() == "MEDIUM":
              st.warning(f"## {prediction.upper()}")
            else:
              st.success(f"## {prediction.upper()}")

            st.write("")

            # ------------------------------------------------
            # Confidence
            # ------------------------------------------------

            if probabilities:

                st.markdown(
                    "### 📊 Model Prediction Confidence"
                )

                p1, p2, p3 = st.columns(3)

                confidence_items = [
                    ("Low", p1),
                    ("Medium", p2),
                    ("High", p3)
                ]

                for label, column in confidence_items:

                    with column:

                        value = probabilities.get(
                            label,
                            0
                        )

                        st.metric(
                            label,
                            f"{value:.2f}%"
                        )

                        st.progress(
                            min(
                                max(
                                    int(value),
                                    0
                                ),
                                100
                            )
                        )

            # ------------------------------------------------
            # Advisory
            # ------------------------------------------------

            advisory = generate_advisory(
                prediction,
                weather["next_24h_rainfall"],
                weather["rain_probability"]
            )

            st.markdown("### 💡 Irrigation Advisory")
            st.info(advisory)

            # ------------------------------------------------
            # Input summary
            # ------------------------------------------------

            st.markdown(
                "### 📋 Analysis Summary"
            )

            summary_col1, summary_col2 = st.columns(2)

            with summary_col1:

                st.write(
                    f"**📍 Location:** {location}, Uttarakhand"
                )

                st.write(
                    f"**🌱 Crop:** {crop_type}"
                )

                st.write(
                    f"**🌿 Growth Stage:** {crop_growth_stage}"
                )

                st.write(
                    f"**💧 Soil Moisture:** "
                    f"{soil_moisture:.2f}"
                )

            with summary_col2:

                st.write(
                    f"**🌡️ Temperature:** "
                    f"{weather['temperature']:.1f} °C"
                )

                st.write(
                    f"**💦 Humidity:** "
                    f"{weather['humidity']}%"
                )

                st.write(
                    f"**🌧️ Forecast Rainfall:** "
                    f"{weather['next_24h_rainfall']:.1f} mm"
                )

                st.write(
                    f"**💨 Wind Speed:** "
                    f"{weather['wind_speed'] * 3.6:.1f} km/h"
                )

        except Exception as error:

            st.error(
                "Prediction could not be generated."
            )

            st.exception(error)


# ============================================================
# MODEL INFORMATION
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🤖 Machine Learning Model</div>',
    unsafe_allow_html=True
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "Selected Model",
        "XGBoost"
    )

with m2:
    st.metric(
        "Test Accuracy",
        "99.65%"
    )

with m3:
    st.metric(
        "F1 Score",
        "99.65%"
    )

with m4:
    st.metric(
        "R² Score",
        "98.89%"
    )

st.info(
    "The XGBoost model was selected after comparing "
    "Random Forest, Decision Tree, XGBoost and SVM "
    "on the project dataset."
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

    🌱 <b>AI-Assisted Smart Irrigation Advisory System</b><br>

    Multi-Crop • Uttarakhand • Machine Learning • Weather Forecasting

    <br><br>

    This system provides an ML-based irrigation advisory
    using agricultural inputs and weather information.

    </div>
    """,
    unsafe_allow_html=True
)