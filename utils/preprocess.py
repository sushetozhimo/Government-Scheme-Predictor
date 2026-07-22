
import pandas as pd

# Maps model feature-column name -> HTML form field name.
FIELD_MAP = {
    "Age": "age",
    "Gender": "gender",
    "Income": "annual_income",
    "Farmer": "is_farmer",
    "Student": "is_student",
    "Disability": "has_disability",
    "BPL": "is_bpl",
    "Occupation": "occupation",
    "District": "district",
    "MaritalStatus": "marital_status",
    "GirlChild": "has_girl_child",
    "StreetVendor": "is_street_vendor",
    "Artisan": "is_artisan",
    "WomanSHG": "is_shg_member",
    "RuralHousehold": "is_rural",
    "SeniorCitizen": "senior_citizen",
}

NUMERIC_MODEL_COLUMNS = {"Age", "Income"}
YES_NO_FORM_FIELDS = {"senior_citizen"}
YES_NO_MODEL_COLUMNS = {"SeniorCitizen"}

# The label encoder key used for the target/label column (the predicted
# scheme name), as opposed to a feature-column encoder.
TARGET_KEY = "Scheme"


def _coerce_yes_no_value(raw_value) -> int:
    if isinstance(raw_value, bool):
        return int(raw_value)
    if raw_value is None:
        return 0
    if isinstance(raw_value, (int, float)):
        return int(raw_value != 0)

    text = str(raw_value).strip().lower()
    if text in {"yes", "y", "true", "1", "1.0"}:
        return 1
    if text in {"no", "n", "false", "0", "0.0", ""}:
        return 0
    return 0


def build_feature_frame(form_data: dict, label_encoders: dict, feature_columns: list) -> pd.DataFrame:
    """
    Convert request.form into a single-row DataFrame matching
    feature_columns, in the exact order/dtype the model expects.

    Raises ValueError with a clear message if a required field is missing
    or a categorical value was never seen during training.
    """
    row = {}

    for model_col in feature_columns:
        form_field = FIELD_MAP.get(model_col, model_col)

        if form_field not in form_data:
            raise ValueError(f"Missing required field: '{form_field}' (model column '{model_col}')")

        raw_value = form_data[form_field]

        if form_field in YES_NO_FORM_FIELDS or model_col in YES_NO_MODEL_COLUMNS:
            row[model_col] = _coerce_yes_no_value(raw_value)

        elif model_col in NUMERIC_MODEL_COLUMNS:
            try:
                row[model_col] = float(raw_value)
            except (TypeError, ValueError):
                raise ValueError(f"'{form_field}' must be a number, got: {raw_value!r}")

        elif model_col in label_encoders:
            encoder = label_encoders[model_col]
            value = str(raw_value)
            if value not in encoder.classes_:
                known = ", ".join(encoder.classes_)
                raise ValueError(
                    f"'{form_field}' value '{value}' was not seen during training. "
                    f"Known values: {known}"
                )
            row[model_col] = encoder.transform([value])[0]

        else:
            # No encoder for this column -- pass the raw value through.
            row[model_col] = raw_value

    # Build the DataFrame with columns in the exact trained order.
    return pd.DataFrame([row], columns=feature_columns)


def decode_prediction(prediction, label_encoders: dict):
    """Decode the model's raw prediction back into a human-readable scheme name."""
    if TARGET_KEY in label_encoders:
        return label_encoders[TARGET_KEY].inverse_transform([prediction])[0]
    return prediction


def rule_based_match(form_data: dict, schemes: list) -> dict:
    """
    Fallback used when scheme_model.pkl is not available. Does a simple
    transparent match against schemes.json's `criteria` field so the app
    still works end-to-end without a trained model.

    Each scheme in schemes.json may optionally include a "criteria" dict,
    e.g. {"is_farmer": "Yes"} meaning "eligible only if is_farmer == Yes".
    Schemes with no criteria are treated as universally eligible (lowest
    priority match).
    """
    best = None
    best_score = -1

    for scheme in schemes:
        criteria = scheme.get("criteria", {})
        if not criteria:
            score = 0
        else:
            matched = sum(
                1 for k, v in criteria.items()
                if str(form_data.get(k, "")).strip().lower() == str(v).strip().lower()
            )
            if matched < len(criteria):
                continue  # doesn't satisfy all stated criteria
            score = matched

        if score > best_score:
            best_score = score
            best = scheme

    return best or (schemes[0] if schemes else None)
