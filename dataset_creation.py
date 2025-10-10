# dataset_creation.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import json

def generate_dataset():
    np.random.seed(42)
    n_samples = 5000
    
    # Generate synthetic data
    data = {
        'car_condition': np.random.choice(['Excellent', 'Good', 'Fair', 'Poor'], n_samples, p=[0.2, 0.4, 0.3, 0.1]),
        'service_type': np.random.choice(['Oil Change', 'Brake Service', 'Tire Rotation', 'Engine Repair', 
                                        'Transmission', 'Electrical', 'AC Service'], n_samples),
        'staff_experience': np.random.randint(1, 21, n_samples),  # years
        'spare_part_status': np.random.choice(['In Stock', 'Available Soon', 'Need Ordering'], n_samples, p=[0.6, 0.3, 0.1]),
        'workload': np.random.randint(1, 11, n_samples),  # 1-10 scale
    }
    
    df = pd.DataFrame(data)
    
    # Calculate turnaround time based on features (in hours)
    turnaround_time = []
    
    for idx, row in df.iterrows():
        base_time = 0
        
        # Car condition impact
        condition_weights = {'Excellent': 0.8, 'Good': 1.0, 'Fair': 1.3, 'Poor': 1.7}
        base_time += condition_weights[row['car_condition']] * 2
        
        # Service type impact
        service_weights = {
            'Oil Change': 1, 'Tire Rotation': 1.5, 'Brake Service': 3, 
            'AC Service': 4, 'Electrical': 5, 'Engine Repair': 8, 'Transmission': 10
        }
        base_time += service_weights[row['service_type']]
        
        # Staff experience impact (more experience = less time)
        base_time *= (1.5 - (row['staff_experience'] * 0.05))
        
        # Spare part impact
        part_weights = {'In Stock': 1, 'Available Soon': 1.5, 'Need Ordering': 3}
        base_time *= part_weights[row['spare_part_status']]
        
        # Workload impact
        base_time *= (1 + (row['workload'] * 0.1))
        
        # Add some random noise
        base_time += np.random.normal(0, 0.5)
        
        turnaround_time.append(max(0.5, base_time))  # Minimum 0.5 hours
    
    df['turnaround_time'] = turnaround_time
    return df

def train_model():
    # Generate dataset
    df = generate_dataset()
    
    # Preprocessing
    le_condition = LabelEncoder()
    le_service = LabelEncoder()
    le_parts = LabelEncoder()
    
    df['car_condition_encoded'] = le_condition.fit_transform(df['car_condition'])
    df['service_type_encoded'] = le_service.fit_transform(df['service_type'])
    df['spare_part_status_encoded'] = le_parts.fit_transform(df['spare_part_status'])
    
    # Features and target
    features = ['car_condition_encoded', 'service_type_encoded', 'staff_experience', 
                'spare_part_status_encoded', 'workload']
    X = df[features]
    y = df['turnaround_time']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performance:")
    print(f"Mean Absolute Error: {mae:.2f} hours")
    print(f"R² Score: {r2:.2f}")
    
    # Save artifacts
    artifacts = {
        'model': model,
        'scaler': scaler,
        'le_condition': le_condition,
        'le_service': le_service,
        'le_parts': le_parts,
        'feature_names': features
    }
    
    with open('model_artifacts.pkl', 'wb') as f:
        pickle.dump(artifacts, f)
    
    # Save sample data for demonstration
    df.head(100).to_csv('sample_service_data.csv', index=False)
    
    return artifacts, df

if __name__ == "__main__":
    artifacts, df = train_model()