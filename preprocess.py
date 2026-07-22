

import pandas as pd

from utils.preprocess import CATEGORICAL_MAPS, YES_NO_FIELDS, FEATURE_COLUMNS


def build_training_frame(df: pd.DataFrame, label_column: str = "scheme"):

    df = df.copy()

    for col, mapping in CATEGORICAL_MAPS.items():
        df[col] = df[col].map(mapping)

    for field in YES_NO_FIELDS:
        df[field] = df[field].apply(
            lambda v: 1 if str(v).strip().lower() == "yes" else 0
        )

    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {missing}")

    X = df[FEATURE_COLUMNS]
    y = df[label_column] if label_column in df.columns else None
    return X, y


if __name__ == "__main__":
    print(
        "This script is a helper module for training scheme_model.pkl.\n"
        "Import build_training_frame() from your own training script; "
        "see the module docstring for an example."
    )
