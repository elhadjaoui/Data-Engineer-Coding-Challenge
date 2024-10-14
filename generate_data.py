import random
from faker import Faker
import mysql.connector
from  mysql.connector import Error
from dotenv import load_dotenv
import os


fake = Faker()
load_dotenv()
def create_server_connection():
    """Create a connection to the MySQL server without specifying a database"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            # database=os.getenv('DEFAULT_DB')
        )
        print("MySQL Server connection successful")
        return connection
    except Error as err:
        print(f"Error: '{err}'")
        return None

def create_database(connection):
    """Create a new database."""
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
        print(f"Database '{os.getenv('DB_NAME')}' created successfully")
    except Error as err:
        print(f"Error: '{err}'")

def create_db_connection():
    """Create a connection to a specific database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        print(f"MySQL Database connection to '{os.getenv('DB_NAME')}' successful")
        return connection
    except Error as err:
        print(f"Error: '{err}'")
        return None

def create_tables(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            slug VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            country_id INT,
            FOREIGN KEY (country_id) REFERENCES countries (id)
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            slug VARCHAR(255) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            store_id INT,
            FOREIGN KEY (store_id) REFERENCES stores (id)
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(255) NOT NULL,  
            created_at DATETIME NOT NULL,
            store_id INT,
            FOREIGN KEY (store_id) REFERENCES stores (id)
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            order_id INT,
            product_id INT,
            quantity INT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            PRIMARY KEY (order_id, product_id)
        )''')

        conn.commit()
        print("Tables created successfully")
    except Error as err:
        print(f"Error: '{err}'")
        exit(1)

def generate_countries(conn, num_countries):
    cursor = conn.cursor()
    for _ in range(num_countries):
        name = fake.country()
        created_at = fake.date_time_between(start_date='-5y', end_date='now')
        cursor.execute('INSERT INTO countries (name, created_at) VALUES (%s, %s)', (name, created_at))
    conn.commit()

def generate_stores(conn, num_stores):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM countries')
    countries = cursor.fetchall()
    for _ in range(num_stores):
        slug = fake.slug()
        created_at = fake.date_time_between(start_date='-5y', end_date='now')
        country_id = random.choice(countries)[0]
        cursor.execute('INSERT INTO stores (slug, created_at, country_id) VALUES (%s, %s, %s)', (slug, created_at, country_id))
    conn.commit()

def generate_products(conn, num_products):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM stores')
    stores = cursor.fetchall()
    for _ in range(num_products):
        slug = fake.slug()
        price = round(random.uniform(1, 1000), 2)
        store_id = random.choice(stores)[0]
        cursor.execute('INSERT INTO products (slug, price, store_id) VALUES (%s, %s, %s)', (slug, price, store_id))
    conn.commit()

def generate_orders(conn, num_orders):
    cursor = conn.cursor()
    cursor.execute('SELECT id, created_at FROM stores')
    stores = cursor.fetchall()
    order_types = ['online', 'in-store', 'phone']
    
    for _ in range(num_orders):
        order_type = random.choice(order_types)
        store_id, store_created_at = random.choice(stores)
        created_at = fake.date_time_between(start_date=store_created_at, end_date='now')
        cursor.execute('INSERT INTO orders (type, created_at, store_id) VALUES (%s, %s, %s)', (order_type, created_at, store_id))
    conn.commit()

def generate_order_items(conn, avg_items_per_order):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM orders')
    orders = cursor.fetchall()
    cursor.execute('SELECT id FROM products')
    products = cursor.fetchall()
    
    for order in orders:
        num_items = random.randint(1, avg_items_per_order *2)
        for _ in range(num_items):
            product_id = random.choice(products)[0]
            quantity = random.randint(1, 5)
            try:
                cursor.execute('INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)', (order[0], product_id, quantity))
            except Error as err:
                print(f"Error: '{err}'")
                print(f"Order ID: {order[0]}, Product ID: {product_id}, Quantity: {quantity}")
    conn.commit()

def main():
    conn = create_server_connection()
    if conn is None:
        return
    create_database(conn)
    conn.close()
    
    db_conn = create_db_connection()
    if db_conn is None:
        return
    
    create_tables(db_conn)
    generate_countries(db_conn, 10)
    generate_stores(db_conn, 50)
    generate_products(db_conn, 1000)
    generate_orders(db_conn, 10000)
    generate_order_items(db_conn, 3)
    
    db_conn.close()

if __name__ == "__main__":
    main()