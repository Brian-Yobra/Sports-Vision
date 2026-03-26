import os
import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from core.db import get_db_connection

def train_prediction_model():
    """
    Train a logistic regression model to predict match outcomes.
    
    Features used:
    - possession: Ball possession percentage
    - shots: Number of shots taken
    - shots_on_target: Shots on target
    - corners: Number of corners
    - home_advantage: 1 if home, 0 if away
    
    Target: result (Win=2, Draw=1, Loss=0)
    """
    conn = get_db_connection()
    matches = conn.execute('''
        SELECT possession, shots, shots_on_target, corners, 
               CASE venue WHEN 'Home' THEN 1 ELSE 0 END as home_advantage,
               CASE result 
                   WHEN 'Win' THEN 2 
                   WHEN 'Draw' THEN 1 
                   ELSE 0 
                END as outcome
        FROM matches
    ''').fetchall()
    conn.close()
    
    if len(matches) < 10:
        return None, "Not enough data to train model (need at least 10 matches)"
    
    # Convert to DataFrame
    df = pd.DataFrame(matches)
    
    # Features and target
    X = df[['possession', 'shots', 'shots_on_target', 'corners', 'home_advantage']]
    y = df['outcome']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_scaled, y)
    
    # Calculate accuracy
    accuracy = model.score(X_scaled, y) * 100
    
    # Save model and scaler
    with open('data/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('data/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    return model, f"Model trained successfully! Accuracy: {accuracy:.2f}%"

def predict_match_outcome(possession, shots, shots_on_target, corners, is_home=True):
    """
    Predict match outcome using trained logistic regression model.
    
    Returns:
        dict with prediction, probabilities, and confidence
    """
    try:
        # Load model and scaler
        with open('data/model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('data/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
    except FileNotFoundError:
        return None
    
    # Prepare input
    home_advantage = 1 if is_home else 0
    input_data = np.array([[possession, shots, shots_on_target, corners, home_advantage]])
    input_scaled = scaler.transform(input_data)
    
    # Predict
    prediction = model.predict(input_scaled)[0]
    probabilities = model.predict_proba(input_scaled)[0]
    
    outcome_map = {0: 'Loss', 1: 'Draw', 2: 'Win'}
    outcome = outcome_map[prediction]
    confidence = round(probabilities[prediction] * 100, 2)
    
    return {
        'prediction': outcome,
        'confidence': confidence,
        'probabilities': {
            'Loss': round(probabilities[0] * 100, 2),
            'Draw': round(probabilities[1] * 100, 2),
            'Win': round(probabilities[2] * 100, 2)
        }
    }
