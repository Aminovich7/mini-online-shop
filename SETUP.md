# Mini Online Shop - Setup Instructions

## Creating Sample Promo Codes

To create sample promo codes for testing, run the following management command:

```bash
python manage.py create_promo_codes
```

This will create the following promo codes:
- **WELCOME10** - 10% discount
- **SUMMER20** - 20% discount
- **SAVE15** - 15% discount
- **NEWYEAR25** - 25% discount
- **SPECIAL30** - 30% discount
- **EXPIRED5** - 5% discount (inactive for testing)

## Features

### Cart Management
- Add products to cart
- Increase/decrease product quantity
- Remove products from cart
- Auto-calculate total price for each item
- Auto-calculate total for entire cart

### Promo Codes
- Apply promo codes to cart
- View discount amount
- Promo codes are case-insensitive
- Only active promo codes can be applied

### Place Order from Cart
- Click "Buyurtma berish" to place order
- Enter delivery address
- Apply promo code before checkout
- View order summary with breakdown

### Admin Panel
- Full CRUD operations for all models
- Category, Product, ProductImage management
- User management
- Order and Order Item tracking
- Promo Code management

## Database Commands

Migrate the database:
```bash
python manage.py migrate
```

Create superuser:
```bash
python manage.py createsuperuser
```

Access admin:
```
http://127.0.0.1:8000/admin/
```
