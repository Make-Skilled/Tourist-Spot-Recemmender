from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager
from models import User, TouristSpot
from recommender import TouristSpotRecommender
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tourist_spots.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize the recommender
recommender = TouristSpotRecommender()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    spots = db.relationship('TouristSpot', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class TouristSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    recommendations = []
    error_message = None
    
    if request.method == 'POST':
        try:
            # Get form data
            category = request.form.get('category', '').strip()
            location = request.form.get('location', '').strip()
            min_rating = float(request.form.get('min_rating', 0))
            num_recommendations = int(request.form.get('num_recommendations', 5))
            preferences = request.form.get('preferences', '').strip()
            
            logger.debug(f"Form data: category={category}, location={location}, min_rating={min_rating}, num_recommendations={num_recommendations}, preferences={preferences}")
            
            # Get recommendations based on input
            if category and location:
                logger.debug("Getting recommendations by category and location")
                recommendations = recommender.get_recommendations_by_category_and_location(
                    category, location, num_recommendations
                )
            elif category:
                logger.debug("Getting recommendations by category")
                recommendations = recommender.get_recommendations_by_category(
                    category, num_recommendations
                )
            elif location:
                logger.debug("Getting recommendations by location")
                recommendations = recommender.get_recommendations_by_location(
                    location, num_recommendations
                )
            else:
                logger.debug("Getting top rated spots")
                recommendations = recommender.get_top_rated_spots(num_recommendations)
            
            # Filter by minimum rating
            if not recommendations.empty:
                recommendations = recommendations[recommendations['Rating'] >= min_rating]
                logger.debug(f"Found {len(recommendations)} recommendations after rating filter")
            
            # Convert recommendations to list of dictionaries
            recommendations = recommendations.to_dict('records')
            logger.debug(f"Final recommendations count: {len(recommendations)}")
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
            error_message = "An error occurred while getting recommendations. Please try again."
    
    return render_template('dashboard.html', 
                         recommendations=recommendations,
                         error_message=error_message,
                         username=current_user.username)

@app.route('/add_spot', methods=['POST'])
@login_required
def add_spot():
    try:
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        location = request.form.get('location')
        category = request.form.get('category')
        rating = float(request.form.get('rating'))
        image_url = request.form.get('image_url')

        # Create new spot
        new_spot = TouristSpot(
            name=name,
            description=description,
            location=location,
            category=category,
            rating=rating,
            image_url=image_url
        )

        # Add to database
        db.session.add(new_spot)
        db.session.commit()

        # Update CSV file
        update_csv_file()

        # Retrain the model
        train_model()

        flash('Tourist spot added successfully!')
    except Exception as e:
        flash(f'Error adding tourist spot: {str(e)}')
    
    return redirect(url_for('dashboard'))

def update_csv_file():
    """Update the CSV file with the latest data from the database."""
    spots = TouristSpot.query.all()
    data = []
    for spot in spots:
        data.append({
            'name': spot.name,
            'description': spot.description,
            'location': spot.location,
            'category': spot.category,
            'rating': spot.rating,
            'image_url': spot.image_url
        })
    
    df = pd.DataFrame(data)
    df.to_csv('tourist_spots.csv', index=False)

def train_model():
    """Retrain the recommendation model with updated data."""
    try:
        from train_model import main as train_main
        train_main()
    except Exception as e:
        print(f"Error training model: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 