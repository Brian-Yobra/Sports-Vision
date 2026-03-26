"""
SportVision Analytics - Main Flask Application
===============================================
A comprehensive sports analytics platform with player statistics,
team analytics, CSV upload, ML predictions, and admin panel.

Author: SportVision Team
Tech Stack: Flask, SQLite, pandas, scikit-learn, Chart.js
"""

from flask import Flask
import os

# Import blueprints
from routes.main import main_bp
from routes.players import players_bp
from routes.teams import teams_bp
from routes.upload import upload_bp
from routes.ml import ml_bp
from routes.admin import admin_bp

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'sportvision_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(players_bp)
app.register_blueprint(teams_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(ml_bp)
app.register_blueprint(admin_bp)
