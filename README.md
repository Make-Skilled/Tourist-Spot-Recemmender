# Tourist Spot Recommender

A Flask-based web application that provides personalized tourist spot recommendations across India. The application uses machine learning to suggest tourist destinations based on user preferences, categories, and locations.

## Features

- User Authentication (Register/Login/Logout)
- Personalized Tourist Spot Recommendations
- Filter by:
  - Category (City, Beach, Historical, Mountain, etc.)
  - Location (State)
  - Minimum Rating
  - Number of Recommendations
- Detailed Information for Each Spot:
  - Activities Available
  - Best Time to Visit
  - Budget Level
  - Family Friendliness
  - Trip Duration

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Tourist-Spot-Recommender.git
cd Tourist-Spot-Recommender
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Install required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
Tourist-Spot-Recommender/
├── app.py                 # Main application file
├── models.py             # Database models
├── extensions.py         # Flask extensions
├── recommender.py        # Recommendation system
├── requirements.txt      # Project dependencies
├── tourist_spots.csv     # Tourist spots data
└── templates/            # HTML templates
    ├── index.html
    ├── login.html
    ├── register.html
    └── dashboard.html
```

## Running the Application

1. Make sure you're in the project directory and your virtual environment is activated

2. Run the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## Usage

1. Register a new account:
   - Click on "Register" in the navigation bar
   - Fill in your details (username, email, password)
   - Submit the form

2. Login:
   - Click on "Login" in the navigation bar
   - Enter your credentials
   - Submit the form

3. Get Recommendations:
   - After logging in, you'll be taken to the dashboard
   - Select your preferences:
     - Category (optional)
     - Location (optional)
     - Minimum Rating
     - Number of Recommendations
   - Click "Get Recommendations"

4. View Results:
   - The system will display personalized recommendations
   - Each recommendation includes:
     - Place name
     - Category
     - Rating
     - Best time to visit
     - Activities
     - Budget level
     - Trip duration

## Technologies Used

- Backend:
  - Flask (Web Framework)
  - SQLAlchemy (Database ORM)
  - Flask-Login (User Authentication)
  - scikit-learn (Machine Learning)
  - pandas (Data Processing)

- Frontend:
  - HTML
  - CSS
  - JavaScript

## Data

The application uses a comprehensive dataset of tourist spots across India, including:
- Popular destinations
- Historical sites
- Natural attractions
- Religious places
- Adventure spots
- Cultural centers

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Your Name - your.email@example.com
Project Link: https://github.com/yourusername/Tourist-Spot-Recommender

## Acknowledgments

- Data sources for tourist spots
- Flask documentation
- scikit-learn documentation
- All contributors who have helped in the development of this project