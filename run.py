#!/usr/bin/env python3
"""
Simple run script for Persona Artisan Platform
Just run: python run.py
"""

import os
import sys
from app import app, db, init_db

def create_directories():
    """Create necessary directories."""
    directories = [
        'static/uploads',
        'instance',
        'logs'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def setup_database():
    """Initialize database with sample data."""
    with app.app_context():
        try:
            # Initialize database and create sample data
            init_db()
            print("Database tables created successfully!")
            print("Sample data created successfully!")
                
        except Exception as e:
            print(f"Database setup error: {e}")
            return False
    
    return True

def main():
    """Main function to run the application."""
    print("🎨 Starting Persona Artisan Platform...")
    print("=" * 50)
    
    # Create necessary directories
    create_directories()
    
    # Setup database
    if not setup_database():
        print("❌ Database setup failed!")
        sys.exit(1)
    
    print("\n✅ Setup complete!")
    print("\n🚀 Starting Flask development server...")
    print("📱 Access the application at: http://localhost:5000")
    print("\n👤 Default login credentials:")
    print("   Admin: admin / admin123")
    print("   Artisan: maya_potter / potter123")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the Flask app
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
