import joblib
import pandas as pd
import numpy as np
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TouristSpotRecommender:
    def __init__(self):
        self.model = None
        self.label_encoders = None
        self.spots_data = None
        self.load_model()

    def load_model(self):
        """Load the trained model and data."""
        try:
            # Check if model files exist
            model_files = {
                'model': 'models/random_forest_model.joblib',
                'encoders': 'models/label_encoders.joblib',
                'data': 'models/processed_data.csv'
            }
            
            for name, path in model_files.items():
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Model file not found: {path}")
            
            logger.info("Loading model components...")
            
            # Load the trained model components
            self.model = joblib.load(model_files['model'])
            self.label_encoders = joblib.load(model_files['encoders'])
            self.spots_data = pd.read_csv(model_files['data'])
            
            # Convert all string columns to lowercase for case-insensitive matching
            string_columns = ['State', 'Place', 'Category', 'Activities', 'Best Time to Visit',
                            'Budget Level', 'Family Friendly', 'Hotels Nearby',
                            'Travel Vehicles Available']
            for col in string_columns:
                if col in self.spots_data.columns:
                    self.spots_data[col] = self.spots_data[col].str.lower()
            
            logger.info(f"Loaded data with {len(self.spots_data)} spots")
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}", exc_info=True)
            raise

    def encode_input(self, input_data):
        """Encode input data using the saved label encoders."""
        try:
            encoded_data = {}
            for col, encoder in self.label_encoders.items():
                if col in input_data:
                    # Convert input to lowercase for case-insensitive matching
                    input_value = str(input_data[col]).lower()
                    # Handle unknown categories by using the most common category
                    try:
                        encoded_data[col] = encoder.transform([input_value])[0]
                    except:
                        encoded_data[col] = encoder.transform([encoder.classes_[0]])[0]
            return encoded_data
        except Exception as e:
            logger.error(f"Error encoding input: {str(e)}")
            raise

    def get_recommendations_by_category_and_location(self, category, location, n=5):
        """Get recommendations based on category and location with flexible matching."""
        try:
            logger.debug(f"Getting recommendations for category={category}, location={location}")
            
            # Convert inputs to lowercase
            category = str(category).lower() if category else ""
            location = str(location).lower() if location else ""
            
            # Initialize empty DataFrame for recommendations
            recommendations = pd.DataFrame()
            
            # Try exact matches first
            if category and location:
                filtered_spots = self.spots_data[
                    (self.spots_data['Category'].str.contains(category, case=False, na=False)) &
                    (self.spots_data['State'].str.contains(location, case=False, na=False))
                ]
                if not filtered_spots.empty:
                    recommendations = filtered_spots
            
            # If no exact matches, try category match
            if recommendations.empty and category:
                category_spots = self.spots_data[
                    self.spots_data['Category'].str.contains(category, case=False, na=False)
                ]
                if not category_spots.empty:
                    recommendations = category_spots
            
            # If still no matches, try location match
            if recommendations.empty and location:
                location_spots = self.spots_data[
                    self.spots_data['State'].str.contains(location, case=False, na=False)
                ]
                if not location_spots.empty:
                    recommendations = location_spots
            
            # If still no matches, return top rated spots
            if recommendations.empty:
                logger.debug("No matches found, returning top rated spots")
                recommendations = self.spots_data.sort_values('Rating', ascending=False)
            
            # Prepare input data for prediction
            input_data = {
                'Category': category if category else recommendations['Category'].iloc[0],
                'State': location if location else recommendations['State'].iloc[0],
                'Activities': recommendations['Activities'].iloc[0],
                'Best Time to Visit': recommendations['Best Time to Visit'].iloc[0],
                'Budget Level': recommendations['Budget Level'].iloc[0],
                'Family Friendly': recommendations['Family Friendly'].iloc[0],
                'Hotels Nearby': recommendations['Hotels Nearby'].iloc[0],
                'Travel Vehicles Available': recommendations['Travel Vehicles Available'].iloc[0],
                'Trip Duration (days)': recommendations['Trip Duration (days)'].iloc[0]
            }
            
            # Encode input data
            encoded_input = self.encode_input(input_data)
            
            # Create feature array for prediction
            feature_columns = ['Category', 'State', 'Activities', 'Best Time to Visit',
                             'Budget Level', 'Family Friendly', 'Hotels Nearby',
                             'Travel Vehicles Available', 'Trip Duration (days)']
            
            X = np.array([[encoded_input[col] for col in feature_columns]])
            
            # Get predicted ratings
            predicted_ratings = self.model.predict(X)
            
            # Sort spots by predicted rating and return top n
            recommendations['Predicted_Rating'] = predicted_ratings[0]
            recommendations = recommendations.sort_values('Predicted_Rating', ascending=False).head(n)
            
            logger.debug(f"Returning {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
            return self.spots_data.sort_values('Rating', ascending=False).head(n)

    def get_recommendations_by_category(self, category, n=5):
        """Get recommendations based on category with flexible matching."""
        try:
            logger.debug(f"Getting recommendations for category={category}")
            
            # Convert input to lowercase
            category = str(category).lower() if category else ""
            
            # Try category match
            if category:
                filtered_spots = self.spots_data[
                    self.spots_data['Category'].str.contains(category, case=False, na=False)
                ]
            else:
                filtered_spots = self.spots_data
            
            if filtered_spots.empty:
                logger.debug("No category matches found, returning top rated spots")
                filtered_spots = self.spots_data.sort_values('Rating', ascending=False)
            
            # Prepare input data for prediction
            input_data = {
                'Category': category if category else filtered_spots['Category'].iloc[0],
                'State': filtered_spots['State'].iloc[0],
                'Activities': filtered_spots['Activities'].iloc[0],
                'Best Time to Visit': filtered_spots['Best Time to Visit'].iloc[0],
                'Budget Level': filtered_spots['Budget Level'].iloc[0],
                'Family Friendly': filtered_spots['Family Friendly'].iloc[0],
                'Hotels Nearby': filtered_spots['Hotels Nearby'].iloc[0],
                'Travel Vehicles Available': filtered_spots['Travel Vehicles Available'].iloc[0],
                'Trip Duration (days)': filtered_spots['Trip Duration (days)'].iloc[0]
            }
            
            # Encode input data
            encoded_input = self.encode_input(input_data)
            
            # Create feature array for prediction
            feature_columns = ['Category', 'State', 'Activities', 'Best Time to Visit',
                             'Budget Level', 'Family Friendly', 'Hotels Nearby',
                             'Travel Vehicles Available', 'Trip Duration (days)']
            
            X = np.array([[encoded_input[col] for col in feature_columns]])
            
            # Get predicted ratings
            predicted_ratings = self.model.predict(X)
            
            # Sort spots by predicted rating and return top n
            filtered_spots['Predicted_Rating'] = predicted_ratings[0]
            recommendations = filtered_spots.sort_values('Predicted_Rating', ascending=False).head(n)
            
            logger.debug(f"Returning {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
            return self.spots_data.sort_values('Rating', ascending=False).head(n)

    def get_recommendations_by_location(self, location, n=5):
        """Get recommendations based on location with flexible matching."""
        try:
            logger.debug(f"Getting recommendations for location={location}")
            
            # Convert input to lowercase
            location = str(location).lower() if location else ""
            
            # Try location match
            if location:
                filtered_spots = self.spots_data[
                    self.spots_data['State'].str.contains(location, case=False, na=False)
                ]
            else:
                filtered_spots = self.spots_data
            
            if filtered_spots.empty:
                logger.debug("No location matches found, returning top rated spots")
                filtered_spots = self.spots_data.sort_values('Rating', ascending=False)
            
            # Prepare input data for prediction
            input_data = {
                'Category': filtered_spots['Category'].iloc[0],
                'State': location if location else filtered_spots['State'].iloc[0],
                'Activities': filtered_spots['Activities'].iloc[0],
                'Best Time to Visit': filtered_spots['Best Time to Visit'].iloc[0],
                'Budget Level': filtered_spots['Budget Level'].iloc[0],
                'Family Friendly': filtered_spots['Family Friendly'].iloc[0],
                'Hotels Nearby': filtered_spots['Hotels Nearby'].iloc[0],
                'Travel Vehicles Available': filtered_spots['Travel Vehicles Available'].iloc[0],
                'Trip Duration (days)': filtered_spots['Trip Duration (days)'].iloc[0]
            }
            
            # Encode input data
            encoded_input = self.encode_input(input_data)
            
            # Create feature array for prediction
            feature_columns = ['Category', 'State', 'Activities', 'Best Time to Visit',
                             'Budget Level', 'Family Friendly', 'Hotels Nearby',
                             'Travel Vehicles Available', 'Trip Duration (days)']
            
            X = np.array([[encoded_input[col] for col in feature_columns]])
            
            # Get predicted ratings
            predicted_ratings = self.model.predict(X)
            
            # Sort spots by predicted rating and return top n
            filtered_spots['Predicted_Rating'] = predicted_ratings[0]
            recommendations = filtered_spots.sort_values('Predicted_Rating', ascending=False).head(n)
            
            logger.debug(f"Returning {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
            return self.spots_data.sort_values('Rating', ascending=False).head(n)

    def get_top_rated_spots(self, n=5):
        """Get top rated spots."""
        try:
            logger.debug("Getting top rated spots")
            return self.spots_data.sort_values('Rating', ascending=False).head(n)
        except Exception as e:
            logger.error(f"Error getting top rated spots: {str(e)}", exc_info=True)
            return self.spots_data.sort_values('Rating', ascending=False).head(n) 