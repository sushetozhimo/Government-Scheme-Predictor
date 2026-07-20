import json
import os

import joblib
from flask import Flask, render_template, request

from utils.preprocess import build_feature_frame, decode_prediction, rule_based_match

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "scheme_model.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "label_encoders.pkl")
FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR, "feature_columns.pkl")
SCHEMES_PATH = os.path.join(BASE_DIR, "schemes.json")

# ---------------------------------------------------------------------------
# Load artifacts once at startup.
#
# IMPORTANT: none of this touches the 500MB training CSV. Only the small
# .pkl files produced by your training script are needed here. If they are
# missing/corrupt the app still runs, falling back to a transparent
# rule-based match against schemes.json.
# ---------------------------------------------------------------------------
model = None
label_encoders = {}
feature_columns = []
model_load_error = None

try:
    model = joblib.load(MODEL_PATH)
    label_encoders = joblib.load(ENCODERS_PATH)
    feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
except Exception as exc:  # noqa: BLE001 - we want to degrade gracefully, not crash
    model_load_error = str(exc)
    print(f"[warning] Could not load model artifacts, using rule-based fallback: {exc}")

try:
    with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
        SCHEMES = json.load(f)
except Exception as exc:  # noqa: BLE001
    print(f"[warning] Could not load schemes.json: {exc}")
    SCHEMES = []

SCHEMES_BY_NAME = {s["name"]: s for s in SCHEMES if "name" in s}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/predict", methods=["POST"])
def predict():
    form_data = request.form.to_dict()
    full_name = form_data.get("full_name", "Citizen")

    used_model = False
    confidence = 0
    predicted_name = None

    if model is not None and feature_columns:
        try:
            features = build_feature_frame(form_data, label_encoders, feature_columns)
            prediction = model.predict(features)[0]
            predicted_name = decode_prediction(prediction, label_encoders)

            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(features)[0]
                confidence = round(max(proba) * 100, 1)
            else:
                confidence = 100.0

            used_model = True
        except ValueError as exc:
            # Bad/unseen input value -- fall back to rule-based rather
            # than showing the user a stack trace.
            print(f"[warning] Model prediction failed, using fallback: {exc}")
        except Exception as exc:  # noqa: BLE001
            print(f"[error] Unexpected error during prediction: {exc}")

    if not used_model:
        match = rule_based_match(form_data, SCHEMES)
        predicted_name = match["name"] if match else None
        confidence = 60.0 if match else 0

    scheme = SCHEMES_BY_NAME.get(predicted_name) or {
        "name": predicted_name or "No matching scheme found",
        "category": "General",
        "description": (
            "We couldn't find a specific scheme for this profile. "
            "Please check the official government schemes portal for the "
            "full list of available schemes."
        ),
        "link": None,
    }

    return render_template(
        "result.html",
        full_name=full_name,
        scheme=scheme,
        confidence=confidence,
        used_model=used_model,
    )


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
