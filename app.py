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

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'persona-digital-twin-secret-key'
# Use /tmp/persona.db for Vercel serverless deployment
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/persona.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'


db = SQLAlchemy(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
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
    
    # Relationships
    persona = db.relationship('Persona', backref='artisan', uselist=False)
    products = db.relationship('Product', backref='artisan', lazy=True)

class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artisan_id = db.Column(db.Integer, db.ForeignKey('artisan.id'), nullable=False)
    tone = db.Column(db.String(50), nullable=False)  # friendly, formal, poetic, warm
    style = db.Column(db.String(50), nullable=False)  # traditional, modern, artistic
    storytelling_depth = db.Column(db.Integer, default=5)  # 1-10 scale
    communication_style = db.Column(db.String(50), default='conversational')
    language_preference = db.Column(db.String(10), default='en')
    generated_bio = db.Column(db.Text)
    personality_traits = db.Column(db.Text)  # JSON string
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
    images = db.Column(db.Text)  # JSON array of image paths
    status = db.Column(db.String(20), default='draft')  # draft, published, sold_out
    cultural_significance = db.Column(db.Text)
    creation_story = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='order_items')

# AI Storytelling Agent
class AIStorytellingAgent:
    @staticmethod
    def generate_artisan_bio(artisan_data, persona_data):
        """Generate AI-powered artisan biography based on persona settings"""
        tone = persona_data.get('tone', 'friendly')
        style = persona_data.get('style', 'traditional')
        depth = persona_data.get('storytelling_depth', 5)
        
        # Template-based generation with persona influence
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
            cultural_addition = f"My {artisan_data['craft_type']} reflects the rich cultural heritage of {artisan_data['location']}, where this art form has flourished for centuries."
            bio_parts.append(cultural_addition)
        
        if depth >= 9:
            personal_touch = "When you choose my work, you're not just buying a product - you're becoming part of a story that connects past, present, and future."
            bio_parts.append(personal_touch)
        
        return " ".join(bio_parts)
    
    @staticmethod
    def enrich_product_description(product_data, artisan_persona):
        """Enhance product description using artisan's persona"""
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

# Helper Functions
def is_logged_in():
    return 'user_id' in session

def get_current_user():
    if is_logged_in():
        return User.query.get(session['user_id'])
    return None

def login_required(f):
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def index():
    # Get featured artisans and products for homepage
    featured_artisans = db.session.query(Artisan).join(Product).filter(Product.status == 'published').limit(6).all()
    featured_products = Product.query.filter_by(status='published').limit(8).all()
    
    return render_template('index.html', 
                         featured_artisans=featured_artisans,
                         featured_products=featured_products,
                         current_user=get_current_user())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            user_type=data.get('user_type', 'customer')
        )
        
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        
        user = User.query.filter_by(username=data['username']).first()
        
        if user and check_password_hash(user.password_hash, data['password']):
            session['user_id'] = user.id
            return jsonify({'success': True, 'message': 'Login successful'})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/artisan/onboard')
@login_required
def artisan_onboard():
    user = get_current_user()
    if user.user_type != 'artisan':
        flash('Access denied. Artisan account required.')
        return redirect(url_for('index'))
    
    return render_template('artisan_onboard.html')

@app.route('/api/artisan/create', methods=['POST'])
@login_required
def create_artisan_profile():
    user = get_current_user()
    data = request.get_json()
    
    # Create artisan profile
    artisan = Artisan(
        user_id=user.id,
        name=data['name'],
        craft_type=data['craft_type'],
        location=data['location'],
        photo=data.get('photo', ''),
        cultural_background=data.get('cultural_background', ''),
        craft_history=data.get('craft_history', '')
    )
    
    db.session.add(artisan)
    db.session.flush()  # Get artisan ID
    
    # Create persona
    persona_data = data.get('persona', {})
    persona = Persona(
        artisan_id=artisan.id,
        tone=persona_data.get('tone', 'friendly'),
        style=persona_data.get('style', 'traditional'),
        storytelling_depth=persona_data.get('storytelling_depth', 5),
        communication_style=persona_data.get('communication_style', 'conversational'),
        language_preference=persona_data.get('language_preference', 'en'),
        personality_traits=json.dumps(persona_data.get('personality_traits', {}))
    )
    
    # Generate AI bio
    artisan_data = {
        'name': artisan.name,
        'craft_type': artisan.craft_type,
        'location': artisan.location
    }
    
    persona.generated_bio = AIStorytellingAgent.generate_artisan_bio(artisan_data, persona_data)
    artisan.bio = persona.generated_bio
    
    db.session.add(persona)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'artisan_id': artisan.id,
        'generated_bio': persona.generated_bio
    })

@app.route('/api/persona/preview', methods=['POST'])
def preview_persona():
    """Generate live preview of persona bio"""
    data = request.get_json()
    
    artisan_data = {
        'name': data.get('name', 'Sample Artisan'),
        'craft_type': data.get('craft_type', 'pottery'),
        'location': data.get('location', 'Sample City')
    }
    
    persona_data = data.get('persona', {})
    
    generated_bio = AIStorytellingAgent.generate_artisan_bio(artisan_data, persona_data)
    
    return jsonify({
        'success': True,
        'preview_bio': generated_bio
    })

@app.route('/artisan/dashboard')
@login_required
def artisan_dashboard():
    user = get_current_user()
    artisan = Artisan.query.filter_by(user_id=user.id).first()
    
    if not artisan:
        return redirect(url_for('artisan_onboard'))
    
    products = Product.query.filter_by(artisan_id=artisan.id).all()
    
    return render_template('artisan_dashboard.html', 
                         artisan=artisan, 
                         products=products)

@app.route('/marketplace')
def marketplace():
    view_type = request.args.get('view', 'scroll')  # scroll view only
    
    artisans_with_products = db.session.query(Artisan).join(Product).filter(Product.status == 'published').all()
    
    return render_template('marketplace.html', 
                         artisans_with_products=artisans_with_products,
                         view_type=view_type)

@app.route('/api/products/create', methods=['POST'])
@login_required
def create_product():
    user = get_current_user()
    artisan = Artisan.query.filter_by(user_id=user.id).first()
    
    if not artisan:
        return jsonify({'success': False, 'message': 'Artisan profile required'})
    
    data = request.get_json()
    
    product = Product(
        artisan_id=artisan.id,
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        stock_quantity=int(data.get('stock_quantity', 1)),
        category=data.get('category', ''),
        images=json.dumps(data.get('images', [])),
        cultural_significance=data.get('cultural_significance', ''),
        creation_story=data.get('creation_story', '')
    )
    
    # AI-enrich description using persona
    if artisan.persona:
        product.ai_enriched_description = AIStorytellingAgent.enrich_product_description(
            data, artisan.persona
        )
    else:
        product.ai_enriched_description = data['description']
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'product_id': product.id,
        'enriched_description': product.ai_enriched_description
    })

@app.route('/api/products/<int:product_id>/status', methods=['PUT'])
@login_required
def update_product_status():
    data = request.get_json()
    product_id = request.view_args['product_id']
    
    user = get_current_user()
    artisan = Artisan.query.filter_by(user_id=user.id).first()
    product = Product.query.filter_by(id=product_id, artisan_id=artisan.id).first()
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    
    product.status = data['status']
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/artisan/products')
@login_required
def my_products():
    """Artisan's product management page"""
    if not get_current_user().user_type == 'artisan':
        flash('Access denied. Artisan account required.', 'error')
        return redirect(url_for('index'))
    
    # Get artisan's products
    artisan = Artisan.query.filter_by(user_id=get_current_user().id).first()
    if not artisan:
        flash('Artisan profile not found.', 'error')
        return redirect(url_for('index'))
    
    products = Product.query.filter_by(artisan_id=artisan.id).order_by(Product.created_at.desc()).all()
    
    return render_template('my_products.html', products=products, artisan=artisan)

@app.route('/api/products/create', methods=['POST'])
@login_required
def create_product_api():
    """API endpoint to create a new product with AI enhancement"""
    if not get_current_user().user_type == 'artisan':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Get artisan
        artisan = Artisan.query.filter_by(user_id=get_current_user().id).first()
        if not artisan:
            return jsonify({'success': False, 'message': 'Artisan profile not found'}), 404
        
        # Validate required fields
        required_fields = ['name', 'description', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field.title()} is required'}), 400
        
        # Create new product
        product = Product(
            name=data['name'],
            description=data['description'],
            price=float(data['price']),
            category=data.get('category', artisan.craft_type),
            stock_quantity=int(data.get('stock_quantity', 1)),
            cultural_significance=data.get('cultural_significance', ''),
            artisan_id=artisan.id,
            status='draft'  # Start as draft
        )
        
        # Generate AI-enhanced description using Google AI
        try:
            from google_ai_service import artisan_storytelling_agent
            
            # Create context for AI enhancement
            context = {
                'artisan_name': artisan.name,
                'craft_type': artisan.craft_type,
                'persona_tone': artisan.persona.tone or 'warm',
                'cultural_background': artisan.cultural_background or '',
                'product_name': product.name,
                'product_description': product.description,
                'cultural_significance': product.cultural_significance
            }
            
            # Generate enhanced description
            enhanced_description = artisan_storytelling_agent.generate_product_description(context)
            if enhanced_description and enhanced_description.strip():
                product.ai_enriched_description = enhanced_description
            
        except Exception as e:
            print(f"AI enhancement failed: {e}")
            # Continue without AI enhancement
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Product created successfully!',
            'product_id': product.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/products/<int:product_id>/status', methods=['PUT'])
@login_required
def update_product_status_api(product_id):
    """API endpoint to update product status"""
    if not get_current_user().user_type == 'artisan':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['draft', 'published', 'sold_out']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        # Get artisan
        artisan = Artisan.query.filter_by(user_id=get_current_user().id).first()
        if not artisan:
            return jsonify({'success': False, 'message': 'Artisan profile not found'}), 404
        
        # Get product
        product = Product.query.filter_by(id=product_id, artisan_id=artisan.id).first()
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        # Update status
        product.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Product status updated to {new_status}!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/generate/artisan-bio', methods=['POST'])
def generate_artisan_bio():
    """Generate artisan biography using Google AI"""
    if not AI_SERVICES_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI services not available',
            'bio': 'Passionate artisan creating beautiful handcrafted pieces with traditional techniques.'
        }), 503
    
    try:
        data = request.get_json()
        artisan_data = {
            'name': data.get('name', ''),
            'craft_type': data.get('craft_type', ''),
            'location': data.get('location', ''),
            'experience_years': data.get('experience_years', 5)
        }
        tone = data.get('tone', 'warm')
        
        bio = artisan_storytelling_agent.generate_artisan_bio(artisan_data, tone)
        
        return jsonify({
            'success': True,
            'bio': bio,
            'tone': tone
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'bio': 'Passionate artisan creating beautiful handcrafted pieces with traditional techniques.'
        }), 500

@app.route('/api/generate/story-title', methods=['POST'])
def generate_story_title():
    """Generate story title using Google AI"""
    if not AI_SERVICES_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI services not available',
            'title': 'Artisan\'s Journey'
        }), 503
    
    try:
        data = request.get_json()
        artisan_data = {
            'craft_type': data.get('craft_type', ''),
            'location': data.get('location', '')
        }
        tone = data.get('tone', 'poetic')
        
        title = artisan_storytelling_agent.generate_story_title(artisan_data, tone)
        
        return jsonify({
            'success': True,
            'title': title,
            'tone': tone
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'title': 'Artisan\'s Journey'
        }), 500

@app.route('/api/generate/product-description', methods=['POST'])
def generate_product_description():
    """Generate product description using Google AI"""
    if not AI_SERVICES_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI services not available',
            'description': 'Exquisite handcrafted item made with premium materials and traditional techniques.'
        }), 503
    
    try:
        data = request.get_json()
        product_data = {
            'name': data.get('name', ''),
            'category': data.get('category', ''),
            'materials': data.get('materials', '')
        }
        persona = data.get('persona', 'warm')
        
        description = artisan_storytelling_agent.generate_product_description(product_data, persona)
        
        return jsonify({
            'success': True,
            'description': description,
            'persona': persona
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'description': 'Exquisite handcrafted item made with premium materials and traditional techniques.'
        }), 500

@app.route('/api/generate/cultural-context', methods=['POST'])
def generate_cultural_context():
    """Generate cultural context using Google AI"""
    if not AI_SERVICES_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI services not available',
            'context': 'Traditional craft with rich cultural heritage and historical significance.'
        }), 503
    
    try:
        data = request.get_json()
        craft_type = data.get('craft_type', '')
        location = data.get('location', '')
        
        context = artisan_storytelling_agent.generate_cultural_context(craft_type, location)
        
        return jsonify({
            'success': True,
            'context': context
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'context': 'Traditional craft with rich cultural heritage and historical significance.'
        }), 500

@app.route('/api/generate/product-bundles', methods=['POST'])
def generate_product_bundles():
    """Generate product bundle suggestions using Google AI"""
    if not AI_SERVICES_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI services not available',
            'bundles': []
        }), 503
    
    try:
        data = request.get_json()
        products = data.get('products', [])
        theme = data.get('theme', 'complementary')
        
        bundles = product_recommendation_agent.suggest_product_bundles(products, theme)
        
        return jsonify({
            'success': True,
            'bundles': bundles,
            'theme': theme
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'bundles': []
        }), 500

@app.route('/api/generate/marketing-content', methods=['POST'])
def generate_marketing_content():
    """Generate marketing content using Google AI"""
    if not AI_SERVICES_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI services not available',
            'content': 'Discover authentic handcrafted treasures that celebrate traditional artistry.'
        }), 503
    
    try:
        data = request.get_json()
        content_type = data.get('type', 'social_media')
        artisan_data = data.get('artisan', {})
        product_data = data.get('product', {})
        
        if content_type == 'social_media':
            content = marketing_content_agent.generate_social_media_post(
                'Instagram', artisan_data, product_data
            )
        elif content_type == 'email':
            campaign_type = data.get('campaign_type', 'newsletter')
            target_audience = data.get('target_audience', 'customers')
            content = marketing_content_agent.generate_email_campaign(campaign_type, target_audience)
        else:
            content = 'Discover authentic handcrafted treasures that celebrate traditional artistry.'
        
        return jsonify({
            'success': True,
            'content': content,
            'type': content_type
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'content': 'Discover authentic handcrafted treasures that celebrate traditional artistry.'
        }), 500

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Translate text using Google Translate API"""
    if not AI_SERVICES_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Translation services not available',
            'translated_text': request.get_json().get('text', '')
        }), 503
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_language = data.get('target_language', 'en')
        source_language = data.get('source_language', None)
        
        translated_text = google_ai_service.translate_text(text, target_language, source_language)
        
        return jsonify({
            'success': True,
            'translated_text': translated_text,
            'target_language': target_language,
            'source_language': source_language
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'translated_text': text
        }), 500

# Initialize database and sample data
def init_db():
    """Initialize database with tables and sample data."""
    with app.app_context():
        db.create_all()
    
        # Create sample data if none exists
        if not User.query.first():
            # Create sample admin user
            admin = User(
                username='admin',
                email='admin@persona.com',
                password_hash=generate_password_hash('admin123'),
                user_type='admin'
            )
            db.session.add(admin)
            
            # Create sample artisan user
            artisan_user = User(
                username='maya_potter',
                email='maya@persona.com',
                password_hash=generate_password_hash('potter123'),
                user_type='artisan'
            )
            db.session.add(artisan_user)
            db.session.flush()
            
            # Create sample artisan profile
            artisan = Artisan(
                user_id=artisan_user.id,
                name='Maya Sharma',
                craft_type='Pottery',
                location='Jaipur, Rajasthan',
                photo='sample_artisan.jpg',
                cultural_background='Traditional Rajasthani pottery techniques passed down through generations',
                craft_history='Started learning pottery at age 12 from grandmother, now 15 years of experience'
            )
            db.session.add(artisan)
            db.session.flush()
            
            # Create sample persona
            persona = Persona(
                artisan_id=artisan.id,
                tone='warm',
                style='traditional',
                storytelling_depth=7,
                communication_style='conversational',
                language_preference='en'
            )
            
            # Generate bio
            artisan_data = {
                'name': artisan.name,
                'craft_type': artisan.craft_type,
                'location': artisan.location
            }
            persona_data = {
                'tone': 'warm',
                'style': 'traditional',
                'storytelling_depth': 7
            }
            
            persona.generated_bio = AIStorytellingAgent.generate_artisan_bio(artisan_data, persona_data)
            artisan.bio = persona.generated_bio
            
            db.session.add(persona)
            
            # Create sample products
            products_data = [
                {
                    'name': 'Handcrafted Blue Pottery Vase',
                    'description': 'Beautiful traditional blue pottery vase with intricate floral patterns',
                    'price': 2500.0,
                    'category': 'Pottery',
                    'stock_quantity': 5
                },
                {
                    'name': 'Terracotta Tea Set',
                    'description': 'Complete tea set made from natural terracotta clay',
                    'price': 1800.0,
                    'category': 'Pottery',
                    'stock_quantity': 3
                }
            ]
            
            for prod_data in products_data:
                product = Product(
                    artisan_id=artisan.id,
                    name=prod_data['name'],
                    description=prod_data['description'],
                    price=prod_data['price'],
                    stock_quantity=prod_data['stock_quantity'],
                    category=prod_data['category'],
                    status='published'
                )
                
                # AI-enrich description
                product.ai_enriched_description = AIStorytellingAgent.enrich_product_description(
                    prod_data, persona
                )
                
                db.session.add(product)
            
            db.session.commit()

# Remove local-only code for Vercel deployment
# if not IS_VERCEL:
#     init_db()  # Optional: only if you want sample data locally
#     app.run(debug=True, host='0.0.0.0', port=5000)
