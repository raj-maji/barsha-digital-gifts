# 🚀 100% Free Hosting & Payment Gateway Deployment Guide
### Barsha Digital Gift — Sahapur, Kolaghat, East Medinipur
**Contact**: 8513010387 || 9832725105

---

## 1. Quick Local Setup & Run

### Step 1: Open Terminal in Project Folder
```bash
cd "C:\Users\YUVARAJ MAJI\.gemini\antigravity\scratch\barsha_digital_gift"
```

### Step 2: Seed the Database with Products & Accounts
```bash
python seed_data.py
```
This automatically sets up:
- **Admin Account**: `admin@barshagift.com` / `admin123`
- **Customer Account**: `customer@example.com` / `customer123`
- Pre-loaded products: Custom Mugs, T-shirts, Rock Stones, Photo Frames, Wall Clocks, Keychains, Tiles, Cushions, Visiting Cards, Flex Banners, and Spiral Binding.

### Step 3: Start the Flask App
```bash
python app.py
```
Open your browser at: **`http://127.0.0.1:5000`**

---

## 2. Deploy 100% Free on Render.com (Recommended)

[Render.com](https://render.com) provides a free cloud hosting tier for Python web applications with automatic HTTPS (SSL certificate) and free deployment directly from GitHub.

### Step A: Push Code to GitHub
1. Create a free account at [github.com](https://github.com).
2. Create a new repository named `barsha-digital-gift`.
3. In your project directory on your computer, run:
```bash
git init
git add .
git commit -m "Initial commit for Barsha Digital Gift"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/barsha-digital-gift.git
git push -u origin main
```

### Step B: Launch Web Service on Render
1. Go to [dashboard.render.com](https://dashboard.render.com) and sign in with GitHub (Free).
2. Click **New +** &rarr; Select **Web Service**.
3. Choose your `barsha-digital-gift` repository.
4. Fill in the settings:
   - **Name**: `barsha-digital-gift`
   - **Region**: Singapore or Frankfurt (fastest for India)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python seed_data.py`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Select **Free**
5. Under **Environment Variables**, add:
   - `SECRET_KEY`: any secure random string
   - `SHOP_UPI_ID`: `8513010387@ybl` (or your preferred PhonePe/GPay UPI ID)
   - `RAZORPAY_KEY_ID`: your Razorpay key
   - `RAZORPAY_KEY_SECRET`: your Razorpay secret
6. Click **Create Web Service**.
7. In 2-3 minutes, your store will be live on: `https://barsha-digital-gift.onrender.com`!

---

## 3. Alternative 100% Free Hosting: PythonAnywhere.com

[PythonAnywhere](https://www.pythonanywhere.com/) provides a permanent 100% free hosting plan for Python Flask apps:
1. Sign up for a free Beginner account at [pythonanywhere.com](https://www.pythonanywhere.com/).
2. Go to the **Web** tab &rarr; Click **Add a new web app**.
3. Select **Flask** and choose **Python 3.10 / 3.11**.
4. Go to **Files** tab and upload your project zip file, then extract it into your home directory.
5. In the **WSGI configuration file**, point to your `app.py`:
   ```python
   import sys
   path = '/home/yourusername/barsha_digital_gift'
   if path not in sys.path:
       sys.path.append(path)
   from app import app as application
   ```
6. Click **Reload** and your site will be live at `https://yourusername.pythonanywhere.com` with free HTTPS!

---

## 4. Setting Up Free Online Payment Gateways

### Method A: Zero-Cost Instant UPI QR Code (Active by Default)
- **Cost**: ₹0 setup fee, ₹0 annual fee, **0% transaction charges**.
- **How it works**:
  1. Whenever a customer places an order, the website automatically creates a dynamic QR code pre-filled with the exact order amount and your UPI ID (`8513010387@ybl`).
  2. The customer scans it with **Google Pay, PhonePe, Paytm, BHIM, or any bank app**.
  3. The payment is transferred directly to your bank account immediately with no middleman cut.
  4. The customer submits their 12-digit UTR reference number or screenshot.
  5. In your **Admin Panel** (`/admin/orders`), you verify the UTR with your bank message and click **"Verified"**!

### Method B: Razorpay Online Payment Gateway (For Cards & Netbanking)
- **Cost**: ₹0 setup fee, ₹0 annual maintenance fee (Razorpay charges only ~2% per transaction when a customer pays via credit/debit card).
- **How to get your free API Keys**:
  1. Go to [razorpay.com](https://razorpay.com) and click **Sign Up** (Free).
  2. Go to **Settings** &rarr; **API Keys** &rarr; Click **Generate Test Key**.
  3. Copy your `Key ID` and `Key Secret`.
  4. Put them into your `config.py` or Render Environment Variables:
     - `RAZORPAY_KEY_ID = "rzp_test_..."`
     - `RAZORPAY_KEY_SECRET = "..."`
  5. Once you complete free KYC with your Aadhaar/PAN and bank account details, switch to **Live Key** to accept real customer cards!

---

## 5. Using the Dashboards

### 👑 Admin Dashboard (`/admin`):
- **Login**: `admin@barshagift.com` / `admin123`
- **Features**:
  - **Product Catalog**: Add new photo mugs, t-shirts, stones, frames, or update prices and stock.
  - **Order Workflow**: Inspect customer-uploaded photos, download high-resolution files, and change order progress from **"Placed"** &rarr; **"In Printing"** &rarr; **"Shipped"** &rarr; **"Delivered"**.
  - **Printing Leads**: Manage commercial quote requests for Flex banners, visiting cards, vinyl stickers, and spiral binding.
  - **Quick Contact**: 1-click button to call or WhatsApp customer with their prefilled order summary.

### 👤 Customer Portal (`/user/dashboard`):
- Customers can log in, view live milestone progress of their printing jobs, download tax receipts, inspect their uploaded custom design files, and directly communicate with the shop over WhatsApp.
