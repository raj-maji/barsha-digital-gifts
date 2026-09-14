import unittest
from app import app
from models import db, User, Product, Order, Category

class BarshaDigitalGiftTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_public_pages(self):
        # Home page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Barsha Digital Gift', response.data)
        self.assertIn(b'8513010387', response.data)
        self.assertIn(b'Kolaghat', response.data)

        # Products page
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Personalized Ceramic Coffee Mug', response.data)

        # Product detail page
        response = self.client.get('/product/personalized-ceramic-coffee-mug')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Personalize Your Item', response.data)

        # Track order page
        response = self.client.get('/track-order')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Track Your Order', response.data)

    def test_02_cart_and_checkout_flow(self):
        with app.app_context():
            prod = Product.query.filter_by(slug='personalized-ceramic-coffee-mug').first()
            prod_id = prod.id

        # 1. Add customized item to cart
        post_data = {
            'product_id': prod_id,
            'quantity': 2,
            'custom_text': 'Happy Birthday Priya',
            'custom_notes': 'Print on both sides'
        }
        res = self.client.post('/cart/add', data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Happy Birthday Priya', res.data)

        # 2. Checkout via Cash on Delivery
        checkout_data = {
            'name': 'Test Buyer',
            'phone': '9876543210',
            'email': 'buyer@example.com',
            'address': 'Near Bus Stand, Sahapur',
            'city': 'Kolaghat',
            'pincode': '721134',
            'order_notes': 'Please pack nicely',
            'payment_method': 'cod'
        }
        res = self.client.post('/checkout', data=checkout_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Order Placed Successfully', res.data)
        self.assertIn(b'Cash on Delivery', res.data)

        # 3. Extract order from database and verify COD attributes
        with app.app_context():
            order = Order.query.filter_by(customer_email='buyer@example.com').order_by(Order.created_at.desc()).first()
            self.assertIsNotNone(order)
            self.assertEqual(order.payment_method, 'Cash on Delivery (COD)')
            self.assertEqual(order.payment_status, 'Pending')
            self.assertEqual(order.order_status, 'Placed')
            order_no = order.order_number
            order_id = order.id

        # 4. Customer order confirmation page renders with COD details
        res = self.client.get(f'/order/success/{order_no}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Cash on Delivery (COD)', res.data)

        # 5. Admin logs in and marks cash as collected / paid
        self.client.post('/login', data={'email': 'admin@barshagift.com', 'password': 'admin123'}, follow_redirects=True)
        admin_res = self.client.post(f'/admin/orders/confirm-payment/{order_id}', follow_redirects=True)
        self.assertEqual(admin_res.status_code, 200)
        self.assertIn(b'Marked as Paid (Cash Collected)', admin_res.data)

        # 6. Verify order in DB is now Paid
        with app.app_context():
            final_order = Order.query.filter_by(order_number=order_no).first()
            self.assertEqual(final_order.payment_status, 'Paid')

        # 7. Customer can see Cash Collected on the invoice / order confirmation
        res = self.client.get(f'/order/success/{order_no}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Paid (Cash Collected)', res.data)

    def test_03_admin_workflow(self):
        # 1. Login as Admin
        login_data = {
            'email': 'admin@barshagift.com',
            'password': 'admin123'
        }
        res = self.client.post('/login', data=login_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Admin Overview', res.data)

        # 2. Access Admin Products
        res = self.client.get('/admin/products')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Product Inventory', res.data)

        # 3. Add a new Product via Admin
        with app.app_context():
            cat = Category.query.first()
            cat_id = cat.id

        new_prod_data = {
            'name': 'LED Light Customized Wooden Frame',
            'category_id': cat_id,
            'price': '999',
            'discount_price': '799',
            'stock': '25',
            'description': 'Warm LED backlight wooden frame for anniversary and couple gifts.',
            'is_customizable': 'on',
            'is_featured': 'on',
            'customization_help_text': 'Upload high res couple portrait'
        }
        res = self.client.post('/admin/products/new', data=new_prod_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'successfully added', res.data)

        # 4. View Admin Orders
        res = self.client.get('/admin/orders')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Customer Orders &amp; Print Jobs', res.data)

if __name__ == '__main__':
    unittest.main()
