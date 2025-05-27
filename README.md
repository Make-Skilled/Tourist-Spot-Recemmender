# Tourist Spot Recommender

A modern web application that helps users discover and explore tourist spots around the world. Built with Flask, SQLite, and Tailwind CSS.

## Features

- Beautiful and responsive landing page
- User authentication (login/register)
- Personalized dashboard
- Tourist spot recommendations
- Search and filter functionality
- Modern UI with Tailwind CSS

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Tourist-Spot-Recemmender.git
cd Tourist-Spot-Recemmender
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated

2. Initialize the database:
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

3. Run the Flask application:
```bash
python app.py
```

4. Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
Tourist-Spot-Recemmender/
├── app.py              # Main application file
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── static/            # Static files (CSS, images)
└── templates/         # HTML templates
    ├── base.html      # Base template
    ├── landing.html   # Landing page
    ├── login.html     # Login page
    ├── register.html  # Registration page
    └── dashboard.html # User dashboard
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.