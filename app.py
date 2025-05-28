from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from extensions import db, login_manager
from models import User
from recommender import TouristSpotRecommender
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tourist_spots.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize the recommender
recommender = TouristSpotRecommender()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 8

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not email or not password or not confirm_password:
            flash('All fields are required')
            return redirect(url_for('register'))

        if not validate_email(email):
            flash('Please enter a valid email address')
            return redirect(url_for('register'))

        if not validate_password(password):
            flash('Password must be at least 8 characters long')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        user = User(username=username, email=email, name=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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
            category = request.form.get('category', '').strip()
            location = request.form.get('location', '').strip()
            min_rating = float(request.form.get('min_rating', 0))
            num_recommendations = int(request.form.get('num_recommendations', 5))
            
            if category and location:
                recommendations = recommender.get_recommendations_by_category_and_location(
                    category, location, num_recommendations
                )
            elif category:
                recommendations = recommender.get_recommendations_by_category(
                    category, num_recommendations
                )
            elif location:
                recommendations = recommender.get_recommendations_by_location(
                    location, num_recommendations
                )
            else:
                recommendations = recommender.get_top_rated_spots(num_recommendations)
            
            if not recommendations.empty:
                recommendations = recommendations[recommendations['Rating'] >= min_rating]
            
            recommendations = recommendations.to_dict('records')
            
        except Exception as e:
            error_message = "An error occurred while getting recommendations. Please try again."
    
    return render_template('dashboard.html', 
                         recommendations=recommendations,
                         error_message=error_message,
                         username=current_user.username)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 