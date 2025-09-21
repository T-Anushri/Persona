from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import logging
from typing import Dict, List, Optional

# Import Google AI services
try:
    from google_ai_service import (
        google_ai_service, 
        artisan_storytelling_agent
    )
    AI_SERVICES_AVAILABLE = True
except ImportError:
    AI_SERVICES_AVAILABLE = False
    logging.warning("Google AI services not available")

from config import Config

app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'persona-digital-twin-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/persona.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '../static/uploads'

db = SQLAlchemy(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ...existing models, routes, and logic from your original app.py...

# DO NOT call app.run() or init_db() here
# Vercel will handle the serverless execution

# Export the Flask app for Vercel
# This is the entry point Vercel expects
