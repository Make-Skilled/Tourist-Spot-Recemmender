import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TouristSpotRecommender:
    def __init__(self):
        self.spots_data = pd.read_csv('tourist_spots.csv')
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self._prepare_data()

    def _prepare_data(self):
        # Combine relevant features for recommendation
        self.spots_data['combined_features'] = self.spots_data.apply(
            lambda row: ' '.join([
                str(row['Category']),
                str(row['Activities']),
                str(row['Budget Level']),
                str(row['Family Friendly'])
            ]), axis=1
        )
        
        # Create TF-IDF matrix
        self.tfidf_matrix = self.tfidf.fit_transform(self.spots_data['combined_features'])

    def get_recommendations_by_category(self, category, num_recommendations=5):
        # Filter by category
        category_spots = self.spots_data[self.spots_data['Category'].str.lower() == category.lower()]
        if category_spots.empty:
            return pd.DataFrame()
        
        # Get recommendations
        return category_spots.nlargest(num_recommendations, 'Rating')

    def get_recommendations_by_location(self, location, num_recommendations=5):
        # Filter by location
        location_spots = self.spots_data[self.spots_data['State'].str.lower() == location.lower()]
        if location_spots.empty:
            return pd.DataFrame()
        
        # Get recommendations
        return location_spots.nlargest(num_recommendations, 'Rating')

    def get_recommendations_by_category_and_location(self, category, location, num_recommendations=5):
        # Filter by both category and location
        filtered_spots = self.spots_data[
            (self.spots_data['Category'].str.lower() == category.lower()) &
            (self.spots_data['State'].str.lower() == location.lower())
        ]
        if filtered_spots.empty:
            return pd.DataFrame()
        
        # Get recommendations
        return filtered_spots.nlargest(num_recommendations, 'Rating')

    def get_top_rated_spots(self, num_recommendations=5):
        # Get top rated spots overall
        return self.spots_data.nlargest(num_recommendations, 'Rating') 