import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, r2_score
from catboost import CatBoostRegressor
import joblib
import argparse
import os
import matplotlib.pyplot as plt

def calculate_evoo_compliance(predictions_df):
    """
    Deterministic post-processing step to calculate isEvooCompliant 
    based on regulatory IOC physical constraints, as detailed in the methodology.
    """
    # Assuming predictions_df has exactly the columns named below
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
    parser = argparse.ArgumentParser(description="Train CatBoost Multi-Output Regression Pipeline")
    parser.add_argument('--data', type=str, default='dataset.csv', help='Path to the synthetic CSV dataset')
    parser.add_argument('--model-out', type=str, default='catboost_pipeline.pkl', help='Path to save output model')
    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: Dataset {args.data} not found. Please generate it first.")
        return

    print(f"Loading dataset from {args.data}...")
    df = pd.read_csv(args.data)

    # Input Features
    features = [
        'maturationIndex', 'moistureContent', 'oilContent', 'defectIndex', 
        'cultivar', 'malaxationTemperature', 'malaxationTime', 
        'waterFlowRate', 'waterToPasteRatio'
    ]
    
    # Continuous Targets for Regression
    targets = [
        'yieldPercentage', 'totalPhenols', 'freeAcidity', 'peroxideValue', 
        'k232', 'k270', 'deltaK', 'fruity', 'bitter', 'pungent'
    ]

    # Use .copy() to avoid SettingWithCopyWarning
    X = df[features].copy()
    Y = df[targets].copy()

    # CatBoost explicitly requires categorical columns to be cast to string type
    X['cultivar'] = X['cultivar'].astype(str)

    # Get the integer index of the categorical feature for CatBoost initialization
    cat_features_indices = [X.columns.get_loc('cultivar')]

    print("Splitting dataset into training (80%) and testing (20%) sets...")
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    print("Initializing CatBoost Multi-Output Regressor...")
    # Initialize the base CatBoost model with optimal default settings for tabular regression
    base_cb = CatBoostRegressor(
        iterations=500,
        learning_rate=0.05,
        depth=6,
        cat_features=cat_features_indices,
        verbose=0,
        random_seed=42
    )

    # Wrap the base model in MultiOutputRegressor to fit one regressor per target
    # This aligns perfectly with the methodology: 'one regressor per target or coordinated workflow'
    model = MultiOutputRegressor(base_cb)

    print("Training pipeline... (this might take a few moments depending on dataset size)")
    model.fit(X_train, Y_train)

    print("\n--- Model Evaluation (Test Set) ---")
    Y_pred = model.predict(X_test)
    Y_pred_df = pd.DataFrame(Y_pred, columns=targets)

    # Evaluate continuous metrics
    r2_scores = []
    
    out_dir = os.path.dirname(args.model_out) or '.'
    os.makedirs(out_dir, exist_ok=True)

    for i, target in enumerate(targets):
        actual = Y_test.iloc[:, i]
        pred = Y_pred_df.iloc[:, i]
        
        r2 = r2_score(actual, pred)
        rmse = np.sqrt(mean_squared_error(actual, pred))
        r2_scores.append(r2)
        
        print(f"Target: {target:<18} R2: {r2:.4f} | RMSE: {rmse:.4f}")
        
        # Create an individual scatter plot for this target
        plt.figure(figsize=(6, 5))
        plt.scatter(actual, pred, alpha=0.5, color='dodgerblue', edgecolor='k')
        
        # Perfect prediction line
        min_val = min(actual.min(), pred.min())
        max_val = max(actual.max(), pred.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        
        plt.title(f'{target} ($R^2$={r2:.2f})')
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        
        plt.tight_layout()
        plot_path = os.path.join(out_dir, f'actual_vs_predicted_{target}.png')
        plt.savefig(plot_path, dpi=300)
        plt.close()

    print("\nSaved individual 'Actual vs Predicted' plots for all targets.")
    
    # R2 Scores Bar Chart
    plt.figure(figsize=(10, 6))
    plt.bar(targets, r2_scores, color='seagreen', edgecolor='k')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('$R^2$ Score')
    plt.title('Model Performance ($R^2$) across all Targets')
    plt.ylim(0, 1.05)
    plt.tight_layout()
    
    r2_plot_path = os.path.join(out_dir, 'r2_scores.png')
    plt.savefig(r2_plot_path, dpi=300)
    plt.close()
    print(f"Saved 'R2 Scores' bar chart to {r2_plot_path}")

    print("\n--- Deterministic EVOO Compliance Evaluation ---")
    # Execute the post-processing as described in the documentation
    pred_evoo = calculate_evoo_compliance(Y_pred_df)
    
    # Extract actual EVOO status from the original ground truth dataset for the test indices
    actual_evoo = df.loc[Y_test.index, 'isEvooCompliant'].values
    
    match_accuracy = np.mean(pred_evoo.values == actual_evoo)
    print(f"EVOO Predictive Accuracy (Post-Processing vs Ground Truth): {match_accuracy * 100:.2f}%")

    print(f"\nSaving certified model pipeline to {args.model_out}...")
    out_dir = os.path.dirname(args.model_out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    joblib.dump(model, args.model_out)
    print("Training Setup Complete. Pipeline is ready for Digital Twin integration.")

if __name__ == "__main__":
    main()
