from app import app
from models import db, User, Category, Product, ServiceInquiry

def seed():
    with app.app_context():
        db.create_all()

        # 1. Admin User
        admin = User.query.filter_by(email="admin@barshagift.com").first()
        if not admin:
            admin = User(
                name="Barsha Admin",
                email="admin@barshagift.com",
                phone="8513010387",
                address="Sahapur, Kolaghat",
                city="Kolaghat",
                pincode="721134",
                is_admin=True
            )
            admin.set_password("admin123")
            db.session.add(admin)
            print("Created Admin: admin@barshagift.com / admin123")

        # 2. Demo Customer User
        customer = User.query.filter_by(email="customer@example.com").first()
        if not customer:
            customer = User(
                name="Rahul Mondal",
                email="customer@example.com",
                phone="9832725105",
                address="Near Kolaghat Thermal Gate, Kolaghat",
                city="Kolaghat",
                pincode="721134",
                is_admin=False
            )
            customer.set_password("customer123")
            db.session.add(customer)
            print("Created Demo Customer: customer@example.com / customer123")

        # 3. Categories
        categories_data = [
            {
                "name": "Customized Mugs",
                "slug": "custom-mugs",
                "description": "Ceramic photo mugs, magic color changing mugs, inner color mugs & travel mugs.",
                "icon": "bi-cup-hot-fill",
                "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80",
                "is_service": False,
                "display_order": 1
            },
            {
                "name": "Custom T-Shirts",
                "slug": "custom-tshirts",
                "description": "High quality 100% cotton T-shirts with vibrant DTF / sublimation print.",
                "icon": "bi-person-fill",
                "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80",
                "is_service": False,
                "display_order": 2
            },
            {
                "name": "Photo Frames & Stones",
                "slug": "frames-and-stones",
                "description": "Sublimation glossy rock stones, wooden frames, LED frames & acrylic plaques.",
                "icon": "bi-image-fill",
                "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=600&q=80",
                "is_service": False,
                "display_order": 3
            },
            {
                "name": "Keychains & Watches",
                "slug": "keychains-watches",
                "description": "Personalized wooden/metal keyrings and wall/desk clocks with custom photos.",
                "icon": "bi-key-fill",
                "image_url": "https://images.unsplash.com/photo-1582255334460-7053075253fa?auto=format&fit=crop&w=600&q=80",
                "is_service": False,
                "display_order": 4
            },
            {
                "name": "Photo Tiles & Cushions",
                "slug": "tiles-cushions",
                "description": "Glossy ceramic tiles with easel stand & custom magic sequin cushions.",
                "icon": "bi-grid-3x3-gap-fill",
                "image_url": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?auto=format&fit=crop&w=600&q=80",
                "is_service": False,
                "display_order": 5
            },
            {
                "name": "Commercial Printing Services",
                "slug": "printing-services",
                "description": "Flex banners, vinyl stickers, visiting cards, spiral binding, and menu cards.",
                "icon": "bi-printer-fill",
                "image_url": "https://images.unsplash.com/photo-1562654501-a0ccc0fc3fb1?auto=format&fit=crop&w=600&q=80",
                "is_service": True,
                "display_order": 6
            }
        ]

        cat_objs = {}
        for cdata in categories_data:
            cat = Category.query.filter_by(slug=cdata["slug"]).first()
            if not cat:
                cat = Category(**cdata)
                db.session.add(cat)
                db.session.flush()
            cat_objs[cdata["slug"]] = cat

        # 4. Products
        products_data = [
            {
                "name": "Personalized Ceramic Coffee Mug",
                "slug": "personalized-ceramic-coffee-mug",
                "category_id": cat_objs["custom-mugs"].id,
                "description": "Premium 325ml white ceramic mug with 360-degree high resolution photo and custom message printing. Microwave and dishwasher safe.",
                "price": 250.0,
                "discount_price": 199.0,
                "stock": 100,
                "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload 1 or 2 high resolution photos and enter the name or wish.",
                "is_featured": True
            },
            {
                "name": "Magic Heat-Sensitive Color Changing Mug",
                "slug": "magic-heat-sensitive-mug",
                "category_id": cat_objs["custom-mugs"].id,
                "description": "Black matte mug that reveals your secret photo and custom message when hot liquid is poured into it! The ultimate surprise gift.",
                "price": 450.0,
                "discount_price": 349.0,
                "stock": 60,
                "image_url": "https://images.unsplash.com/photo-1577937927133-66ef06acdf18?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload the surprise photo and optional love/birthday note.",
                "is_featured": True
            },
            {
                "name": "Custom Printed Round Neck Cotton T-Shirt",
                "slug": "custom-printed-round-neck-tshirt",
                "category_id": cat_objs["custom-tshirts"].id,
                "description": "180 GSM breathable combed cotton t-shirt with HD DTF color print. Available in White, Black, Navy, and Maroon. Perfect for birthdays, couples, and team events.",
                "price": 499.0,
                "discount_price": 399.0,
                "stock": 80,
                "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Specify size (S, M, L, XL, XXL), color, and upload front/back design.",
                "is_featured": True
            },
            {
                "name": "Couple Special Matching Printed T-Shirts (Pack of 2)",
                "slug": "couple-matching-tshirts-pack-2",
                "category_id": cat_objs["custom-tshirts"].id,
                "description": "Celebrate love and anniversaries with matching King & Queen / Hubby & Wifey customized graphic tees.",
                "price": 899.0,
                "discount_price": 699.0,
                "stock": 40,
                "image_url": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Enter names, anniversary date, and sizes for both.",
                "is_featured": False
            },
            {
                "name": "Sublimation Natural Rock Stone Photo Slate",
                "slug": "natural-rock-stone-photo-slate",
                "category_id": cat_objs["frames-and-stones"].id,
                "description": "Genuine natural slate stone with polished chiseled edges and high gloss permanent photo sublimation. Includes two tabletop display stands.",
                "price": 650.0,
                "discount_price": 499.0,
                "stock": 35,
                "image_url": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload portrait or landscape photo for HD stone printing.",
                "is_featured": True
            },
            {
                "name": "Designer Collage Wooden Photo Frame (12x18 inch)",
                "slug": "designer-collage-wooden-photo-frame",
                "category_id": cat_objs["frames-and-stones"].id,
                "description": "Elegant textured matte wooden frame with 6-8 photos collage design and personalized family name or celebration quote.",
                "price": 850.0,
                "discount_price": 599.0,
                "stock": 45,
                "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload zip or multiple pictures and title text.",
                "is_featured": True
            },
            {
                "name": "Personalized Wall Clock with Family Photos",
                "slug": "personalized-wall-clock-photos",
                "category_id": cat_objs["keychains-watches"].id,
                "description": "12-inch circular designer silent sweep clock featuring custom 12 photos or one centerpiece family portrait with numbers.",
                "price": 799.0,
                "discount_price": 549.0,
                "stock": 30,
                "image_url": "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload your centerpiece photo or multiple pictures for hour positions.",
                "is_featured": True
            },
            {
                "name": "Engraved Acrylic & Wooden Keychain (Double Sided)",
                "slug": "engraved-acrylic-wooden-keychain",
                "category_id": cat_objs["keychains-watches"].id,
                "description": "Laser-cut durable acrylic or solid beech wood keyring with photo on one side and vehicle number/name on the reverse.",
                "price": 180.0,
                "discount_price": 120.0,
                "stock": 150,
                "image_url": "https://images.unsplash.com/photo-1582255334460-7053075253fa?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload photo and specify name or vehicle registration number.",
                "is_featured": True
            },
            {
                "name": "Ceramic Glossy Photo Tile (6x6 inch with Easel)",
                "slug": "ceramic-glossy-photo-tile",
                "category_id": cat_objs["tiles-cushions"].id,
                "description": "Waterproof scratch-resistant high gloss ceramic tile print. Comes with a black display stand. Great for desk, shrine, or showcase.",
                "price": 350.0,
                "discount_price": 249.0,
                "stock": 50,
                "image_url": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload your high-res square or cropped picture.",
                "is_featured": False
            },
            {
                "name": "Custom Magic Sequin Reversible Photo Cushion",
                "slug": "custom-magic-sequin-cushion",
                "category_id": cat_objs["tiles-cushions"].id,
                "description": "Heart or square shaped cushion with shiny sequins. Swipe hand in one direction to reveal hidden photo, swipe back to hide it!",
                "price": 599.0,
                "discount_price": 449.0,
                "stock": 40,
                "image_url": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload photo to print on the magic sequin surface.",
                "is_featured": True
            },
            # Commercial printing services
            {
                "name": "Business Visiting Cards Printing (Pack of 500)",
                "slug": "business-visiting-cards-500",
                "category_id": cat_objs["printing-services"].id,
                "description": "350 GSM premium art card with velvet matte or glossy lamination. Sharp digital offset print. Free basic card designing included.",
                "price": 750.0,
                "discount_price": 550.0,
                "stock": 999,
                "image_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload your logo/card file or enter shop name, phone, address, and tagline.",
                "is_featured": True
            },
            {
                "name": "Flex Banner & Hoarding Printing (Per Sq. Ft)",
                "slug": "flex-banner-printing-sqft",
                "category_id": cat_objs["printing-services"].id,
                "description": "Normal, Star, and Blackout flex printing with eyelets (rings) for shops, events, elections, and road signs in Kolaghat & East Medinipur.",
                "price": 18.0,
                "discount_price": 14.0,
                "stock": 9999,
                "image_url": "https://images.unsplash.com/photo-1562654501-a0ccc0fc3fb1?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Specify size in feet (e.g., 6ft x 3ft) and upload your design or banner text.",
                "is_featured": True
            },
            {
                "name": "Vinyl Stickers & Die-Cut Product Labels (100 pcs)",
                "slug": "vinyl-stickers-diecut-labels-100",
                "category_id": cat_objs["printing-services"].id,
                "description": "Waterproof, UV-resistant vinyl stickers cut to exact shapes (round, square, or contour) for bottle packaging, laptops, vehicles, and boxes.",
                "price": 400.0,
                "discount_price": 299.0,
                "stock": 999,
                "image_url": "https://images.unsplash.com/photo-1572375992501-4b0892d50c69?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload label logo file and specify dimension (e.g. 2 inch x 2 inch).",
                "is_featured": False
            },
            {
                "name": "Spiral & Wire-O Book Binding Service",
                "slug": "spiral-binding-service",
                "category_id": cat_objs["printing-services"].id,
                "description": "Professional spiral binding with transparent front OHP sheet and durable back sheet for project reports, study materials, and office registers.",
                "price": 60.0,
                "discount_price": 45.0,
                "stock": 999,
                "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80",
                "is_customizable": True,
                "allow_photo_upload": True,
                "allow_text_customization": True,
                "customization_help_text": "Upload your PDF document to print and bind, or specify number of pages.",
                "is_featured": False
            }
        ]

        for pdata in products_data:
            prod = Product.query.filter_by(slug=pdata["slug"]).first()
            if not prod:
                prod = Product(**pdata)
                db.session.add(prod)

        db.session.commit()
        print("Database successfully seeded with Barsha Digital Gift categories, products, and accounts!")

if __name__ == "__main__":
    seed()
