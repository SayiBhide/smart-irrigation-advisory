# ============================================================
# IRRIGATION PREDICTOR
# Smart Irrigation Advisory System
# Uses the already trained XGBoost model
# ============================================================

from pathlib import Path
import joblib
import pandas as pd


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "ML_Results" / "final_irrigation_model.pkl"
MAPPING_PATH = BASE_DIR / "ML_Results" / "target_mapping.pkl"


# ------------------------------------------------------------
# Load trained model
# ------------------------------------------------------------

def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found:\n{MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    return model


# ------------------------------------------------------------
# Load target mapping
# ------------------------------------------------------------

def load_target_mapping():

    if not MAPPING_PATH.exists():

        return {
            0: "Low",
            1: "Medium",
            2: "High"
        }

    mapping = joblib.load(MAPPING_PATH)

    # Handle either:
    # {"Low": 0, "Medium": 1, "High": 2}
    # OR
    # {0: "Low", 1: "Medium", 2: "High"}

    if all(isinstance(k, int) for k in mapping.keys()):
        return mapping

    return {value: key for key, value in mapping.items()}


# ------------------------------------------------------------
# Predict irrigation requirement
# ------------------------------------------------------------

def predict_irrigation(input_data):

    model = load_model()
    target_mapping = load_target_mapping()

    input_df = pd.DataFrame([input_data])

    prediction = model.predict(input_df)[0]

    # Convert numerical prediction into label
    try:
        prediction_int = int(prediction)
        predicted_class = target_mapping.get(
            prediction_int,
            str(prediction)
        )
    except Exception:
        predicted_class = str(prediction)

    # Probability / confidence
    probabilities = {}

    if hasattr(model, "predict_proba"):

        probability_values = model.predict_proba(input_df)[0]

        if hasattr(model, "classes_"):

            classes = model.classes_

            for class_value, probability in zip(
                classes,
                probability_values
            ):

                try:
                    class_name = target_mapping.get(
                        int(class_value),
                        str(class_value)
                    )
                except Exception:
                    class_name = str(class_value)

                probabilities[class_name] = round(
                    float(probability) * 100,
                    2
                )

    return predicted_class, probabilities


# ------------------------------------------------------------
# Generate advisory
# ------------------------------------------------------------

def generate_advisory(
    prediction,
    rainfall_forecast,
    rain_probability
):

    prediction = prediction.lower()

    if prediction == "low":

        message = (
            "Low irrigation requirement. "
            "Immediate irrigation may not be necessary. "
            "Continue monitoring soil moisture and weather conditions."
        )

    elif prediction == "medium":

        message = (
            "Moderate irrigation requirement. "
            "Plan irrigation based on soil moisture and crop growth stage."
        )

    elif prediction == "high":

        message = (
            "High irrigation requirement. "
            "Irrigation should be considered soon while monitoring "
            "soil and weather conditions."
        )

    else:

        message = (
            "Irrigation requirement could not be classified."
        )

    # Weather-aware advisory
    if rainfall_forecast >= 5 or rain_probability >= 60:

        message += (
            " Rainfall is expected in the next 24 hours, "
            "so irrigation should be reassessed before application."
        )

    return message