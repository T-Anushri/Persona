import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ----------------------------
# Detect if running on Vercel
# ----------------------------
ON_VERCEL = "VERCEL" in os.environ

# ----------------------------
# Configure Flask instance path
# ----------------------------
if ON_VERCEL:
    instance_path = "/tmp/instance"  # writable path on Vercel
else:
    instance_path = os.path.join(os.path.dirname(__file__), "instance")

os.makedirs(instance_path, exist_ok=True)
app = Flask(__name__, instance_path=instance_path)

# ----------------------------
# Configure upload folder
# ----------------------------
if ON_VERCEL:
    UPLOAD_FOLDER = "/tmp/uploads"
else:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static/uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ----------------------------
# Secret key and config
# ----------------------------
app.config['SECRET_KEY'] = 'persona-digital-twin-secret-key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ----------------------------
# SQLite DB path
# ----------------------------
if ON_VERCEL:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/persona.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///persona.db'

# ----------------------------
# Initialize DB
# ----------------------------
db = SQLAlchemy(app)

# ----------------------------
# Logging for missing AI services
# ----------------------------
try:
    from google_ai_service import google_ai_service, artisan_storytelling_agent
    AI_SERVICES_AVAILABLE = True
except ImportError:
    AI_SERVICES_AVAILABLE = False
    logging.warning("Google AI services not available")

# ----------------------------
# Database Models
# ----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='customer')  # artisan, customer, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Artisan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    craft_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(200))
    bio = db.Column(db.Text)
    cultural_background = db.Column(db.Text)
    craft_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    persona = db.relationship('Persona', backref='artisan', uselist=False)
    products = db.relationship('Product', backref='artisan', lazy=True)

class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artisan_id = db.Column(db.Integer, db.ForeignKey('artisan.id'), nullable=False)
    tone = db.Column(db.String(50), nullable=False)
    style = db.Column(db.String(50), nullable=False)
    storytelling_depth = db.Column(db.Integer, default=5)
    communication_style = db.Column(db.String(50), default='conversational')
    language_preference = db.Column(db.String(10), default='en')
    generated_bio = db.Column(db.Text)
    personality_traits = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artisan_id = db.Column(db.Integer, db.ForeignKey('artisan.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ai_enriched_description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=1)
    category = db.Column(db.String(100))
    images = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    cultural_significance = db.Column(db.Text)
    creation_story = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product', backref='order_items')

# ----------------------------
# AI Storytelling Agent
# ----------------------------
class AIStorytellingAgent:
    @staticmethod
    def generate_artisan_bio(artisan_data, persona_data):
        # Implementation stays the same as your code
        # ...
        tone = persona_data.get('tone', 'friendly')
        style = persona_data.get('style', 'traditional')
        depth = persona_data.get('storytelling_depth', 5)
        templates = {
            'friendly': {
                'intro': f"Hi there! I'm {artisan_data['name']}, and I'm passionate about {artisan_data['craft_type']}.",
                'craft': f"I've been creating beautiful {artisan_data['craft_type']} pieces from my workshop in {artisan_data['location']}.",
                'story': "Each piece I create tells a story - a blend of traditional techniques passed down through generations and my own creative vision."
            },
            'formal': {
                'intro': f"I am {artisan_data['name']}, a dedicated {artisan_data['craft_type']} artisan.",
                'craft': f"My workshop in {artisan_data['location']} serves as the foundation for creating exceptional {artisan_data['craft_type']} works.",
                'story': "My commitment lies in preserving traditional craftsmanship while incorporating contemporary design elements."
            },
            'poetic': {
                'intro': f"In the heart of {artisan_data['location']}, where tradition meets creativity, I am {artisan_data['name']}.",
                'craft': f"My hands dance with clay and dreams, shaping {artisan_data['craft_type']} that whisper ancient stories.",
                'story': "Every creation is a poem written in form and texture, a bridge between the wisdom of ancestors and the hopes of tomorrow."
            },
            'warm': {
                'intro': f"Welcome to my world! I'm {artisan_data['name']}, and {artisan_data['craft_type']} is not just my craft - it's my heart's language.",
                'craft': f"From my cozy workshop in {artisan_data['location']}, I pour love into every piece I create.",
                'story': "I believe that handmade items carry the warmth of human touch and the joy of creation. Each piece is made with care, just for you."
            }
        }
        template = templates.get(tone, templates['friendly'])
        bio_parts = [template['intro'], template['craft']]
        if depth >= 5:
            bio_parts.append(template['story'])
        if depth >= 7:
            bio_parts.append(f"My {artisan_data['craft_type']} reflects the rich cultural heritage of {artisan_data['location']}.")
        if depth >= 9:
            bio_parts.append("When you choose my work, you're not just buying a product - you're becoming part of a story that connects past, present, and future.")
        return " ".join(bio_parts)

    @staticmethod
    def enrich_product_description(product_data, artisan_persona):
        # Implementation stays the same
        base_description = product_data.get('description', '')
        tone = artisan_persona.tone
        craft_type = product_data.get('category', 'handcraft')
        enrichment_styles = {
            'friendly': f"This beautiful {craft_type} piece is one of my favorites to create! {base_description} I put so much care into every detail, and I hope you'll love it as much as I enjoyed making it.",
            'formal': f"This {craft_type} represents the finest in traditional craftsmanship. {base_description} Each element has been carefully considered to ensure both aesthetic appeal and functional excellence.",
            'poetic': f"Behold this {craft_type}, born from inspiration and shaped by skilled hands. {base_description} It carries within it the essence of creativity and the soul of artisanal tradition.",
            'warm': f"I'm so excited to share this special {craft_type} with you! {base_description} Made with love in my workshop, it's ready to bring joy and beauty to your space."
        }
        return enrichment_styles.get(tone, enrichment_styles['friendly'])

# ----------------------------
# Helper functions and routes
# ----------------------------
# All your routes, login_required, get_current_user, etc.
# Keep everything as-is from your original app.py
# ----------------------------

# ----------------------------
# Database init function
# ----------------------------
def init_db():
    """Initialize database with tables and sample data."""
    with app.app_context():
        db.create_all()
        # Optional: add sample data if needed
