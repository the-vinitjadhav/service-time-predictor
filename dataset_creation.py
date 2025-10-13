import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_ml_dataset(n_samples=1000):
    """Generate dataset optimized for free tier deployment"""
    logger.info("🤖 Generating ML training dataset...")
    np.random.seed(42)
    
    # Generate realistic service data
    data = {
        'car_condition': np.random.choice(['Excellent', 'Good', 'Fair', 'Poor'], n_samples, p=[0.2, 0.4, 0.3, 0.1]),
        'service_type': np.random.choice(['Oil Change', 'Brake Service', 'Tire Rotation', 'Engine Repair', 'AC Service'], n_samples),
        'staff_experience': np.random.randint(1, 21, n_samples),
        'spare_part_status': np.random.choice(['In Stock', 'Available Soon', 'Need Ordering'], n_samples, p=[0.6, 0.3, 0.1]),
        'workload': np.random.randint(1, 11, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Calculate realistic turnaround times
    turnaround_time = []
    for _, row in df.iterrows():
        # Base time from service type
        service_times = {
            'Oil Change': 1.0, 'Tire Rotation': 1.5, 'Brake Service': 3.0,
            'AC Service': 4.0, 'Engine Repair': 6.0
        }
        
        base_time = service_times[row['service_type']]
        
        # Apply multipliers
        condition_multiplier = {'Excellent': 0.8, 'Good': 1.0, 'Fair': 1.3, 'Poor': 1.7}
        parts_multiplier = {'In Stock': 1.0, 'Available Soon': 1.5, 'Need Ordering': 2.0}
        
        total_time = base_time
        total_time *= condition_multiplier[row['car_condition']]
        total_time *= parts_multiplier[row['spare_part_status']]
        total_time *= max(0.7, 1.3 - (row['staff_experience'] * 0.03))
        total_time *= (1 + (row['workload'] * 0.08))
        
        # Add noise and ensure bounds
        noise = np.random.normal(0, 0.3)
        final_time = max(0.5, total_time + noise)
        turnaround_time.append(round(final_time, 2))
    
    df['turnaround_time'] = turnaround_time
    logger.info(f"✅ Dataset generated: {len(df)} samples")
    return df

def train_lightweight_model():
    """Train optimized ML model for free tier"""
    try:
        logger.info("🎯 Training Lightweight Random Forest Model...")
        
        # Generate dataset
        df = generate_ml_dataset(800)  # Smaller dataset for free tier
        
        # Encode categorical features
        le_condition = LabelEncoder()
        le_service = LabelEncoder()
        le_parts = LabelEncoder()
        
        df['car_condition_encoded'] = le_condition.fit_transform(df['car_condition'])
        df['service_type_encoded'] = le_service.fit_transform(df['service_type'])
        df['spare_part_status_encoded'] = le_parts.fit_transform(df['spare_part_status'])
        
        # Prepare features and target
        features = ['car_condition_encoded', 'service_type_encoded', 'staff_experience', 'spare_part_status_encoded', 'workload']
        X = df[features].values
        y = df['turnaround_time'].values
        
        # Train lightweight Random Forest
        model = RandomForestRegressor(
            n_estimators=50,      # Reduced for performance
            max_depth=10,         # Limited depth
            min_samples_split=5,
            random_state=42,
            n_jobs=1             # Single job for compatibility
        )
        
        model.fit(X, y)
        
        # Quick evaluation
        train_score = model.score(X, y)
        logger.info(f"📊 Model R² Score: {train_score:.3f}")
        
        # Save artifacts
        artifacts = {
            'model': model,
            'le_condition': le_condition,
            'le_service': le_service,
            'le_parts': le_parts,
            'feature_names': features,
            'model_type': 'ml_random_forest',
            'performance': {'r2_score': train_score}
        }
        
        with open('model_artifacts.pkl', 'wb') as f:
            pickle.dump(artifacts, f)
        
        logger.info("💾 ML Model saved successfully!")
        return artifacts
        
    except Exception as e:
        logger.error(f"❌ ML training failed: {e}")
        # Fallback to rule-based
        return create_fallback_model()

def create_fallback_model():
    """Create rule-based fallback if ML fails"""
    logger.info("🔄 Creating rule-based fallback model...")
    artifacts = {
        'model_type': 'rule_based_fallback',
        'service_times': {
            'Oil Change': 1.0, 'Tire Rotation': 1.5, 'Brake Service': 3.0,
            'AC Service': 4.0, 'Engine Repair': 6.0
        },
        'condition_multiplier': {'Excellent': 0.8, 'Good': 1.0, 'Fair': 1.3, 'Poor': 1.7},
        'parts_multiplier': {'In Stock': 1.0, 'Available Soon': 1.5, 'Need Ordering': 2.0}
    }
    
    with open('model_artifacts.pkl', 'wb') as f:
        pickle.dump(artifacts, f)
    
    return artifacts

if __name__ == "__main__":
    print("🚗 ML Service Time Predictor - Training")
    artifacts = train_lightweight_model()
    print(f"✅ Model trained: {artifacts['model_type']}")
