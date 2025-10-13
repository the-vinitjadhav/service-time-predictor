# app.py - ML-Powered Service Time Predictor
import os
import pickle
import numpy as np
from flask import Flask, render_template, request, jsonify
import logging
from dataset_creation import train_lightweight_model, create_fallback_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variable for ML artifacts
artifacts = None

def load_ml_model():
    """Load ML model with fallback handling"""
    global artifacts
    try:
        with open('model_artifacts.pkl', 'rb') as f:
            artifacts = pickle.load(f)
        logger.info(f"✅ Model loaded: {artifacts['model_type']}")
        return True
    except FileNotFoundError:
        logger.warning("📝 No model found. Training new ML model...")
        artifacts = train_lightweight_model()
        return True
    except Exception as e:
        logger.error(f"❌ Model loading failed: {e}")
        artifacts = create_fallback_model()
        return False

def predict_with_ml(car_condition, service_type, staff_experience, spare_part_status, workload):
    """Make prediction using ML model or fallback"""
    try:
        if artifacts['model_type'] == 'ml_random_forest':
            # ML Prediction
            condition_encoded = artifacts['le_condition'].transform([car_condition])[0]
            service_encoded = artifacts['le_service'].transform([service_type])[0]
            parts_encoded = artifacts['le_parts'].transform([spare_part_status])[0]
            
            # Prepare features
            features = np.array([[
                condition_encoded, 
                service_encoded, 
                staff_experience,
                parts_encoded, 
                workload
            ]])
            
            # ML Prediction
            prediction = artifacts['model'].predict(features)[0]
            return max(0.5, float(prediction)), 'ml_model'
            
        else:
            # Rule-based fallback
            base_time = artifacts['service_times'].get(service_type, 2.0)
            time = base_time
            time *= artifacts['condition_multiplier'].get(car_condition, 1.0)
            time *= artifacts['parts_multiplier'].get(spare_part_status, 1.0)
            time *= max(0.7, 1.3 - (staff_experience * 0.03))
            time *= (1 + (workload * 0.08))
            return max(0.5, time), 'rule_based'
            
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        # Ultimate simple fallback
        simple_times = {'Oil Change': 1.0, 'Tire Rotation': 1.5, 'Brake Service': 3.0, 
                       'AC Service': 4.0, 'Engine Repair': 6.0}
        base_time = simple_times.get(service_type, 2.0)
        return base_time * (1 + (workload * 0.1)), 'simple_fallback'

# Load model on startup
load_ml_model()

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
        
        # Validate inputs
        if staff_experience < 1 or staff_experience > 30:
            return jsonify({'success': False, 'error': 'Staff experience must be between 1-30 years'})
        
        if workload < 1 or workload > 10:
            return jsonify({'success': False, 'error': 'Workload must be between 1-10'})
        
        # Make prediction
        hours, model_type = predict_with_ml(car_condition, service_type, staff_experience, spare_part_status, workload)
        
        # Format result
        if hours < 1:
            time_str = f"{int(hours * 60)} minutes"
        elif hours == 1:
            time_str = "1 hour"
        elif hours < 24:
            time_str = f"{hours:.1f} hours"
        else:
            days = hours / 8
            time_str = f"{days:.1f} days"
        
        return jsonify({
            'success': True,
            'prediction': time_str,
            'raw_hours': round(hours, 2),
            'model_type': model_type,
            'model_used': artifacts['model_type'] if artifacts else 'unknown'
        })
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Prediction service temporarily unavailable'
        })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': artifacts is not None,
        'model_type': artifacts.get('model_type', 'none') if artifacts else 'none',
        'message': 'ML Service Time Predictor is running'
    })

@app.route('/retrain', methods=['POST'])
def retrain_model():
    """Endpoint to retrain ML model"""
    try:
        global artifacts
        artifacts = train_lightweight_model()
        return jsonify({
            'success': True,
            'message': f"Model retrained successfully: {artifacts['model_type']}",
            'performance': artifacts.get('performance', {})
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting ML Service Predictor on port {port}")
    app.run(host='0.0.0.0', port=port)
