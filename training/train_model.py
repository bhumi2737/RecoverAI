import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, precision_score, recall_score, f1_score
import json

def train_and_evaluate():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "payment_recovery_data.csv")
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}. Run generate_synthetic_data.py first.")
        return

    df = pd.read_csv(data_path)
    
    # Define features and target
    target = 'recovered'
    categorical_features = ['failure_reason', 'payment_method']
    numerical_features = [
        'transaction_amount', 
        'successful_payments', 
        'failed_payments', 
        'total_customer_spend', 
        'average_order_value', 
        'previous_recovery_attempts', 
        'previous_recovery_success', 
        'days_since_last_purchase', 
        'customer_tenure_days'
    ]

    X = df[categorical_features + numerical_features]
    y = df[target]

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    # Baseline: Logistic Regression
    lr_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                  ('classifier', LogisticRegression(random_state=42, max_iter=1000))])
    
    lr_pipeline.fit(X_train, y_train)
    lr_preds = lr_pipeline.predict(X_test)
    lr_probs = lr_pipeline.predict_proba(X_test)[:, 1]
    
    lr_precision = precision_score(y_test, lr_preds)
    lr_recall = recall_score(y_test, lr_preds)
    lr_f1 = f1_score(y_test, lr_preds)
    lr_roc_auc = roc_auc_score(y_test, lr_probs)

    print("--- Logistic Regression Baseline ---")
    print(classification_report(y_test, lr_preds))
    print(f"ROC-AUC: {lr_roc_auc:.4f}\n")

    # Primary Model: Random Forest
    rf_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                  ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))])
    
    rf_pipeline.fit(X_train, y_train)
    rf_preds = rf_pipeline.predict(X_test)
    rf_probs = rf_pipeline.predict_proba(X_test)[:, 1]

    rf_precision = precision_score(y_test, rf_preds)
    rf_recall = recall_score(y_test, rf_preds)
    rf_f1 = f1_score(y_test, rf_preds)
    rf_roc_auc = roc_auc_score(y_test, rf_probs)

    print("--- Random Forest Primary Model ---")
    print(classification_report(y_test, rf_preds))
    print(f"ROC-AUC: {rf_roc_auc:.4f}\n")
    
    # Model Selection
    if rf_f1 >= lr_f1:
        best_model = rf_pipeline
        best_model_name = "Random Forest"
        best_metrics = {
            "model": best_model_name,
            "precision": rf_precision,
            "recall": rf_recall,
            "f1_score": rf_f1,
            "roc_auc": rf_roc_auc
        }
        # Feature Importance for RF
        rf_model = rf_pipeline.named_steps['classifier']
        cat_encoder = rf_pipeline.named_steps['preprocessor'].named_transformers_['cat']
        cat_feature_names = list(cat_encoder.get_feature_names_out(categorical_features))
        feature_names = numerical_features + cat_feature_names
        
        importances = rf_model.feature_importances_
        feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
        feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
        
        print(f"--- Top 5 Features ({best_model_name}) ---")
        print(feature_importance_df.head(5))
        best_metrics["top_features"] = feature_importance_df.head(10).to_dict('records')
    else:
        best_model = lr_pipeline
        best_model_name = "Logistic Regression"
        best_metrics = {
            "model": best_model_name,
            "precision": lr_precision,
            "recall": lr_recall,
            "f1_score": lr_f1,
            "roc_auc": lr_roc_auc
        }
        # Coefficients for LR
        lr_model = lr_pipeline.named_steps['classifier']
        cat_encoder = lr_pipeline.named_steps['preprocessor'].named_transformers_['cat']
        cat_feature_names = list(cat_encoder.get_feature_names_out(categorical_features))
        feature_names = numerical_features + cat_feature_names
        
        coeffs = lr_model.coef_[0]
        feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Coefficient': coeffs})
        feature_importance_df['Abs_Coefficient'] = feature_importance_df['Coefficient'].abs()
        feature_importance_df = feature_importance_df.sort_values(by='Abs_Coefficient', ascending=False)
        
        print(f"--- Top 5 Features ({best_model_name}) ---")
        print(feature_importance_df[['Feature', 'Coefficient']].head(5))
        best_metrics["top_features"] = feature_importance_df.head(10).to_dict('records')

    print(f"\nSelected Best Model: {best_model_name} (F1: {best_metrics['f1_score']:.4f})")

    # Save Model
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    model_path = os.path.join(model_dir, "recovery_model.pkl")
    
    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)
        
    print(f"\nModel saved to {model_path}")
    
    # Save Metrics
    metrics_path = os.path.join(model_dir, "model_metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(best_metrics, f, indent=4)
        
    print(f"Metrics saved to {metrics_path}")

if __name__ == "__main__":
    train_and_evaluate()
