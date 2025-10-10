# app.py
from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

# Load model artifacts
def load_model():
    with open('model_artifacts.pkl', 'rb') as f:
        artifacts = pickle.load(f)
    return artifacts

artifacts = load_model()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        car_condition = request.form['car_condition']
        service_type = request.form['service_type']
        staff_experience = float(request.form['staff_experience'])
        spare_part_status = request.form['spare_part_status']
        workload = float(request.form['workload'])
        
        # Preprocess input
        condition_encoded = artifacts['le_condition'].transform([car_condition])[0]
        service_encoded = artifacts['le_service'].transform([service_type])[0]
        parts_encoded = artifacts['le_parts'].transform([spare_part_status])[0]
        
        # Create feature array
        features = np.array([[condition_encoded, service_encoded, staff_experience, 
                            parts_encoded, workload]])
        
        # Scale features
        features_scaled = artifacts['scaler'].transform(features)
        
        # Make prediction
        prediction = artifacts['model'].predict(features_scaled)[0]
        
        # Format prediction
        hours = max(0.5, prediction)  # Ensure minimum 0.5 hours
        if hours < 1:
            time_str = f"{int(hours * 60)} minutes"
        elif hours == 1:
            time_str = "1 hour"
        elif hours < 24:
            time_str = f"{hours:.1f} hours"
        else:
            days = hours / 8  # Assuming 8-hour work day
            time_str = f"{days:.1f} days"
        
        return jsonify({
            'success': True,
            'prediction': time_str,
            'raw_hours': round(hours, 2)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for programmatic access"""
    try:
        data = request.get_json()
        
        car_condition = data['car_condition']
        service_type = data['service_type']
        staff_experience = float(data['staff_experience'])
        spare_part_status = data['spare_part_status']
        workload = float(data['workload'])
        
        # Preprocess input
        condition_encoded = artifacts['le_condition'].transform([car_condition])[0]
        service_encoded = artifacts['le_service'].transform([service_type])[0]
        parts_encoded = artifacts['le_parts'].transform([spare_part_status])[0]
        
        # Create feature array
        features = np.array([[condition_encoded, service_encoded, staff_experience, 
                            parts_encoded, workload]])
        
        # Scale features
        features_scaled = artifacts['scaler'].transform(features)
        
        # Make prediction
        prediction = artifacts['model'].predict(features_scaled)[0]
        
        return jsonify({
            'turnaround_time_hours': round(max(0.5, prediction), 2),
            'car_condition': car_condition,
            'service_type': service_type,
            'staff_experience': staff_experience,
            'spare_part_status': spare_part_status,
            'workload': workload
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)