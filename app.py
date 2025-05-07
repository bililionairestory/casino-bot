import os
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from utils.data_manager import DataManager
from db import db
from models import User

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize data manager for Discord bot data
bot_data_manager = DataManager()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def load_bot_data():
    """
    Load data from the Discord bot for the current user.
    Returns None if user is not logged in or Discord account is not linked.
    """
    if not current_user.is_authenticated or not current_user.discord_id:
        return None
    
    # Get data for the user's linked Discord account
    user_data = bot_data_manager.get_user_data(current_user.discord_id)
    return user_data

@app.route('/')
def index():
    """Homepage with bot information and links."""
    return render_template('index.html')

@app.route('/leaderboard')
def leaderboard():
    """Display the global gambling leaderboard."""
    # Get all user data from the bot
    all_data = bot_data_manager.get_all_data()
    
    # Sort by balance, highest first
    sorted_data = sorted(
        all_data.items(),
        key=lambda x: x[1]["balance"],
        reverse=True
    )
    
    # Limit to top 20
    top_users = sorted_data[:20]
    
    return render_template('leaderboard.html', leaderboard_data=top_users)

@app.route('/how-to-play')
def how_to_play():
    """Display information about how to use the bot and play games."""
    return render_template('how_to_play.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Basic validation
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return render_template('register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Invalid email address', 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing account info and bot stats."""
    # Get Discord data if account is linked
    discord_data = None
    if current_user.discord_id:
        discord_data = bot_data_manager.get_user_data(current_user.discord_id)
        
        # Add current timestamp for daily reward countdown
        session['now'] = datetime.now().timestamp()
    
    return render_template('dashboard.html', user=current_user, discord_data=discord_data)

@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/link-discord', methods=['GET', 'POST'])
@login_required
def link_discord():
    """Link user's Discord account to their web account."""
    if request.method == 'POST':
        discord_id = request.form.get('discord_id')
        
        if not discord_id:
            flash('Discord ID is required', 'danger')
            return render_template('link_discord.html')
        
        # Validate that it's a numeric ID
        if not discord_id.isdigit():
            flash('Discord ID must be a numeric value', 'danger')
            return render_template('link_discord.html')
        
        # Check if this Discord ID is already linked to another account
        existing_user = User.query.filter_by(discord_id=discord_id).first()
        if existing_user and existing_user.id != current_user.id:
            flash('This Discord ID is already linked to another account', 'danger')
            return render_template('link_discord.html')
        
        # Update user's Discord ID
        current_user.discord_id = discord_id
        db.session.commit()
        
        flash('Discord account linked successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('link_discord.html')

@app.route('/api/slot-symbols')
def slot_symbols():
    """API endpoint to get slot machine symbols and payouts"""
    # This could be expanded to pull data from the actual slot machine
    symbols = {
        "7️⃣": {"type": "Rare", "payout_3": 500, "payout_2": 25},
        "💎": {"type": "Uncommon", "payout_3": 25, "payout_2": 10},
        "🎰": {"type": "Wild", "payout_3": 5, "payout_2": 3, "special": "Replaces any symbol except Scatter"},
        "*️⃣": {"type": "Scatter", "payout_3": 3, "payout_2": 2, "special": "Counts anywhere on the line"},
        "🔔": {"type": "Medium", "payout_3": 2, "payout_2": 1},
        "🍊": {"type": "Common", "payout_3": 1, "payout_2": 1},
        "🍋": {"type": "Common", "payout_3": 0.75, "payout_2": 1},
        "❤️": {"type": "Common", "payout_3": 0.5, "payout_2": 0.75},
        "🍒": {"type": "Common", "payout_3": 0.5, "payout_2": 0.25}
    }
    return jsonify({"symbols": symbols})

# Create database tables
with app.app_context():
    db.create_all()