
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import numpy as np
import glob
import os
import re

def preprocess_for_training(df):
    """
    Preprocesses the raw race data for training and evaluation.
    Keeps essential columns for evaluation like 'key', '単勝'.
    """
    # Make a copy to avoid SettingWithCopyWarning
    df = df.copy()

    # --- Target Variable ---
    # Coerce non-numeric `着順` to NaN, then fill with 0 and convert to int
    df['着順_numeric'] = pd.to_numeric(df['着順'], errors='coerce').fillna(0).astype(int)
    df['is_first_place'] = (df['着順_numeric'] == 1).astype(int)

    # --- Feature Engineering & Data Cleaning ---
    # Extract horse weight
    df['馬体重'] = df['馬体重'].str.extract(r'(\d+)').astype(float)
    # Clean distance column
    df['距離'] = df['距離'].str.replace('m', '').astype(float)
    # Convert odds to numeric for calculation, coercing errors
    df['単勝'] = pd.to_numeric(df['単勝'], errors='coerce').fillna(0)

    # --- Feature Selection ---
    features = [
        '開催場', 'クラス', '枠番', '馬番', '性', '年齢', '斤量', '騎手',
        '馬体重', '芝ダート', '距離', '天候', '馬場'
    ] 
    
    # --- Imputation and Type Conversion for Features ---
    for col in features:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('missing').astype('category')
        else:
            # Impute with median for numerical features
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # Convert all categorical features to 'category' dtype for LightGBM
    categorical_features = [col for col in features if df[col].dtype.name == 'category' or df[col].dtype == 'object']
    for col in categorical_features:
        df[col] = df[col].astype('category')
        
    return df, features, categorical_features

def main():
    """
    Main function to load data, train model, and evaluate correctly by race.
    """
    # --- 1. Load Data ---
    path = 'database'
    all_files = glob.glob(os.path.join(path, "*.csv"))
    df = pd.concat((pd.read_csv(f, dtype={'key': str}) for f in all_files), ignore_index=True)

    # --- 2. Group-wise Split (by Race) ---
    race_keys = df['key'].unique()
    train_keys, test_keys = train_test_split(race_keys, test_size=0.2, random_state=42)

    train_df = df[df['key'].isin(train_keys)]
    test_df = df[df['key'].isin(test_keys)]

    # --- 3. Preprocess Data ---
    train_df, features, categorical_features = preprocess_for_training(train_df)
    test_df, _, _ = preprocess_for_training(test_df)

    # --- 4. Train Model ---
    X_train = train_df[features]
    y_train = train_df['is_first_place']

    # Calculate scale_pos_weight for handling class imbalance
    if y_train.value_counts().get(1, 0) > 0:
        scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]
    else:
        scale_pos_weight = 1

    print("Training LightGBM model on race-split data...")
    lgbm = lgb.LGBMClassifier(random_state=42, scale_pos_weight=scale_pos_weight)
    lgbm.fit(X_train, y_train, categorical_feature=categorical_features)

    # --- Save the trained model ---
    model_filename = 'race_predictor_model.txt'
    lgbm.booster_.save_model(model_filename)
    print(f"\nModel saved to {model_filename}")

    # --- 5. Evaluate Model (Race by Race) ---
    print("\nEvaluating model on unseen races...")
    X_test = test_df[features]
    
    # Predict probabilities for the positive class (1st place)
    win_probabilities = lgbm.predict_proba(X_test)[:, 1]
    
    # Add predictions back to the test dataframe
    results_df = test_df.copy()
    results_df['predicted_prob'] = win_probabilities

    # Group by race to find the predicted winner for each race
    test_races = results_df.groupby('key')

    # --- 5. Evaluate Model (Race by Race with Thresholds) ---
    print("\nEvaluating model on unseen races with various probability thresholds...")
    
    # Define a range of thresholds to test
    thresholds = np.arange(0.1, 1.0, 0.05) # From 0.1 to 0.95 with step 0.05
    
    evaluation_results = []

    for threshold in thresholds:
        current_correct_predictions = 0
        current_total_investment = 0
        current_total_return = 0
        current_num_bets = 0

        for key, race_df in test_races:
            # Find the horse with the highest predicted probability in the race
            predicted_winner_idx = race_df['predicted_prob'].idxmax()
            predicted_winner = race_df.loc[predicted_winner_idx]

            # Only consider betting if the predicted probability is above the current threshold
            if predicted_winner['predicted_prob'] >= threshold:
                current_num_bets += 1
                current_total_investment += 100 # Bet 100 yen

                # Check if the prediction was correct
                if predicted_winner['is_first_place'] == 1:
                    current_correct_predictions += 1
                    current_total_return += 100 * predicted_winner['単勝'] # Add winnings

        # Calculate metrics for the current threshold
        current_win_rate = (current_correct_predictions / current_num_bets) * 100 if current_num_bets > 0 else 0
        current_return_rate = (current_total_return / current_total_investment) * 100 if current_total_investment > 0 else 0

        evaluation_results.append({
            'Threshold': f"{threshold:.2f}",
            'Bets': current_num_bets,
            'Win Rate (%)': f"{current_win_rate:.2f}",
            'ROI (%)': f"{current_return_rate:.2f}"
        })

    # --- 6. Display Results ---
    print("\n--- Model Evaluation Results by Threshold ---")
    results_table = pd.DataFrame(evaluation_results)
    print(results_table.to_string(index=False))

    print("\nNote: 'Bets' indicates the number of races where the model's top pick exceeded the threshold.")
    print("A higher threshold means fewer bets but potentially higher ROI.")

if __name__ == '__main__':
    main()
