# ShopEasy — Professional Django E-commerce

## Run on Windows
```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_products
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Admin
```bat
python manage.py createsuperuser
```
Then open http://127.0.0.1:8000/admin/

## Features
- Professional responsive storefront
- Product search and sorting
- Product detail pages
- Session-based shopping cart
- Quantity update/remove
- Checkout and order creation
- Inventory reduction after order
- Django admin product/order management
- Demo products included via `seed_products`

Note: product images use remote Unsplash URLs, so internet access is needed for those images. Replace `image_url` values with your own images if desired.

Task Technology 
fastAPI(Python 3.13)
Native websockets
Modern vanilla JS+CSS3

Verification and test
Automated Integration Test Suite(test_taskflow.py)
Run command:
python test_taskflow.py

2.Live server verification 
