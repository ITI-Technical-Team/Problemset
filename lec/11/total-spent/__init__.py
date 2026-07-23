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
    """total-spent.sql exists"""
    check50.exists("total-spent.sql")


@check50.check(exists)
def test_db_setup():
    """store database can be created from CSV files"""
    setup_db()
    if not os.path.exists("store.db"):
        raise check50.Failure("Could not create store.db from CSV files")


@check50.check(test_db_setup)
def valid_sql_syntax():
    """SQL query has valid syntax (executes without errors)"""
    run_sql_file("store.db", "total-spent.sql")


@check50.check(valid_sql_syntax)
def test_correct_results():
    """finds total amount spent by each customer, filtering for totals > 500"""
    rows = run_sql_file("store.db", "total-spent.sql")
    # Normalize rows (customer_id, total_amount)
    normalized = sorted([(int(row[0]), float(row[1])) for row in rows])
    expected = sorted([
        (1, 650.0),
        (2, 950.0),
        (3, 1200.0),
        (4, 1300.0),
        (6, 600.0)
    ])
    if normalized != expected:
        raise check50.Failure(
            f"Expected to get {expected}, but got {normalized}",
            help="Ensure you GROUP BY customer_id and filter using HAVING SUM(amount) > 500"
        )


@check50.check(test_correct_results)
def test_dynamic_db():
    """query reflects database updates dynamically and utilizes HAVING clause"""
    if not os.path.exists("store.db"):
        setup_db()
    conn = sqlite3.connect("store.db")
    # Customer 5 currently spent 100. Add an order of 450 to make total 550 (> 500)
    conn.execute("INSERT INTO ORDERS VALUES (10, 5, 450.0, 'Tablet')")
    # Customer 6 currently spent 600. Update order to make total exactly 500 (should be excluded!)
    conn.execute("UPDATE ORDERS SET amount = 500.0 WHERE order_id = 9")
    conn.commit()
    conn.close()

    rows = run_sql_file("store.db", "total-spent.sql")
    normalized = sorted([(int(row[0]), float(row[1])) for row in rows])
    expected = sorted([
        (1, 650.0),
        (2, 950.0),
        (3, 1200.0),
        (4, 1300.0),
        (5, 550.0)
    ])
    if normalized != expected:
        raise check50.Failure(
            "Query did not dynamically group or filter correctly after database updates",
            help="Ensure you use SUM(amount) and HAVING SUM(amount) > 500"
        )
