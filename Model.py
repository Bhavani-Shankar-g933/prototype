import pandas as pd
import joblib

model_path = r"C:\Users\bhava\OneDrive\Desktop\prototype\Models\Model objects\churn_xgb_model.pkl"
encoder_path = r"C:\Users\bhava\OneDrive\Desktop\prototype\Models\Model objects\label_encoder.pkl"

# Load once
churn_model = joblib.load(model_path)
label_encoders = joblib.load(encoder_path)


def predict_churn(input_df: pd.DataFrame):
    """
    Predict churn for a DataFrame of input data.
    """
    df = input_df.copy()

    # Drop Churn column if present (for test data)
    if 'Churn' in df.columns:
        df = df.drop('Churn', axis=1)

    # Encode categorical columns
    for col in df.select_dtypes(include="object").columns:
        if col in label_encoders:
            df[col] = label_encoders[col].transform(df[col])

    # Predict
    prediction = churn_model.predict(df)

    # Add prediction to DataFrame
    input_df = input_df.copy()
    input_df['Churn'] = prediction

    return input_df
