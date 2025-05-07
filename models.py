from datetime import datetime
from flask_login import UserMixin
from db import db

class User(UserMixin, db.Model):
    """User model for web interface authentication."""
    __tablename__ = 'casino_users'  # Custom table name to avoid conflicts
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    discord_id = db.Column(db.String(64), unique=True, nullable=True)
    
    def __repr__(self):
        return f'<User {self.username}>'