# Mini Online Shop

An online shop built with Django templates, with separate buyer and seller accounts, a shopping cart with promo codes, and order checkout.

## Features

- Buyer and seller registration, login, profile and logout (custom user model)
- Product catalogue with categories, multiple images per product, comments, likes and saved items
- Seller dashboard to create, edit and delete their own products
- Cart: add, update quantity, remove, live totals
- Promo codes (percentage discounts, active/inactive) applied at checkout
- Checkout with delivery address, order confirmation and order history
- Django admin for all models

## Stack

Python, Django (class-based views, ModelForms, custom user model, custom management commands), SQLite, Pillow.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_products        # sample catalogue (150 products; downloads images)
python manage.py create_promo_codes   # sample promo codes
python manage.py runserver
```

More detail: [SETUP.md](SETUP.md), [CART_ENHANCEMENTS.md](CART_ENHANCEMENTS.md), [TESTING_GUIDE.md](TESTING_GUIDE.md).

## Configuration

`SECRET_KEY` and `DEBUG` are read from environment variables (see `.env.example`). If they are not set, the project falls back to development defaults, so it runs locally out of the box.

| Variable | Default |
|---|---|
| `DJANGO_SECRET_KEY` | a development-only key |
| `DJANGO_DEBUG` | `True` |
