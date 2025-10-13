import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def predict_service_time(car_condition, service_type, staff_experience, spare_part_status, workload):
    """
    Rule-based prediction without ML dependencies
    """
    # Base service times (hours)
    service_times = {
        'Oil Change': 1.0,
        'Tire Rotation': 1.5, 
        'Brake Service': 3.0,
        'AC Service': 4.0,
        'Electrical': 5.0,
        'Engine Repair': 8.0,
        'Transmission': 10.0
    }
    
    # Multipliers
    condition_multiplier = {'Excellent': 0.8, 'Good': 1.0, 'Fair': 1.3, 'Poor': 1.7}
    parts_multiplier = {'In Stock': 1.0, 'Available Soon': 1.5, 'Need Ordering': 2.0}
    
    # Calculate
    base_time = service_times.get(service_type, 2.0)
    total_time = base_time
    total_time *= condition_multiplier.get(car_condition, 1.0)
    total_time *= parts_multiplier.get(spare_part_status, 1.0)
    total_time *= max(0.7, 1.3 - (staff_experience * 0.03))
    total_time *= (1 + (workload * 0.08))
    
    return max(0.5, round(total_time, 2))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        car_condition = request.form['car_condition']
        service_type = request.form['service_type']
        staff_experience = float(request.form['staff_experience'])
        spare_part_status = request.form['spare_part_status']
        workload = float(request.form['workload'])
        
        hours = predict_service_time(car_condition, service_type, staff_experience, spare_part_status, workload)
        
        # Format output
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
            'raw_hours': hours
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Service running smoothly'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
