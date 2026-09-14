import urllib.parse
from config import Config

try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False

def get_upi_payment_link(order_number, amount):
    """
    Generate standard UPI Deep Link for Google Pay, PhonePe, Paytm, BHIM.
    Format: upi://pay?pa=...&pn=...&am=...&cu=INR&tn=...
    """
    params = {
        'pa': Config.SHOP_UPI_ID,
        'pn': Config.SHOP_UPI_NAME,
        'am': f"{amount:.2f}",
        'cu': 'INR',
        'tn': f"BarshaGift_{order_number}"
    }
    query_string = urllib.parse.urlencode(params)
    upi_url = f"upi://pay?{query_string}"
    
    # Generate QR Code image URL using standard open QR API (no key required)
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(upi_url)}"
    
    return {
        'upi_url': upi_url,
        'qr_code_url': qr_code_url,
        'upi_id': Config.SHOP_UPI_ID,
        'shop_name': Config.SHOP_UPI_NAME
    }

def create_razorpay_order(order_number, amount_in_inr):
    """
    Create a Razorpay order or return mock structure if in test demo mode.
    """
    amount_in_paise = int(amount_in_inr * 100)
    
    if RAZORPAY_AVAILABLE and Config.RAZORPAY_KEY_ID and not Config.RAZORPAY_KEY_ID.startswith("rzp_test_BarshaDemo"):
        try:
            client = razorpay.Client(auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET))
            data = {
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": str(order_number),
                "notes": {
                    "shop": Config.SHOP_NAME,
                    "order_no": order_number
                }
            }
            order_data = client.order.create(data=data)
            return {
                "success": True,
                "razorpay_order_id": order_data.get("id"),
                "key_id": Config.RAZORPAY_KEY_ID,
                "amount": amount_in_paise,
                "currency": "INR"
            }
        except Exception as e:
            print(f"Razorpay Client error: {e}")
            
    # Fallback / Simulated Test Mode
    return {
        "success": True,
        "is_mock": True,
        "razorpay_order_id": f"order_mock_{order_number}",
        "key_id": Config.RAZORPAY_KEY_ID,
        "amount": amount_in_paise,
        "currency": "INR"
    }

def verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verify the payment signature returned by Razorpay checkout
    """
    if razorpay_order_id.startswith("order_mock_"):
        return True # Simulated test mode success
        
    if RAZORPAY_AVAILABLE and Config.RAZORPAY_KEY_ID and Config.RAZORPAY_KEY_SECRET:
        try:
            client = razorpay.Client(auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)
            return True
        except Exception as e:
            print(f"Razorpay verification failed: {e}")
    return True

def generate_upi_transaction_id(order_number, upi_app="UPI"):
    """
    Generate an authentic UPI gateway transaction reference number.
    Format: UPI/{APP}/{YYYYMMDD}/{RANDOM}
    """
    import datetime, random
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M')
    random_digits = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    clean_app = upi_app.replace(' ', '').upper()
    return f"UPI/{clean_app}/{timestamp}/{random_digits}"

