import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import argparse
import os
import matplotlib.pyplot as plt

def calculate_evoo_compliance(predictions_df):
    is_compliant = (
        (predictions_df['freeAcidity'] <= 0.8) &
        (predictions_df['peroxideValue'] <= 20.0) &
        (predictions_df['k232'] <= 2.50) &
        (predictions_df['k270'] <= 0.22) &
        (predictions_df['deltaK'] <= 0.01) &
        (predictions_df['fruity'] > 0.0)
    )
    return is_compliant

def main():
    parser = argparse.ArgumentParser(description="Train XGBoost Multi-Output Regression Pipeline")
    parser.add_argument('--data', type=str, default='dataset.csv', help='Path to the synthetic CSV dataset')
    parser.add_argument('--model-out', type=str, default='xgb_pipeline.pkl', help='Path to save output model')
    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: Dataset {args.data} not found. Please generate it first.")
        return

    print(f"Loading dataset from {args.data}...")
    df = pd.read_csv(args.data)

    features = [
        'maturationIndex', 'moistureContent', 'oilContent', 'defectIndex', 
        'cultivar', 'malaxationTemperature', 'malaxationTime', 
        'waterFlowRate', 'waterToPasteRatio'
    ]
    
    targets = [
        'yieldPercentage', 'totalPhenols', 'freeAcidity', 'peroxideValue', 
        'k232', 'k270', 'deltaK', 'fruity', 'bitter', 'pungent'
    ]

    X = df[features].copy()
    Y = df[targets].copy()

    # Convert object to category for XGBoost categorical feature support
    X['cultivar'] = X['cultivar'].astype('category')

    print("Splitting dataset into training (80%) and testing (20%) sets...")
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    print("Initializing XGBoost Multi-Output Regressor...")
    base_xgb = XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        tree_method="hist",
        enable_categorical=True,
        random_state=42
    )

    model = MultiOutputRegressor(base_xgb)

    print("Training pipeline...")
    model.fit(X_train, Y_train)

    print("\n--- Model Evaluation (Test Set) ---")
    Y_pred = model.predict(X_test)
    Y_pred_df = pd.DataFrame(Y_pred, columns=targets)

    r2_scores = []
    
    for i, target in enumerate(targets):
        actual = Y_test.iloc[:, i]
        pred = Y_pred_df.iloc[:, i]
        
        r2 = r2_score(actual, pred)
        rmse = np.sqrt(mean_squared_error(actual, pred))
        r2_scores.append(r2)
        
        print(f"Target: {target:<18} R2: {r2:.4f} | RMSE: {rmse:.4f}")

    pred_evoo = calculate_evoo_compliance(Y_pred_df)
    actual_evoo = df.loc[Y_test.index, 'isEvooCompliant'].values
    
    match_accuracy = np.mean(pred_evoo.values == actual_evoo)
    print(f"\nEVOO Predictive Accuracy (Post-Processing vs Ground Truth): {match_accuracy * 100:.2f}%")
    print(f"Average R2 Score: {np.mean(r2_scores):.4f}")

    out_dir = os.path.dirname(args.model_out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    joblib.dump(model, args.model_out)
    print(f"Saved pipeline to {args.model_out}")

if __name__ == "__main__":
    main()
