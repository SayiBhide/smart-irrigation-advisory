# ============================================================
# AI-ASSISTED SMART IRRIGATION ADVISORY SYSTEM
# Multi-Crop - Uttarakhand
# FINAL MULTILINGUAL STREAMLIT DASHBOARD
# ============================================================

import streamlit as st
import pandas as pd
from pathlib import Path

from weather_api import get_weather_data, UTTARAKHAND_LOCATIONS
from irrigation_predictor import predict_irrigation

from translations import (
    LANGUAGES,
    CROP_VALUES,
    STAGE_VALUES,
    tr,
    display_crop,
    display_stage,
    display_weather_condition,
    localized_advisory
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
# LANGUAGE SELECTION
# ============================================================

if "language" not in st.session_state:
    st.session_state["language"] = "English"

language = st.selectbox(
    "🌐 " + tr(st.session_state["language"], "language"),
    LANGUAGES,
    index=LANGUAGES.index(st.session_state["language"]),
    key="language_selector"
)

st.session_state["language"] = language


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg,
            #f3fff5 0%,
            #eefcf7 45%,
            #f7fff1 100%
        );
    }

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

    .section-title {
        font-size: 25px;
        font-weight: 750;
        color: #166534;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .info-card {
        background: white;
        padding: 20px;
        border-radius: 18px;
        border-left: 6px solid #22c55e;
        box-shadow: 0px 5px 18px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }

    .weather-card {
        background: linear-gradient(135deg, #e0f2fe, #f0f9ff);
        padding: 20px;
        border-radius: 18px;
        border-left: 6px solid #0ea5e9;
        box-shadow: 0px 5px 18px rgba(0,0,0,0.08);
    }

    .footer {
        text-align: center;
        padding: 25px;
        color: #64748b;
        font-size: 14px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #14532d,
            #166534,
            #15803d
        );
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 700;
        padding: 12px;
    }

    [data-testid="stSidebar"] input:not([type="password"]) {
        color: #1b4332 !important;
        -webkit-text-fill-color: #1b4332 !important;
        background-color: white !important;
    }

    [data-testid="stSidebar"] input[type="password"] {
        color: #1b4332 !important;
        -webkit-text-fill-color: #1b4332 !important;
        background-color: white !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] {
        color: #1b4332 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #1b4332 !important;
    }

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
    f'<div class="main-title">{tr(language, "project_title")}</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="subtitle">{tr(language, "subtitle")}</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="info-card">
        <b>{tr(language, "objective")}</b>
    </div>
    """,
    unsafe_allow_html=True
)

st.info(tr(language, "intro"))


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## " + tr(language, "weather_config")
)

try:
    api_key = st.secrets["OPENWEATHER_API_KEY"]
except Exception:
    api_key = ""

if not api_key:
    st.sidebar.error(tr(language, "api_missing"))

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### " + tr(language, "location")
)

location = st.sidebar.selectbox(
    tr(language, "select_location"),
    list(UTTARAKHAND_LOCATIONS.keys())
)

st.sidebar.info(
    tr(language, "location_info")
)

# Clear old weather when the selected location changes.
if st.session_state.get("weather_location") != location:
    st.session_state.pop("weather", None)


# ============================================================
# LOAD DATASET FOR INTERNAL DEFAULTS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
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
    f'<div class="section-title">{tr(language, "farm_info")}</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    # Display localized crop names, but keep the original
    # English dataset value for the trained model.
    crop_display_options = [
        display_crop(language, value) for value in CROP_VALUES
    ]

    selected_crop_display = st.selectbox(
        tr(language, "crop_type"),
        crop_display_options
    )

    crop_type = CROP_VALUES[crop_display_options.index(
        selected_crop_display
    )]


with col2:
    # Display localized growth-stage names, but keep the
    # original English dataset value internally.
    stage_display_options = [
        display_stage(language, value) for value in STAGE_VALUES
    ]

    selected_stage_display = st.selectbox(
        tr(language, "growth_stage"),
        stage_display_options
    )

    crop_growth_stage = STAGE_VALUES[stage_display_options.index(
        selected_stage_display
    )]


with col3:
    field_area = st.number_input(
        tr(language, "field_area"),
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
# They are derived from the project dataset and are not
# claimed to be live field measurements.

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
    ["Kharif", "Rabi", "Summer", "Winter", "Monsoon"]
)[0]

irrigation_type = get_categories(
    "Irrigation_Type",
    ["Drip", "Sprinkler", "Flood", "Rainfed"]
)[0]

water_source = get_categories(
    "Water_Source",
    ["Canal", "Groundwater", "Rainwater", "Reservoir"]
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
    f'<div class="section-title">{tr(language, "weather_section")}</div>',
    unsafe_allow_html=True
)

if not api_key:

    st.warning(tr(language, "api_missing"))

else:

    if st.button(
        tr(language, "get_weather"),
        use_container_width=True
    ):

        with st.spinner(
            tr(language, "fetching", location=location)
        ):

            try:

                weather = get_weather_data(
                    api_key,
                    location
                )

                st.session_state["weather"] = weather
                st.session_state["weather_location"] = location

            except Exception as error:

                st.error(
                    tr(language, "weather_error", error=error)
                )


# ============================================================
# DISPLAY WEATHER
# ============================================================

if "weather" in st.session_state:

    weather = st.session_state["weather"]

    translated_condition = display_weather_condition(
        language,
        weather.get("weather_main", ""),
        weather["description"].title()
    )

    st.markdown(
        f"""
        <div class="weather-card">
            <h3>📍 {weather['location']}, Uttarakhand</h3>
            <p>
                {tr(language, "live_condition")}:
                <b>{translated_condition}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    w1, w2, w3, w4 = st.columns(4)

    with w1:
        st.metric(
            tr(language, "live_temperature"),
            f"{weather['temperature']:.1f} °C"
        )

    with w2:
        st.metric(
            tr(language, "live_humidity"),
            f"{weather['humidity']} %"
        )

    with w3:
        st.metric(
            tr(language, "forecast_rainfall"),
            f"{weather['next_24h_rainfall']:.1f} mm"
        )

    with w4:
        st.metric(
            tr(language, "rain_probability"),
            f"{weather['rain_probability']:.0f} %"
        )


# ============================================================
# PREDICTION SECTION
# ============================================================

st.markdown("---")

st.markdown(
    f'<div class="section-title">{tr(language, "prediction_section")}</div>',
    unsafe_allow_html=True
)

predict_button = st.button(
    tr(language, "get_advisory"),
    use_container_width=True
)


if predict_button:

    if "weather" not in st.session_state:

        st.error(tr(language, "fetch_first"))

    else:

        weather = st.session_state["weather"]

        # ----------------------------------------------------
        # MODEL INPUT
        # ----------------------------------------------------
        # Farmer-facing inputs remain simple.
        # The remaining technical features are filled internally
        # using dataset-derived defaults.
        # Weather features come from OpenWeather.

        model_input = {

            "Soil_Type": soil_type,

            "Soil_pH": soil_ph,

            "Soil_Moisture": soil_moisture,

            "Organic_Carbon": organic_carbon,

            "Electrical_Conductivity": electrical_conductivity,

            "Temperature_C": weather["temperature"],

            "Humidity": weather["humidity"],

            "Rainfall_mm": weather["next_24h_rainfall"],

            "Sunlight_Hours": sunlight_hours,

            "Wind_Speed_kmh": weather["wind_speed"] * 3.6,

            "Crop_Type": crop_type,

            "Crop_Growth_Stage": crop_growth_stage,

            "Season": season,

            "Irrigation_Type": irrigation_type,

            "Water_Source": water_source,

            "Field_Area_hectare": field_area,

            "Mulching_Used": mulching,

            "Previous_Irrigation_mm": previous_irrigation,

            "Region": region
        }

        try:

            with st.spinner(
                tr(language, "running_model")
            ):

                prediction, _ = predict_irrigation(
                    model_input
                )


            # ------------------------------------------------
            # PREDICTION RESULT
            # ------------------------------------------------

            st.markdown(
                f"### {tr(language, 'prediction')}"
            )

            prediction_upper = prediction.upper()

            if prediction_upper == "HIGH":

                st.error(
                    f"## {tr(language, 'high')}"
                )

            elif prediction_upper == "MEDIUM":

                st.warning(
                    f"## {tr(language, 'medium')}"
                )

            else:

                st.success(
                    f"## {tr(language, 'low')}"
                )


            # ------------------------------------------------
            # LOCALIZED ADVISORY
            # ------------------------------------------------

            advisory = localized_advisory(
                language,
                prediction,
                weather["next_24h_rainfall"],
                weather["rain_probability"]
            )

            st.markdown(
                tr(language, "advisory")
            )

            st.info(advisory)


            # ------------------------------------------------
            # PARAMETERS USED FOR PREDICTION
            # ------------------------------------------------

            st.markdown(
                tr(language, "parameters")
            )

            summary_col1, summary_col2 = st.columns(2)

            with summary_col1:

                st.write(
                    f"**{tr(language, 'location_label')}:** "
                    f"{location}, Uttarakhand"
                )

                st.write(
                    f"**{tr(language, 'crop_label')}:** "
                    f"{display_crop(language, crop_type)}"
                )

                st.write(
                    f"**{tr(language, 'growth_label')}:** "
                    f"{display_stage(language, crop_growth_stage)}"
                )

                st.write(
                    f"**{tr(language, 'soil_moisture')}:** "
                    f"{soil_moisture:.2f}"
                )

            with summary_col2:

                st.write(
                    f"**{tr(language, 'temperature')}:** "
                    f"{weather['temperature']:.1f} °C"
                )

                st.write(
                    f"**{tr(language, 'humidity')}:** "
                    f"{weather['humidity']}%"
                )

                st.write(
                    f"**{tr(language, 'forecast')}:** "
                    f"{weather['next_24h_rainfall']:.1f} mm"
                )

                st.write(
                    f"**{tr(language, 'wind')}:** "
                    f"{weather['wind_speed'] * 3.6:.1f} km/h"
                )

        except Exception as error:

            st.error(
                tr(language, "prediction_error")
            )

            st.exception(error)


# ============================================================
# ML MODEL EXPLANATION
# ============================================================

st.markdown(
    tr(language, "model_basis")
)

with st.expander(
    tr(language, "view_basis")
):

    st.write(
        tr(language, "basis1")
    )

    st.write(
        tr(language, "basis2")
    )

    st.write(
        tr(language, "basis3")
    )


st.info(
    tr(language, "class_info")
)


# ============================================================
# MODEL INFORMATION
# ============================================================

st.markdown("---")

st.markdown(
    f'<div class="section-title">{tr(language, "model_info")}</div>',
    unsafe_allow_html=True
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        tr(language, "selected_model"),
        "XGBoost"
    )

with m2:
    st.metric(
        tr(language, "accuracy"),
        "99.65%"
    )

with m3:
    st.metric(
        tr(language, "f1"),
        "99.65%"
    )

with m4:
    st.metric(
        tr(language, "r2"),
        "98.89%"
    )

st.info(
    tr(language, "model_compare")
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"""
    <div class="footer">
        {tr(language, "footer")}
    </div>
    """,
    unsafe_allow_html=True
)
