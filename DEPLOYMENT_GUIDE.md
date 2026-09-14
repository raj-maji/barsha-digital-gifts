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
5. Under **Environment Variables** (Optional):
   - `SECRET_KEY`: any secure random string (e.g. `barsha-secure-key-2026`)
6. Click **Create Web Service**.
7. In 2-3 minutes, your store will be live on: `https://barsha-digital-gifts.onrender.com`!

---

## 3. Payment Mode: 100% Cash on Delivery (COD) / Pay at Shop
- No online payment gateway registration, KYC, or gateway fees required!
- Customers select Cash on Delivery, provide their delivery address, and confirm their order.
- In your **Admin Panel** (`/admin/orders`), you review the customized print files, prepare the items, and click **"Mark Cash Collected"** upon delivery or shop pickup.

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
