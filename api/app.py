import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app  # Import the Flask app from the root directory

# Vercel will use 'app' as the entry point
