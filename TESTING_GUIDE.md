# Testing Guide for Cart Enhancements

## Pre-requisites
1. Database migrations applied: `python manage.py migrate`
2. Promo codes created: `python manage.py create_promo_codes`
3. Admin user created: `python manage.py createsuperuser`
4. Test user account created (via registration)

## Test Cases

### Test 1: Add Product to Cart
**Steps:**
1. Login as user
2. Go to product page
3. Click "Savatga qo'shish"
4. Go to cart

**Expected:**
- Product appears in cart
- Quantity is 1
- Unit price is correct (with product discount applied)
- Total for item is correct

---

### Test 2: Quantity Controls
**Steps:**
1. Add product to cart
2. Click `+` button multiple times
3. Verify total updates
4. Click `-` button
5. Verify total updates
6. Click `-` until quantity is 0

**Expected:**
- Quantity increases with each +
- Quantity decreases with each -
- Total price updates: `quantity × unit_price`
- Item removed when quantity reaches 0

---

### Test 3: Multiple Items in Cart
**Steps:**
1. Add 3 different products with different quantities
2. Go to cart
3. Verify subtotal = sum of all item totals

**Expected:**
- All items display correctly
- Cart subtotal matches: item1_total + item2_total + item3_total
- Each item shows correct individual total

---

### Test 4: Promo Code Application
**Steps:**
1. Add products to cart (total ~$100)
2. Enter promo code "WELCOME10"
3. Click "Qo'llash"
4. Check cart page

**Expected:**
- Message shows "Promo-kod qo'llanildi! 10% chegirma."
- Promo code displays as applied (if showing on cart)
- Checkout should show discount calculation

**Test Invalid Code:**
1. Try code "INVALID"
2. Click "Qo'llash"

**Expected:**
- Error message: "Promo-kod topilmadi yoki faol emas."

**Test Inactive Code:**
1. Try code "EXPIRED5"
2. Click "Qo'llash"

**Expected:**
- Error message: "Promo-kod topilmadi yoki faol emas."

---

### Test 5: Checkout from Cart
**Steps:**
1. Add products to cart
2. (Optional) Apply promo code
3. Click "Buyurtma berish"
4. Verify checkout page shows:
   - All items with quantities
   - Subtotal
   - Discount (if promo applied)
   - Final total
5. Enter address
6. Click "Buyurtmani tasdiqlash"

**Expected:**
- Checkout page displays all items
- Prices calculated correctly
- Order created successfully
- Redirected to order success page
- Cart cleared
- Order shows correct final price

---

### Test 6: Order Success Page
**Steps:**
1. Complete checkout
2. View order success page

**Expected:**
- Shows order status as "Yangi"
- Shows delivery address
- Shows promo code (or "Ishlatilmagan")
- Shows final price with discount applied
- Lists all order items with quantities

---

### Test 7: Admin Panel - Promo Codes
**Steps:**
1. Go to `/admin/`
2. Click "Promo Codes"
3. View all promo codes

**Expected:**
- All 6 sample codes visible
- Can edit codes (change discount, toggle active)
- Can create new codes
- Code is unique constraint

**Test Disabling Code:**
1. Edit "WELCOME10"
2. Uncheck "Active"
3. Save
4. Try using code in cart

**Expected:**
- Code no longer works
- Error: "Promo-kod topilmadi yoki faol emas."
- Can re-enable and it works again

---

### Test 8: Admin Panel - Orders
**Steps:**
1. Go to `/admin/`
2. Click "Orders"
3. View recent order

**Expected:**
- Order shows user, status, address
- Final price is correct with discount
- Promo code link visible
- Can filter by status
- Can see order items in inline

---

### Test 9: Admin Panel - Cart
**Steps:**
1. Go to `/admin/`
2. Click "Cards"
3. View user's cart

**Expected:**
- Shows user and total quantity
- Shows subtotal (sum of items)
- Can view cart items inline
- Each item shows product, quantity, and price

---

### Test 10: Admin Panel - Users
**Steps:**
1. Go to `/admin/`
2. Click "Custom Users"
3. View users

**Expected:**
- Shows type (admin/user/seller)
- Can filter by type
- Can search by username/email
- All fields editable

---

## Discount Calculation Verification

### Scenario 1: Product Discount Only
- Product: $100, discount 20%
- Quantity: 2
- Promo code: None

**Calculation:**
- Product discounted price: $100 × (100 - 20) / 100 = $80
- Item total: $80 × 2 = $160
- Cart total: $160

---

### Scenario 2: Product + Promo Discount
- Product: $100, discount 20%
- Quantity: 2
- Promo code: 10% (WELCOME10)

**Calculation:**
- Product discounted price: $100 × 80% = $80
- Item total: $80 × 2 = $160
- Subtotal: $160
- Promo discount: $160 × 10% = $16
- Final total: $160 - $16 = $144

---

### Scenario 3: Multiple Items + Promo
- Item 1: $50, no discount, quantity 1 = $50
- Item 2: $100, 20% discount, quantity 1 = $80
- Promo code: 15% (SAVE15)

**Calculation:**
- Subtotal: $50 + $80 = $130
- Promo discount: $130 × 15% = $19.50
- Final total: $130 - $19.50 = $110.50

---

## Possible Issues & Solutions

### Issue: "Savat bo'sh" error on checkout
**Solution:** Ensure products were added to cart and not deleted

### Issue: Promo code not applying
**Solution:** 
- Check code is active in admin
- Check code spelling (case-insensitive)
- Clear browser cache

### Issue: Quantity button not working
**Solution:**
- Check JavaScript console for errors
- Verify form submits correctly
- Check CSRF token present

### Issue: Order total incorrect
**Solution:**
- Check product discount in admin
- Verify promo code discount percentage
- Check OrderItem.total_price calculations

---

## SQL Queries for Verification

```sql
-- Check promo codes
SELECT * FROM orders_promocode;

-- Check cart items
SELECT c.user_id, ci.product_id, ci.quantity, ci.total_price 
FROM orders_card c
JOIN orders_carditem ci ON c.id = ci.card_id;

-- Check orders with discount
SELECT id, user_id, address, promo_code_id, finished_price 
FROM orders_order 
ORDER BY created_at DESC;

-- Check order items
SELECT oi.order_id, oi.product_id, oi.quantity, oi.total_price
FROM orders_orderitem oi
ORDER BY oi.order_id DESC;
```
