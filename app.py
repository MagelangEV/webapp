from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
from database import create_connection
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this for production


# Initialize database
def get_db_connection():
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()

    # Get featured products
    products = conn.execute('SELECT * FROM products LIMIT 4').fetchall()

    # Get testimonials
    testimonials = conn.execute('SELECT * FROM testimonials').fetchall()

    # Get cart count for logged in users
    cart_count = 0
    if 'user_id' in session:
        cart_count = conn.execute('SELECT COUNT(*) FROM cart WHERE user_id = ?',
                                  (session['user_id'],)).fetchone()[0]

    conn.close()

    return render_template('index.html',
                           products=products,
                           testimonials=testimonials,
                           cart_count=cart_count)


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # In a real app, you would verify credentials properly
        # For demo, we'll just set a session
        session['user_id'] = 1  # Assuming user with ID 1 exists
        return jsonify({'success': True, 'message': 'Logged in successfully'})


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    conn = get_db_connection()

    # Check if product exists
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        conn.close()
        return jsonify({'success': False, 'message': 'Product not found'})

    # Check if product is already in cart
    cart_item = conn.execute('SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
                             (session['user_id'], product_id)).fetchone()

    if cart_item:
        # Update quantity
        new_quantity = cart_item['quantity'] + quantity
        conn.execute('UPDATE cart SET quantity = ? WHERE id = ?',
                     (new_quantity, cart_item['id']))
    else:
        # Add new item to cart
        conn.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
                     (session['user_id'], product_id, quantity))

    conn.commit()

    # Get updated cart count
    cart_count = conn.execute('SELECT COUNT(*) FROM cart WHERE user_id = ?',
                              (session['user_id'],)).fetchone()[0]

    conn.close()

    return jsonify({
        'success': True,
        'message': 'Product added to cart',
        'cart_count': cart_count
    })


@app.route('/get_cart')
def get_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    conn = get_db_connection()

    cart_items = conn.execute('''
        SELECT p.id, p.name, p.price, p.image_url, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (session['user_id'],)).fetchall()

    total = 0
    items = []
    for item in cart_items:
        item_total = item['price'] * item['quantity']
        total += item_total
        items.append({
            'id': item['id'],
            'name': item['name'],
            'price': item['price'],
            'image_url': item['image_url'],
            'quantity': item['quantity'],
            'total': item_total
        })

    conn.close()

    return jsonify({
        'success': True,
        'items': items,
        'total': total
    })


@app.route('/submit_question', methods=['POST'])
def submit_question():
    question = request.form.get('question')
    if not question:
        return jsonify({'success': False, 'message': 'Question is required'})

    # In a real app, you would save this to database or send to WhatsApp
    print(f"New question received: {question}")

    return jsonify({
        'success': True,
        'message': 'Your question has been submitted. We will contact you soon.'
    })


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    data = request.get_json()
    product_id = data.get('product_id')

    conn = get_db_connection()

    # Delete the item from cart
    conn.execute('DELETE FROM cart WHERE user_id = ? AND product_id = ?',
                 (session['user_id'], product_id))
    conn.commit()

    # Get updated cart count
    cart_count = conn.execute('SELECT COUNT(*) FROM cart WHERE user_id = ?',
                              (session['user_id'],)).fetchone()[0]

    conn.close()

    return jsonify({
        'success': True,
        'message': 'Product removed from cart',
        'cart_count': cart_count
    })


@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    data = request.get_json()
    shipping_data = data.get('shipping_address', {})

    # Validasi data pengiriman
    if not all([shipping_data.get('full_name'), shipping_data.get('phone'), shipping_data.get('address')]):
        return jsonify({'success': False, 'message': 'Shipping information is incomplete'})

    conn = get_db_connection()

    # 1. Validasi cart tidak kosong
    cart_items = conn.execute('''
        SELECT p.id, p.name, p.price, p.stock, c.quantity 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ?
    ''', (session['user_id'],)).fetchall()

    if not cart_items:
        conn.close()
        return jsonify({'success': False, 'message': 'Your cart is empty'})

    # 2. Validasi stok produk
    out_of_stock = []
    for item in cart_items:
        if item['stock'] < item['quantity']:
            out_of_stock.append(item['name'])

    if out_of_stock:
        conn.close()
        return jsonify({
            'success': False,
            'message': f'Some items are out of stock: {", ".join(out_of_stock)}'
        })

    try:
        # 3. Buat order
        order_total = sum(item['price'] * item['quantity'] for item in cart_items)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (user_id, total, status) 
            VALUES (?, ?, ?)
        ''', (session['user_id'], order_total, 'pending'))
        order_id = cursor.lastrowid

        # 4. Tambahkan order items
        for item in cart_items:
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (order_id, item['id'], item['quantity'], item['price']))

            # Kurangi stok
            cursor.execute('''
                UPDATE products SET stock = stock - ? WHERE id = ?
            ''', (item['quantity'], item['id']))

        # 5. Kosongkan cart
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (session['user_id'],))

        # Simpan alamat pengiriman
        cursor.execute('''
                    INSERT INTO shipping_addresses (user_id, order_id, full_name, phone, address)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session['user_id'], order_id,
                      shipping_data['full_name'],
                      shipping_data['phone'],
                      shipping_data['address']))

        conn.commit()
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order_id': order_id,
            'cart_count': 0
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()


@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    conn = get_db_connection()
    conn.execute('DELETE FROM cart WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Cart cleared successfully',
        'cart_count': 0
    })


@app.route('/get_order_details')
def get_order_details():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    order_id = request.args.get('order_id')
    if not order_id:
        return jsonify({'success': False, 'message': 'Order ID is required'})

    conn = get_db_connection()

    try:
        order = conn.execute('''
            SELECT id, total, created_at 
            FROM orders 
            WHERE id = ? AND user_id = ?
        ''', (order_id, session['user_id'])).fetchone()

        if not order:
            return jsonify({'success': False, 'message': 'Order not found'})

        items = conn.execute('''
            SELECT p.name, oi.quantity, oi.price 
            FROM order_items oi 
            JOIN products p ON oi.product_id = p.id 
            WHERE oi.order_id = ?
        ''', (order_id,)).fetchall()

        shipping_address = conn.execute('''
            SELECT full_name, phone, address 
            FROM shipping_addresses 
            WHERE order_id = ?
        ''', (order_id,)).fetchone()

        return jsonify({
            'success': True,
            'order': dict(order),
            'items': [dict(item) for item in items],
            'shipping_address': dict(shipping_address) if shipping_address else None
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

#Alamat Pengiriman
@app.route('/save_shipping_address', methods=['POST'])
def save_shipping_address():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    data = request.get_json()
    order_id = data.get('order_id')
    full_name = data.get('full_name')
    phone = data.get('phone')
    address = data.get('address')

    if not all([order_id, full_name, phone, address]):
        return jsonify({'success': False, 'message': 'All fields are required'})

    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO shipping_addresses (user_id, order_id, full_name, phone, address)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], order_id, full_name, phone, address))
        conn.commit()
        return jsonify({'success': True, 'message': 'Shipping address saved'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)