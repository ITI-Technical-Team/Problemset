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
    """order-amount.sql exists"""
    check50.exists("order-amount.sql")


@check50.check(exists)
def test_db_setup():
    """store database can be created from CSV files"""
    setup_db()
    if not os.path.exists("store.db"):
        raise check50.Failure("Could not create store.db from CSV files")


@check50.check(test_db_setup)
def valid_sql_syntax():
    """SQL query has valid syntax (executes without errors)"""
    run_sql_file("store.db", "order-amount.sql")


@check50.check(valid_sql_syntax)
def test_correct_results():
    """finds all orders where amount is between 300 and 1000 inclusive"""
    rows = run_sql_file("store.db", "order-amount.sql")
    # Normalize rows (order_id, customer_id, amount, item)
    normalized = sorted([(int(row[0]), int(row[1]), float(row[2]), row[3].strip()) for row in rows])
    expected = sorted([
        (2, 1, 400.0, "Laptop"),
        (4, 2, 800.0, "TV"),
        (6, 4, 300.0, "Keyboard"),
        (7, 4, 1000.0, "Monitor"),
        (9, 6, 600.0, "Camera")
    ])
    if normalized != expected:
        raise check50.Failure(
            f"Expected to get {expected}, but got {normalized}",
            help="Ensure you select all columns where amount is between 300 and 1000 inclusive"
        )


@check50.check(test_correct_results)
def test_dynamic_db():
    """query reflects database updates dynamically and checks inclusiveness boundaries"""
    if not os.path.exists("store.db"):
        setup_db()
    conn = sqlite3.connect("store.db")
    # Add boundary test orders: 299 (exclude), 300 (include), 1000 (include), 1001 (exclude)
    conn.execute("INSERT INTO ORDERS VALUES (10, 1, 299.99, 'Cheap Item')")
    conn.execute("INSERT INTO ORDERS VALUES (11, 1, 1000.01, 'Expensive Item')")
    conn.execute("INSERT INTO ORDERS VALUES (12, 1, 500.0, 'Middle Item')")
    conn.commit()
    conn.close()

    rows = run_sql_file("store.db", "order-amount.sql")
    normalized = sorted([(int(row[0]), int(row[1]), float(row[2]), row[3].strip()) for row in rows])
    expected = sorted([
        (2, 1, 400.0, "Laptop"),
        (4, 2, 800.0, "TV"),
        (6, 4, 300.0, "Keyboard"),
        (7, 4, 1000.0, "Monitor"),
        (9, 6, 600.0, "Camera"),
        (12, 1, 500.0, "Middle Item")
    ])
    if normalized != expected:
        raise check50.Failure(
            "Query did not dynamically filter correctly based on boundaries",
            help="Make sure you use amount >= 300 AND amount <= 1000 or BETWEEN 300 AND 1000"
        )
