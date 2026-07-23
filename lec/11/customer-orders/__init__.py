import check50
import sqlite3
import csv
import os


def setup_db():
    check50.include("CUSTOMERS.csv", "ORDERS.csv")
    conn = sqlite3.connect("store.db")
    conn.execute("DROP TABLE IF EXISTS CUSTOMERS")
    conn.execute("DROP TABLE IF EXISTS ORDERS")
    
    conn.execute("""CREATE TABLE CUSTOMERS (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        age INTEGER,
        country TEXT
    )""")
    
    conn.execute("""CREATE TABLE ORDERS (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        amount REAL,
        item TEXT
    )""")
    
    with open("CUSTOMERS.csv") as f:
        conn.executemany(
            "INSERT INTO CUSTOMERS VALUES (?,?,?,?,?)",
            [(int(r["customer_id"]), r["first_name"], r["last_name"], int(r["age"]), r["country"])
             for r in csv.DictReader(f)]
        )
        
    with open("ORDERS.csv") as f:
        conn.executemany(
            "INSERT INTO ORDERS VALUES (?,?,?,?)",
            [(int(r["order_id"]), int(r["customer_id"]), float(r["amount"]), r["item"])
             for r in csv.DictReader(f)]
        )
        
    conn.commit()
    conn.close()


def run_sql_file(db_path, sql_file):
    sql = open(sql_file).read()
    conn = sqlite3.connect(db_path)
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    results = []
    for stmt in statements:
        try:
            cur = conn.execute(stmt)
            rows = cur.fetchall()
            if rows:
                results = rows
        except sqlite3.Error as e:
            conn.close()
            raise check50.Failure(
                f"SQL Error in {sql_file}: {e}",
                help="Fix the SQL syntax or query error in your file"
            )
    conn.close()
    return results


@check50.check()
def exists():
    """customer-orders.sql exists"""
    check50.exists("customer-orders.sql")


@check50.check(exists)
def test_db_setup():
    """store database can be created from CSV files"""
    setup_db()
    if not os.path.exists("store.db"):
        raise check50.Failure("Could not create store.db from CSV files")


@check50.check(test_db_setup)
def valid_sql_syntax():
    """SQL query has valid syntax (executes without errors)"""
    run_sql_file("store.db", "customer-orders.sql")


@check50.check(valid_sql_syntax)
def test_correct_results():
    """displays customer names along with their ordered items and amounts"""
    rows = run_sql_file("store.db", "customer-orders.sql")
    # Normalize rows (first_name, last_name, item, amount)
    normalized = sorted([(row[0].strip(), row[1].strip(), row[2].strip(), float(row[3])) for row in rows])
    expected = sorted([
        ("John", "Doe", "Book", 250.0),
        ("John", "Doe", "Laptop", 400.0),
        ("Jane", "Smith", "Phone", 150.0),
        ("Jane", "Smith", "TV", 800.0),
        ("Jack", "Ma", "Car", 1200.0),
        ("Sarah", "Connor", "Keyboard", 300.0),
        ("Sarah", "Connor", "Monitor", 1000.0),
        ("James", "Bond", "Headphones", 100.0),
        ("Maria", "Garcia", "Camera", 600.0)
    ])
    if normalized != expected:
        raise check50.Failure(
            f"Expected to get {expected}, but got {normalized}",
            help="Ensure you JOIN CUSTOMERS and ORDERS on customer_id, selecting first_name, last_name, item, amount"
        )


@check50.check(test_correct_results)
def test_dynamic_db():
    """query reflects database updates dynamically and performs proper join"""
    if not os.path.exists("store.db"):
        setup_db()
    conn = sqlite3.connect("store.db")
    # Update customer name
    conn.execute("UPDATE CUSTOMERS SET first_name = 'Johnny' WHERE customer_id = 1")
    # Add new customer and a matching order
    conn.execute("INSERT INTO CUSTOMERS VALUES (7, 'Tony', 'Stark', 45, 'USA')")
    conn.execute("INSERT INTO ORDERS VALUES (10, 7, 5000.0, 'Suit')")
    conn.commit()
    conn.close()

    rows = run_sql_file("store.db", "customer-orders.sql")
    normalized = sorted([(row[0].strip(), row[1].strip(), row[2].strip(), float(row[3])) for row in rows])
    expected = sorted([
        ("Johnny", "Doe", "Book", 250.0),
        ("Johnny", "Doe", "Laptop", 400.0),
        ("Jane", "Smith", "Phone", 150.0),
        ("Jane", "Smith", "TV", 800.0),
        ("Jack", "Ma", "Car", 1200.0),
        ("Sarah", "Connor", "Keyboard", 300.0),
        ("Sarah", "Connor", "Monitor", 1000.0),
        ("James", "Bond", "Headphones", 100.0),
        ("Maria", "Garcia", "Camera", 600.0),
        ("Tony", "Stark", "Suit", 5000.0)
    ])
    if normalized != expected:
        raise check50.Failure(
            "Query did not dynamically reflect joint updates correctly",
            help="Make sure you use SELECT CUSTOMERS.first_name, CUSTOMERS.last_name, ORDERS.item, ORDERS.amount FROM CUSTOMERS JOIN ORDERS ON ..."
        )
