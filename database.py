import sqlite3
from sqlite3 import Error


def create_connection():
    """Create a database connection to SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('ecommerce.db')
        print(f"SQLite version: {sqlite3.version}")
        return conn
    except Error as e:
        print(e)

    return conn


def create_tables(conn):
    """Create all necessary tables"""
    try:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT,
            stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Cart table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """)
        # Orders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)

        # Order items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """)
        # Shipping address table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS shipping_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
        """)

        # Testimonials table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS testimonials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            rating INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Tables created successfully")
    except Error as e:
        print(e)


def initialize_database():
    """Initialize the database with sample data"""
    conn = create_connection()
    if conn is not None:
        create_tables(conn)

        # Insert sample products if they don't exist
        sample_products = [
            ("Smartphone X100", "Latest model with advanced features", 799.99, "Electronics",
             "https://storage.googleapis.com/a1aa/image/e9122a71-f7ae-4983-be74-89c260181c38.jpg", 50),
            ("Stylish Jacket", "Perfect for all seasons", 129.99, "Fashion",
             "https://storage.googleapis.com/a1aa/image/13d37277-88e5-42d5-0ea9-6f09aee26fb6.jpg", 30),
            ("Modern Lamp", "Brighten your home with style", 89.99, "Home Goods",
             "https://storage.googleapis.com/a1aa/image/181190f2-faf8-46e7-10db-9b25cf034c80.jpg", 20),
            ("Running Shoes", "Comfort and performance combined", 149.99, "Sports",
             "https://storage.googleapis.com/a1aa/image/b9488a2a-168c-41a2-e4ad-eec674e7e874.jpg", 40)
        ]

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.executemany("""
            INSERT INTO products (name, description, price, category, image_url, stock)
            VALUES (?, ?, ?, ?, ?, ?)
            """, sample_products)

            # Insert sample testimonials
            sample_testimonials = [
                ("John Doe", "Great products and fast delivery! Will shop here again.", 5),
                ("Jane Smith", "The quality exceeded my expectations. Highly recommended!", 5),
                ("Robert Johnson", "Good prices but shipping took longer than expected.", 4),
                ("Emily Davis", "Excellent customer service and easy returns.", 5),
                ("Michael Brown", "Products are good but could have more variety.", 4)
            ]

            cursor.executemany("""
            INSERT INTO testimonials (author, content, rating)
            VALUES (?, ?, ?)
            """, sample_testimonials)

            conn.commit()
            print("Sample data inserted successfully")

        conn.close()
    else:
        print("Error: Cannot create database connection")


if __name__ == '__main__':
    initialize_database()