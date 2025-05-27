import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_and_preprocess_data():
    """Load and preprocess the tourist spots data."""
    try:
        # Read the CSV file
        df = pd.read_csv('tourist_spots.csv')
        
        # Ensure all required columns are present
        required_columns = ['State', 'Place', 'Category', 'Hotels Nearby', 
                          'Travel Vehicles Available', 'Rating', 'Best Time to Visit',
                          'Family Friendly', 'Activities', 'Budget Level', 
                          'Trip Duration (days)']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in the dataset")
        
        # Convert categorical features to string and handle missing values
        categorical_columns = ['Category', 'State', 'Activities', 'Best Time to Visit',
                             'Budget Level', 'Family Friendly', 'Hotels Nearby',
                             'Travel Vehicles Available']
        
        for col in categorical_columns:
            df[col] = df[col].fillna('').astype(str)
        
        # Convert rating to float and handle missing values
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(0)
        
        # Convert trip duration to float and handle missing values
        df['Trip Duration (days)'] = pd.to_numeric(df['Trip Duration (days)'], errors='coerce').fillna(0)
        
        # Convert all string columns to lowercase
        for col in categorical_columns:
            df[col] = df[col].str.lower()
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def encode_categorical_features(df):
    """Encode categorical features using LabelEncoder."""
    try:
        # Create a copy of the dataframe
        df_encoded = df.copy()
        
        # Initialize LabelEncoder
        label_encoders = {}
        
        # Columns to encode
        categorical_columns = ['Category', 'State', 'Activities', 'Best Time to Visit',
                             'Budget Level', 'Family Friendly', 'Hotels Nearby',
                             'Travel Vehicles Available']
        
        # Encode each categorical column
        for col in categorical_columns:
            label_encoders[col] = LabelEncoder()
            df_encoded[col] = label_encoders[col].fit_transform(df[col])
        
        return df_encoded, label_encoders
        
    except Exception as e:
        logger.error(f"Error encoding features: {str(e)}")
        raise

def train_model():
    """Train the Random Forest model."""
    try:
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Load and preprocess the data
        logger.info("Loading and preprocessing data")
        df = load_and_preprocess_data()
        
        # Encode categorical features
        logger.info("Encoding categorical features")
        df_encoded, label_encoders = encode_categorical_features(df)
        
        # Save the original data and label encoders
        logger.info("Saving processed data and encoders")
        df.to_csv('models/processed_data.csv', index=False)
        joblib.dump(label_encoders, 'models/label_encoders.joblib')
        
        # Prepare features and target
        feature_columns = ['Category', 'State', 'Activities', 'Best Time to Visit',
                         'Budget Level', 'Family Friendly', 'Hotels Nearby',
                         'Travel Vehicles Available', 'Trip Duration (days)']
        
        X = df_encoded[feature_columns]
        y = df_encoded['Rating']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Initialize and train Random Forest model
        logger.info("Training Random Forest model")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        # Calculate and log model accuracy
        train_accuracy = rf_model.score(X_train, y_train)
        test_accuracy = rf_model.score(X_test, y_test)
        logger.info(f"Training accuracy: {train_accuracy:.4f}")
        logger.info(f"Testing accuracy: {test_accuracy:.4f}")
        
        # Save the trained model
        logger.info("Saving trained model")
        joblib.dump(rf_model, 'models/random_forest_model.joblib')
        
        # Save feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': rf_model.feature_importances_
        })
        feature_importance.to_csv('models/feature_importance.csv', index=False)
        
        logger.info("Model training completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    train_model() 