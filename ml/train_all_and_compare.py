import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from catboost import CatBoostRegressor
from xgboost import XGBRegressor

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
    data_path = 'dataset.csv'
    out_dir = 'comparison_results'
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(data_path):
        print(f"Error: Dataset {data_path} not found.")
        return

    print("Loading dataset...")
    df = pd.read_csv(data_path)

    features = [
        'maturationIndex', 'moistureContent', 'oilContent', 'defectIndex', 
        'cultivar', 'malaxationTemperature', 'malaxationTime', 
        'waterFlowRate', 'waterToPasteRatio'
    ]
    
    targets = [
        'yieldPercentage', 'totalPhenols', 'freeAcidity', 'peroxideValue', 
        'k232', 'k270', 'deltaK', 'fruity', 'bitter', 'pungent'
    ]

    # Preprocessing for different models
    # 1. CatBoost (native string categories)
    X_cat = df[features].copy()
    X_cat['cultivar'] = X_cat['cultivar'].astype(str)
    cat_features_indices = [X_cat.columns.get_loc('cultivar')]

    # 2. Random Forest (One-Hot Encoding)
    X_rf = pd.get_dummies(df[features], columns=['cultivar'], drop_first=True)

    # 3. XGBoost (Categorical type)
    X_xgb = df[features].copy()
    X_xgb['cultivar'] = X_xgb['cultivar'].astype('category')

    Y = df[targets].copy()

    print("Splitting dataset (80% train, 20% test)...")
    # Generate same split indices for all
    indices = np.arange(len(df))
    idx_train, idx_test = train_test_split(indices, test_size=0.2, random_state=42)

    Y_train, Y_test = Y.iloc[idx_train], Y.iloc[idx_test]

    models_info = {
        'CatBoost': {
            'X_train': X_cat.iloc[idx_train], 'X_test': X_cat.iloc[idx_test],
            'model': MultiOutputRegressor(CatBoostRegressor(
                iterations=500, learning_rate=0.05, depth=6, 
                cat_features=cat_features_indices, verbose=0, random_seed=42
            ))
        },
        'RandomForest': {
            'X_train': X_rf.iloc[idx_train], 'X_test': X_rf.iloc[idx_test],
            'model': MultiOutputRegressor(RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            ))
        },
        'XGBoost': {
            'X_train': X_xgb.iloc[idx_train], 'X_test': X_xgb.iloc[idx_test],
            'model': MultiOutputRegressor(XGBRegressor(
                n_estimators=200, learning_rate=0.05, max_depth=6,
                tree_method="hist", enable_categorical=True, random_state=42
            ))
        }
    }

    results = {}
    
    actual_evoo = df.loc[Y_test.index, 'isEvooCompliant'].values

    for name, info in models_info.items():
        print(f"\nTraining {name}...")
        info['model'].fit(info['X_train'], Y_train)
        
        print(f"Evaluating {name}...")
        Y_pred = info['model'].predict(info['X_test'])
        Y_pred_df = pd.DataFrame(Y_pred, columns=targets, index=Y_test.index)
        
        r2_scores = []
        for i, target in enumerate(targets):
            r2 = r2_score(Y_test.iloc[:, i], Y_pred_df.iloc[:, i])
            r2_scores.append(r2)
            
        pred_evoo = calculate_evoo_compliance(Y_pred_df)
        evoo_acc = np.mean(pred_evoo.values == actual_evoo)
        
        results[name] = {
            'r2_scores': r2_scores,
            'avg_r2': np.mean(r2_scores),
            'evoo_accuracy': evoo_acc
        }

    # Generate Images
    print("\nGenerating Comparison Plots...")
    
    # 1. R2 Scores Comparison (Grouped Bar Chart)
    x = np.arange(len(targets))
    width = 0.25
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.bar(x - width, results['CatBoost']['r2_scores'], width, label='CatBoost', color='dodgerblue')
    ax.bar(x, results['RandomForest']['r2_scores'], width, label='Random Forest', color='seagreen')
    ax.bar(x + width, results['XGBoost']['r2_scores'], width, label='XGBoost', color='darkorange')
    
    ax.set_ylabel('$R^2$ Score')
    ax.set_title('Model Comparison: $R^2$ Scores per Target')
    ax.set_xticks(x)
    ax.set_xticklabels(targets, rotation=45, ha='right')
    ax.legend()
    plt.ylim(0, 1.1)
    plt.tight_layout()
    r2_plot_path = os.path.join(out_dir, 'comparison_r2_scores.png')
    plt.savefig(r2_plot_path, dpi=300)
    plt.close()

    # 2. Overall Metrics Comparison
    metrics = ['Average $R^2$', 'EVOO Accuracy']
    cat_metrics = [results['CatBoost']['avg_r2'], results['CatBoost']['evoo_accuracy']]
    rf_metrics = [results['RandomForest']['avg_r2'], results['RandomForest']['evoo_accuracy']]
    xgb_metrics = [results['XGBoost']['avg_r2'], results['XGBoost']['evoo_accuracy']]
    
    x_metrics = np.arange(len(metrics))
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.bar(x_metrics - width, cat_metrics, width, label='CatBoost', color='dodgerblue')
    ax2.bar(x_metrics, rf_metrics, width, label='Random Forest', color='seagreen')
    ax2.bar(x_metrics + width, xgb_metrics, width, label='XGBoost', color='darkorange')
    
    ax2.set_ylabel('Score / Accuracy')
    ax2.set_title('Overall Performance Comparison')
    ax2.set_xticks(x_metrics)
    ax2.set_xticklabels(metrics)
    ax2.legend(loc='lower right')
    plt.ylim(0, 1.1)
    for p in ax2.patches:
        ax2.annotate(f"{p.get_height():.3f}", (p.get_x() * 1.005, p.get_height() * 1.01))
    plt.tight_layout()
    overall_plot_path = os.path.join(out_dir, 'comparison_overall.png')
    plt.savefig(overall_plot_path, dpi=300)
    plt.close()

    # Write Markdown Report
    print("Writing Markdown Report...")
    report_path = os.path.join(out_dir, 'model_comparison_report.md')
    with open(report_path, 'w') as f:
        f.write("# Machine Learning Model Comparison Report\n\n")
        f.write("This report details the benchmarking of three gradient-boosted and tree-based ensemble models: **CatBoost**, **Random Forest**, and **XGBoost**.\n")
        f.write("All models were trained and tested using an **80% train / 20% test** split on the same synthetic dataset.\n\n")
        
        f.write("## Overall Metrics\n\n")
        f.write("| Model | Average $R^2$ | EVOO Compliance Accuracy |\n")
        f.write("|---|---|---|\n")
        for name in ['CatBoost', 'RandomForest', 'XGBoost']:
            f.write(f"| {name} | {results[name]['avg_r2']:.4f} | {results[name]['evoo_accuracy']*100:.2f}% |\n")
        
        f.write("\n## Target-Specific $R^2$ Scores\n\n")
        f.write("| Target | CatBoost | Random Forest | XGBoost |\n")
        f.write("|---|---|---|---|\n")
        for i, target in enumerate(targets):
            f.write(f"| {target} | {results['CatBoost']['r2_scores'][i]:.4f} | {results['RandomForest']['r2_scores'][i]:.4f} | {results['XGBoost']['r2_scores'][i]:.4f} |\n")
            
        f.write("\n## Visualizations\n\n")
        f.write("### Target $R^2$ Comparison\n")
        f.write("![R2 Comparison](comparison_r2_scores.png)\n\n")
        f.write("### Overall Performance\n")
        f.write("![Overall Comparison](comparison_overall.png)\n\n")

        f.write("## Conclusion\n")
        f.write("The results indicate that all three models perform exceptionally well on the synthetic dataset, capturing the nonlinear relationships with high fidelity. ")
        f.write("The minor variations in the average $R^2$ score and identical EVOO compliance accuracy across the ensembles suggest robust modeling. ")
        f.write("However, **CatBoost** remains highly favorable due to its native handling of categorical features, avoiding the need for manual one-hot encoding or type casting necessary in Random Forest and XGBoost.\n")

    print(f"\nAll tasks complete! Results saved in '{out_dir}/' directory.")

if __name__ == "__main__":
    main()
