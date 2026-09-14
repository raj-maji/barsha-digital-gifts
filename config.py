import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'barsha-digital-gift-secret-key-2026-kolaghat')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{BASE_DIR / 'barsha_gift.db'}")
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configurations
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

    # Payment Gateway Settings
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_BarshaDemo')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'test_secret_key_12345')
    
    # Direct UPI Payment Info (0% Fee, direct to shop account)
    SHOP_UPI_ID = os.environ.get('SHOP_UPI_ID', '8513010387@ybl')
    SHOP_UPI_NAME = "Barsha Digital Gifts"
    
    # Business Contacts
    SHOP_NAME = "Barsha Digital Gifts"
    SHOP_PHONE_1 = "8513010387"
    SHOP_PHONE_2 = "9832725105"
    SHOP_LOCATION = "Sahapur, Kolaghat, East Medinipur, West Bengal - 721134"
