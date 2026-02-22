
import pandas as pd
import lightgbm as lgb
import sys
import os
import re

def preprocess_for_prediction(df):
    """
    Preprocesses new race data for prediction.
    This must be consistent with the training preprocessing,
    but handles data without target variables ('着順', '単勝').
    """
    df = df.copy()

    # --- Feature Engineering ---
    # Extract horse weight
    df['馬体重'] = df['馬体重'].str.extract(r'(\d+)').astype(float)
    # Clean distance column
    df['距離'] = df['距離'].str.replace('m', '').astype(float)

    # --- Feature Selection ---
    features = [
        '開催場', 'クラス', '枠番', '馬番', '性', '年齢', '斤量', '騎手',
        '馬体重', '芝ダート', '距離', '天候', '馬場'
    ] 
    
    # Check if all required feature columns exist
    for col in features:
        if col not in df.columns:
            raise ValueError(f"Error: Input CSV is missing required column '{col}'")

    # --- Imputation and Type Conversion for Features ---
    for col in features:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('missing').astype('category')
        else:
            # Impute with a reasonable default (e.g., 0 or median) if needed
            # For prediction, it's better to ensure data is complete, but we'll handle NaNs.
            if df[col].isnull().any():
                # Using 0 for simplicity, but a trained imputer or median from training set would be more robust
                df[col] = df[col].fillna(0)

    # Convert all categorical features to 'category' dtype
    categorical_features = [col for col in features if df[col].dtype.name == 'category' or df[col].dtype == 'object']
    for col in categorical_features:
        df[col] = df[col].astype('category')
        
    return df[features]

def main():
    """
    Main function to load a trained model and predict on a new race.
    """
    # --- 1. Load Model and Input Data ---
    model_filename = 'race_predictor_model.txt'
    if not os.path.exists(model_filename):
        print(f"Error: Model file not found at '{model_filename}'")
        print("Please run 'python train_model_v2.py' first to train and save the model.")
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python predict.py <path_to_race_csv>")
        sys.exit(1)
        
    race_csv_path = sys.argv[1]
    if not os.path.exists(race_csv_path):
        print(f"Error: Input CSV file not found at '{race_csv_path}'")
        sys.exit(1)

    # Load the trained model
    try:
        bst = lgb.Booster(model_file=model_filename)
    except lgb.basic.LightGBMError as e:
        print(f"Error loading model: {e}")
        print("The model file might be corrupted or incompatible.")
        sys.exit(1)

    # Load race data
    race_df = pd.read_csv(race_csv_path)
    
    # Keep original info for final display
    original_info = race_df[['馬番', '馬名']].copy()

    # --- 2. Preprocess Data ---
    print(f"Preprocessing data from '{race_csv_path}'...")
    try:
        X_pred = preprocess_for_prediction(race_df)
    except ValueError as e:
        print(e)
        sys.exit(1)

    # --- 3. Predict Probabilities ---
    print("Predicting win probabilities...")
    # For a loaded Booster, .predict() returns the probability of the positive class
    win_probabilities = bst.predict(X_pred)

    # --- 4. Display Results ---
    original_info['Win Probability'] = win_probabilities
    
    # Sort by probability in descending order
    sorted_results = original_info.sort_values(by='Win Probability', ascending=False).reset_index(drop=True)
    
    # Format probability as percentage
    sorted_results['Win Probability'] = sorted_results['Win Probability'].apply(lambda x: f"{x*100:.2f}%")

    print("\n--- Prediction Results ---")
    print(sorted_results.to_string())

if __name__ == '__main__':
    main()
