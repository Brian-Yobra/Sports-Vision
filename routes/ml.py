import os
from flask import Blueprint, render_template, request, flash
from services.ml_service import train_prediction_model, predict_match_outcome

ml_bp = Blueprint('ml', __name__)

@ml_bp.route('/predict', methods=['GET', 'POST'])
def predict():
    """Match outcome prediction using ML."""
    prediction = None
    
    if request.method == 'POST':
        possession = float(request.form.get('possession', 50))
        shots = int(request.form.get('shots', 10))
        shots_on_target = int(request.form.get('shots_on_target', 5))
        corners = int(request.form.get('corners', 5))
        venue = request.form.get('venue', 'Home')
        
        is_home = venue == 'Home'
        
        # Check if model exists, if not train it
        if not os.path.exists('data/model.pkl'):
            model, message = train_prediction_model()
            if model is None:
                flash(message, 'warning')
                return render_template('predict.html', prediction=None)
        
        prediction = predict_match_outcome(possession, shots, shots_on_target, corners, is_home)
        
        if prediction is None:
            flash('Error making prediction. Please ensure model is trained.', 'error')
    
    return render_template('predict.html', prediction=prediction)
