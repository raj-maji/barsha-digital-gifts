import os
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort, send_from_directory
)
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Category, Product, Order, OrderItem, ServiceInquiry, StoreSetting
from payments import get_upi_payment_link, create_razorpay_order, verify_razorpay_payment, generate_upi_transaction_id

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folders exist
os.makedirs(app.config['UPLOAD_FOLDER'] / 'products', exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'] / 'custom', exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'] / 'services', exist_ok=True)

db.init_app(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# --- Custom Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Admin login required.', 'danger')
            return redirect(url_for('login', next=request.url))
        user = db.session.get(User, session['user_id'])
        if not user or not user.is_admin:
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Context Processors ---
@app.context_processor
def inject_global_vars():
    categories = Category.query.order_by(Category.display_order).all()
    current_user = None
    if 'user_id' in session:
        current_user = db.session.get(User, session['user_id'])
    
    cart = session.get('cart', {})
    cart_count = sum(item.get('quantity', 1) for item in cart.values())
    
    opening_time = StoreSetting.get_val('opening_time', '8:00 AM')
    closing_time = StoreSetting.get_val('closing_time', '10:00 PM')
    store_timing = f"Open {opening_time} - {closing_time}"
    
    new_orders_count = 0
    if current_user and current_user.is_admin:
        new_orders_count = Order.query.filter_by(order_status='Placed').count()
    pending_payments_count = new_orders_count
    
    return {
        'shop_name': Config.SHOP_NAME,
        'shop_phone_1': Config.SHOP_PHONE_1,
        'shop_phone_2': Config.SHOP_PHONE_2,
        'shop_location': Config.SHOP_LOCATION,
        'shop_upi_id': Config.SHOP_UPI_ID,
        'store_timing': store_timing,
        'opening_time': opening_time,
        'closing_time': closing_time,
        'nav_categories': categories,
        'current_user': current_user,
        'cart_count': cart_count,
        'new_orders_count': new_orders_count,
        'pending_payments_count': pending_payments_count,
        'now': datetime.now(timezone.utc)
    }

@app.template_filter('currency')
def currency_filter(amount):
    try:
        return f"₹{float(amount):,.2f}"
    except (ValueError, TypeError):
        return f"₹{amount}"

# --- Public Routes ---

@app.route('/')
def index():
    featured_products = Product.query.filter_by(is_active=True, is_featured=True).limit(8).all()
    categories = Category.query.filter_by(is_service=False).order_by(Category.display_order).all()
    services = Category.query.filter_by(is_service=True).all()
    recent_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    return render_template('index.html', 
                           featured_products=featured_products,
                           categories=categories,
                           services=services,
                           recent_products=recent_products)

@app.route('/products')
def products():
    category_slug = request.args.get('category')
    search_query = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'newest')
    
    query = Product.query.filter_by(is_active=True)
    selected_category = None
    
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)
            
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%') | Product.description.ilike(f'%{search_query}%'))
        
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())
        
    products_list = query.all()
    categories = Category.query.order_by(Category.display_order).all()
    
    return render_template('products.html', 
                           products=products_list, 
                           categories=categories,
                           selected_category=selected_category,
                           search_query=search_query,
                           sort=sort)

@app.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()
    return render_template('product_detail.html', product=product, related_products=related_products)

@app.route('/services')
def services():
    service_cat = Category.query.filter_by(slug='printing-services').first()
    service_products = []
    if service_cat:
        service_products = Product.query.filter_by(category_id=service_cat.id, is_active=True).all()
    return render_template('services.html', service_products=service_products)

@app.route('/services/inquire', methods=['POST'])
def service_inquire():
    name = request.form.get('customer_name')
    phone = request.form.get('customer_phone')
    email = request.form.get('customer_email')
    service_type = request.form.get('service_type')
    quantity = request.form.get('quantity_estimate')
    details = request.form.get('details')
    
    file_path = None
    if 'service_file' in request.files:
        file = request.files['service_file']
        if file and file.filename and allowed_file(file.filename):
            filename = f"service_{uuid.uuid4().hex[:10]}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'services', filename))
            file_path = f"/static/uploads/services/{filename}"
            
    inquiry = ServiceInquiry(
        customer_name=name,
        customer_phone=phone,
        customer_email=email,
        service_type=service_type,
        quantity_estimate=quantity,
        details=details,
        file_attachment=file_path
    )
    db.session.add(inquiry)
    db.session.commit()
    
    flash('Thank you! Your printing request has been submitted. Our team in Kolaghat will call you shortly.', 'success')
    return redirect(url_for('services'))

# --- Cart System ---

@app.route('/cart')
def cart():
    cart_session = session.get('cart', {})
    cart_items = []
    subtotal = 0.0
    
    for item_key, item_data in cart_session.items():
        product = db.session.get(Product, item_data['product_id'])
        if product:
            price = product.current_price
            item_total = price * item_data['quantity']
            subtotal += item_total
            cart_items.append({
                'key': item_key,
                'product': product,
                'quantity': item_data['quantity'],
                'unit_price': price,
                'subtotal': item_total,
                'custom_text': item_data.get('custom_text', ''),
                'custom_image': item_data.get('custom_image', ''),
                'custom_notes': item_data.get('custom_notes', '')
            })
            
    delivery_fee = 0.0 if subtotal >= 500 or subtotal == 0 else 50.0
    total = subtotal + delivery_fee
    
    return render_template('cart.html', 
                           cart_items=cart_items, 
                           subtotal=subtotal, 
                           delivery_fee=delivery_fee, 
                           total=total)

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    custom_text = request.form.get('custom_text', '').strip()
    custom_notes = request.form.get('custom_notes', '').strip()
    
    product = Product.query.get_or_404(product_id)
    
    custom_image_url = ''
    if 'custom_image' in request.files:
        file = request.files['custom_image']
        if file and file.filename and allowed_file(file.filename):
            filename = f"custom_{uuid.uuid4().hex[:10]}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'custom', filename))
            custom_image_url = f"/static/uploads/custom/{filename}"
            
    cart_session = session.get('cart', {})
    
    # Unique cart item key based on product id and customization
    item_key = f"{product_id}_{uuid.uuid4().hex[:6]}" if (custom_text or custom_image_url) else str(product_id)
    
    if item_key in cart_session and not (custom_text or custom_image_url):
        cart_session[item_key]['quantity'] += quantity
    else:
        cart_session[item_key] = {
            'product_id': product.id,
            'quantity': quantity,
            'custom_text': custom_text,
            'custom_image': custom_image_url,
            'custom_notes': custom_notes
        }
        
    session['cart'] = cart_session
    flash(f'"{product.name}" added to your cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/cart/update', methods=['POST'])
def update_cart():
    item_key = request.form.get('item_key')
    action = request.form.get('action')
    cart_session = session.get('cart', {})
    
    if item_key in cart_session:
        if action == 'increase':
            cart_session[item_key]['quantity'] += 1
        elif action == 'decrease':
            cart_session[item_key]['quantity'] -= 1
            if cart_session[item_key]['quantity'] <= 0:
                del cart_session[item_key]
        elif action == 'remove':
            del cart_session[item_key]
            
    session['cart'] = cart_session
    flash('Cart updated.', 'info')
    return redirect(url_for('cart'))

@app.route('/cart/clear')
def clear_cart():
    session.pop('cart', None)
    flash('Your cart has been cleared.', 'info')
    return redirect(url_for('cart'))

# --- Checkout & Payment ---

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_session = session.get('cart', {})
    if not cart_session:
        flash('Your cart is empty! Add gifts or printing items before checking out.', 'warning')
        return redirect(url_for('products'))
        
    subtotal = 0.0
    for item_data in cart_session.values():
        prod = db.session.get(Product, item_data['product_id'])
        if prod:
            subtotal += prod.current_price * item_data['quantity']
            
    delivery_fee = 0.0 if subtotal >= 500 else 50.0
    total_amount = subtotal + delivery_fee
    
    user = None
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        
    if request.method == 'POST':
        customer_name = request.form.get('name')
        customer_phone = request.form.get('phone')
        customer_email = request.form.get('email')
        delivery_address = request.form.get('address')
        city = request.form.get('city', 'Kolaghat')
        pincode = request.form.get('pincode', '721134')
        order_notes = request.form.get('order_notes', '')
        # Solely Cash on Delivery (COD)
        payment_method = 'Cash on Delivery (COD)'
        
        # Generate Order Number (BDG-YYYYMMDD-XXXX)
        today_str = datetime.now(timezone.utc).strftime('%Y%m%d')
        random_suffix = uuid.uuid4().hex[:4].upper()
        order_number = f"BDG-{today_str}-{random_suffix}"
        
        order = Order(
            order_number=order_number,
            user_id=user.id if user else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            delivery_address=delivery_address,
            city=city,
            pincode=pincode,
            order_notes=order_notes,
            total_amount=total_amount,
            payment_method='Cash on Delivery (COD)',
            payment_status='Pending',
            order_status='Placed'
        )
        db.session.add(order)
        db.session.flush()
        
        # Create Order Items
        for item_data in cart_session.values():
            prod = db.session.get(Product, item_data['product_id'])
            if prod:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=prod.id,
                    product_name=prod.name,
                    unit_price=prod.current_price,
                    quantity=item_data['quantity'],
                    subtotal=prod.current_price * item_data['quantity'],
                    custom_text=item_data.get('custom_text', ''),
                    custom_image=item_data.get('custom_image', ''),
                    custom_instructions=item_data.get('custom_notes', '')
                )
                db.session.add(order_item)
                
        db.session.commit()
        
        # Clear cart upon order placement
        session.pop('cart', None)
        flash('🎉 Thank you! Your order has been placed successfully with Cash on Delivery.', 'success')
        return redirect(url_for('order_success', order_number=order_number))
            
    return render_template('checkout.html', 
                           subtotal=subtotal, 
                           delivery_fee=delivery_fee, 
                           total_amount=total_amount,
                           user=user)

@app.route('/payment/gateway/<order_number>')
def pay_gateway(order_number):
    return redirect(url_for('order_success', order_number=order_number))

# Backward compatibility aliases
@app.route('/payment/upi/<order_number>')
def pay_upi(order_number):
    return redirect(url_for('order_success', order_number=order_number))

@app.route('/payment/razorpay/<order_number>')
def pay_razorpay(order_number):
    return redirect(url_for('order_success', order_number=order_number))

@app.route('/payment/submit-upi', methods=['POST'])
def submit_upi_payment():
    order_number = request.form.get('order_number')
    return redirect(url_for('order_success', order_number=order_number))

@app.route('/payment/process-upi', methods=['POST'])
def process_upi_payment():
    order_number = request.form.get('order_number')
    return redirect(url_for('order_success', order_number=order_number))

@app.route('/payment/razorpay/verify', methods=['POST'])
def verify_razorpay():
    order_number = request.form.get('order_number')
    return redirect(url_for('order_success', order_number=order_number))

@app.route('/order/success/<order_number>')
def order_success(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_success.html', order=order)

# --- Authentication ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            flash(f'Welcome back, {user.name}!', 'success')
            
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page or url_for('admin_dashboard'))
            return redirect(next_page or url_for('user_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone')
        password = request.form.get('password')
        address = request.form.get('address')
        city = request.form.get('city', 'Kolaghat')
        pincode = request.form.get('pincode', '721134')
        
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('login'))
            
        user = User(
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['is_admin'] = False
        flash('Account created successfully! Welcome to Barsha Digital Gift.', 'success')
        return redirect(url_for('user_dashboard'))
        
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- User Dashboard ---

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    user = db.session.get(User, session['user_id'])
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('user/dashboard.html', user=user, orders=orders)

@app.route('/user/order/<order_number>')
@login_required
def user_order_detail(order_number):
    user = db.session.get(User, session['user_id'])
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.user_id != user.id and not user.is_admin:
        abort(403)
    return render_template('user/order_detail.html', order=order)

# --- Admin Dashboard ---

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_orders = Order.query.count()
    total_products = Product.query.count()
    pending_prints = Order.query.filter(Order.order_status.in_(['Placed', 'Processing', 'In Printing'])).count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.payment_status.in_(['Paid', 'Verified'])).scalar() or 0.0
    
    new_placed_orders = Order.query.filter_by(order_status='Placed').order_by(Order.created_at.desc()).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    recent_inquiries = ServiceInquiry.query.order_by(ServiceInquiry.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                           total_orders=total_orders,
                           total_products=total_products,
                           pending_prints=pending_prints,
                           total_revenue=total_revenue,
                           new_placed_orders=new_placed_orders,
                           pending_payment_orders=new_placed_orders,
                           recent_orders=recent_orders,
                           recent_inquiries=recent_inquiries)

@app.route('/admin/products')
@admin_required
def admin_products():
    products_list = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products_list)

@app.route('/admin/products/new', methods=['GET', 'POST'])
@admin_required
def admin_product_new():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug') or secure_filename(name.lower().replace(' ', '-'))
        category_id = request.form.get('category_id', type=int)
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        discount_price = request.form.get('discount_price', type=float) or None
        stock = request.form.get('stock', 50, type=int)
        is_customizable = 'is_customizable' in request.form
        is_featured = 'is_featured' in request.form
        custom_help = request.form.get('customization_help_text', '')
        
        image_url = request.form.get('image_url', '').strip()
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file and file.filename and allowed_file(file.filename):
                filename = f"prod_{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'products', filename))
                image_url = f"/static/uploads/products/{filename}"
                
        # Ensure unique slug
        base_slug = slug
        count = 1
        while Product.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{count}"
            count += 1
            
        prod = Product(
            name=name,
            slug=slug,
            category_id=category_id,
            description=description,
            price=price,
            discount_price=discount_price,
            stock=stock,
            image_url=image_url,
            is_customizable=is_customizable,
            is_featured=is_featured,
            customization_help_text=custom_help
        )
        db.session.add(prod)
        db.session.commit()
        flash(f'Product "{prod.name}" successfully added!', 'success')
        return redirect(url_for('admin_products'))
        
    return render_template('admin/product_form.html', categories=categories, product=None)

@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(id):
    prod = Product.query.get_or_404(id)
    categories = Category.query.all()
    if request.method == 'POST':
        prod.name = request.form.get('name')
        prod.category_id = request.form.get('category_id', type=int)
        prod.description = request.form.get('description')
        prod.price = request.form.get('price', type=float)
        prod.discount_price = request.form.get('discount_price', type=float) or None
        prod.stock = request.form.get('stock', type=int)
        prod.is_customizable = 'is_customizable' in request.form
        prod.is_featured = 'is_featured' in request.form
        prod.customization_help_text = request.form.get('customization_help_text', '')
        
        if request.form.get('image_url'):
            prod.image_url = request.form.get('image_url')
            
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file and file.filename and allowed_file(file.filename):
                filename = f"prod_{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'products', filename))
                prod.image_url = f"/static/uploads/products/{filename}"
                
        db.session.commit()
        flash(f'Product "{prod.name}" updated successfully!', 'success')
        return redirect(url_for('admin_products'))
        
    return render_template('admin/product_form.html', categories=categories, product=prod)

@app.route('/admin/products/delete/<int:id>', methods=['POST'])
@admin_required
def admin_product_delete(id):
    prod = Product.query.get_or_404(id)
    db.session.delete(prod)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    status_filter = request.args.get('status')
    payment_filter = request.args.get('payment_status')
    query = Order.query
    if status_filter:
        query = query.filter_by(order_status=status_filter)
    if payment_filter:
        query = query.filter_by(payment_status=payment_filter)
    orders_list = query.order_by(Order.created_at.desc()).all()
    
    new_placed_orders = Order.query.filter_by(order_status='Placed').order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', 
                           orders=orders_list, 
                           current_status=status_filter,
                           current_payment=payment_filter,
                           new_placed_orders=new_placed_orders)

@app.route('/admin/orders/confirm-payment/<int:id>', methods=['POST'])
@admin_required
def admin_confirm_payment(id):
    order = Order.query.get_or_404(id)
    order.payment_status = 'Paid'
    if not order.upi_utr:
        order.upi_utr = f"CASH-COLLECTED-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
    db.session.commit()
    flash(f'Payment confirmed for Order #{order.order_number}! Marked as Paid (Cash Collected).', 'success')
    return redirect(request.referrer or url_for('admin_orders'))

@app.route('/admin/orders/reject-payment/<int:id>', methods=['POST'])
@admin_required
def admin_reject_payment(id):
    order = Order.query.get_or_404(id)
    order.payment_status = 'Payment Rejected'
    db.session.commit()
    flash(f'Payment for Order #{order.order_number} marked as Rejected/Not Received.', 'warning')
    return redirect(request.referrer or url_for('admin_orders'))

@app.route('/admin/orders/<int:id>')
@admin_required
def admin_order_detail(id):
    order = Order.query.get_or_404(id)
    return render_template('admin/order_detail.html', order=order)

@app.route('/admin/orders/update/<int:id>', methods=['POST'])
@admin_required
def admin_order_update(id):
    order = Order.query.get_or_404(id)
    order.order_status = request.form.get('order_status', order.order_status)
    order.payment_status = request.form.get('payment_status', order.payment_status)
    db.session.commit()
    flash(f'Order #{order.order_number} status updated!', 'success')
    return redirect(url_for('admin_order_detail', id=order.id))

@app.route('/admin/services')
@admin_required
def admin_services():
    inquiries = ServiceInquiry.query.order_by(ServiceInquiry.created_at.desc()).all()
    return render_template('admin/services.html', inquiries=inquiries)

@app.route('/admin/services/update/<int:id>', methods=['POST'])
@admin_required
def admin_service_update(id):
    inq = ServiceInquiry.query.get_or_404(id)
    inq.status = request.form.get('status', inq.status)
    db.session.commit()
    flash(f'Inquiry #{inq.id} updated.', 'success')
    return redirect(url_for('admin_services'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    if request.method == 'POST':
        opening_time = request.form.get('opening_time', '8:00 AM')
        closing_time = request.form.get('closing_time', '10:00 PM')
        shop_notice = request.form.get('shop_notice', '')
        StoreSetting.set_val('opening_time', opening_time)
        StoreSetting.set_val('closing_time', closing_time)
        StoreSetting.set_val('shop_notice', shop_notice)
        flash('Shop timings and settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    opening_time = StoreSetting.get_val('opening_time', '8:00 AM')
    closing_time = StoreSetting.get_val('closing_time', '10:00 PM')
    shop_notice = StoreSetting.get_val('shop_notice', '')
    return render_template('admin/settings.html', 
                           opening_time=opening_time, 
                           closing_time=closing_time, 
                           shop_notice=shop_notice)

@app.route('/track-order', methods=['GET', 'POST'])
def track_orders():
    searched = False
    orders_found = []
    query = request.args.get('q', '').strip()
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        
    if query:
        searched = True
        orders_found = Order.query.filter(
            (Order.order_number.ilike(f'%{query}%')) | 
            (Order.customer_phone.ilike(f'%{query}%'))
        ).order_by(Order.created_at.desc()).all()
    elif 'user_id' in session:
        return redirect(url_for('user_dashboard'))
        
    return render_template('track_order.html', searched=searched, orders=orders_found, query=query)

# Uploads file serving route
@app.route('/uploads/<path:subpath>')
def uploaded_file(subpath):
    return send_from_directory(app.config['UPLOAD_FOLDER'], subpath)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Starting Barsha Digital Gift E-Commerce Server on http://127.0.0.1:5000 ...")
    app.run(debug=True, host='0.0.0.0', port=5000)
