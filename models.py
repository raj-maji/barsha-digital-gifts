from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), default="Kolaghat")
    pincode = db.Column(db.String(20), default="721134")
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default="bi-gift")
    image_url = db.Column(db.String(255), nullable=True)
    is_service = db.Column(db.Boolean, default=False)  # True for printout/flex/binding
    display_order = db.Column(db.Integer, default=0)
    
    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float, nullable=True)
    stock = db.Column(db.Integer, default=50)
    image_url = db.Column(db.String(255), nullable=True)
    
    # Customization flags
    is_customizable = db.Column(db.Boolean, default=True)
    allow_photo_upload = db.Column(db.Boolean, default=True)
    allow_text_customization = db.Column(db.Boolean, default=True)
    customization_help_text = db.Column(db.String(255), default="Upload high resolution photo & your message")
    
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    @property
    def current_price(self):
        if self.discount_price and self.discount_price > 0:
            return self.discount_price
        return self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.discount_price < self.price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    def __repr__(self):
        return f'<Product {self.name}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), default="Kolaghat")
    pincode = db.Column(db.String(20), default="721134")
    order_notes = db.Column(db.Text, nullable=True)
    
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='cod')  # 'razorpay', 'upi_qr', 'cod'
    payment_status = db.Column(db.String(50), default='Pending') # 'Pending', 'Paid', 'Failed', 'Verified'
    order_status = db.Column(db.String(50), default='Placed')    # 'Placed', 'Processing', 'In Printing', 'Shipped', 'Delivered', 'Cancelled'
    
    razorpay_order_id = db.Column(db.String(100), nullable=True)
    razorpay_payment_id = db.Column(db.String(100), nullable=True)
    upi_utr = db.Column(db.String(100), nullable=True)
    upi_screenshot = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(200), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    subtotal = db.Column(db.Float, nullable=False)
    
    # Custom print details
    custom_text = db.Column(db.String(255), nullable=True)
    custom_image = db.Column(db.String(255), nullable=True)
    custom_instructions = db.Column(db.Text, nullable=True)

    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderItem {self.product_name}>'

class ServiceInquiry(db.Model):
    __tablename__ = 'service_inquiries'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120), nullable=True)
    service_type = db.Column(db.String(100), nullable=False) # Flex, Visiting Card, Spiral Binding, Vinyl Sticker, etc.
    quantity_estimate = db.Column(db.String(100), nullable=True)
    details = db.Column(db.Text, nullable=False)
    file_attachment = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='New') # 'New', 'Quotation Sent', 'Approved', 'Completed'
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f'<ServiceInquiry {self.service_type} - {self.customer_name}>'

class StoreSetting(db.Model):
    __tablename__ = 'store_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    @classmethod
    def get_val(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting and setting.value else default

    @classmethod
    def set_val(cls, key, value):
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(key=key, value=value)
            db.session.add(setting)
        else:
            setting.value = value
        db.session.commit()

    def __repr__(self):
        return f'<StoreSetting {self.key}={self.value}>'

