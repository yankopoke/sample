import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
import glob
import os
import re

def preprocess_data(df):
    """
    Preprocesses the raw race data.
    """
    # Coerce non-numeric `着順` to NaN, then fill with 0 and convert to int
    df['着順'] = pd.to_numeric(df['着順'], errors='coerce').fillna(0).astype(int)
    # Target variable: 1 if finish order is 1, else 0
    df['is_first_place'] = (df['着順'] == 1).astype(int)

    # Feature Engineering
    # Extract horse weight from "weight(change)" format
    df['馬体重'] = df['馬体重'].str.extract(r'(\d+)').astype(float)

    # Clean distance column by removing 'm'
    df['距離'] = df['距離'].str.replace('m', '').astype(float)

    # Select features to use
    features = [
        '開催場', 'クラス', '枠番', '馬番', '性', '年齢', '斤量', '騎手',
        '馬体重', '芝ダート', '距離', '天候', '馬場'
    ]
    
    # Add target variable to the list of columns to keep
    all_cols = features + ['is_first_place']
    df = df[all_cols]

    # Handle missing values (simple imputation)
    for col in features:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('missing')
        else:
            df[col] = df[col].fillna(df[col].median())

    # Convert categorical features for LightGBM
    categorical_features = ['開催場', 'クラス', '性', '騎手', '芝ダート', '天候', '馬場']
    for col in categorical_features:
        df[col] = df[col].astype('category')

    return df, features

def main():
    """
    Main function to load data, train model, and evaluate.
    """
    # Load data
    path = 'database'
    all_files = glob.glob(os.path.join(path, "*.csv"))
    df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)

    # Preprocess data
    df, features = preprocess_data(df)

    # Split data
    X = df[features]
    y = df['is_first_place']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Calculate scale_pos_weight for handling class imbalance
    scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]

    # Train model
    print("Training LightGBM model with scale_pos_weight...")
    lgbm = lgb.LGBMClassifier(random_state=42, scale_pos_weight=scale_pos_weight)
    lgbm.fit(X_train, y_train, categorical_feature=[col for col in features if df[col].dtype.name == 'category'])

    # Evaluate model
    print("\nModel Evaluation:")
    y_pred = lgbm.predict(X_test)
    
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred):.4f}")
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Feature Importance
    print("\nFeature Importances:")
    feature_imp = pd.DataFrame(sorted(zip(lgbm.feature_importances_, features)), columns=['Value','Feature'])
    print(feature_imp.sort_values(by="Value", ascending=False))

if __name__ == '__main__':
    main()
