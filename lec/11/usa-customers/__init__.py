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
    """usa-customers.sql exists"""
    check50.exists("usa-customers.sql")


@check50.check(exists)
def test_db_setup():
    """store database can be created from CSV files"""
    setup_db()
    if not os.path.exists("store.db"):
        raise check50.Failure("Could not create store.db from CSV files")


@check50.check(test_db_setup)
def valid_sql_syntax():
    """SQL query has valid syntax (executes without errors)"""
    run_sql_file("store.db", "usa-customers.sql")


@check50.check(valid_sql_syntax)
def test_correct_results():
    """retrieves correct first_name and age for USA customers"""
    rows = run_sql_file("store.db", "usa-customers.sql")
    # Normalize rows
    normalized = sorted([(row[0].strip(), int(row[1])) for row in rows])
    expected = sorted([("John", 31), ("Sarah", 40)])
    if normalized != expected:
        raise check50.Failure(
            f"Expected to get {expected}, but got {normalized}",
            help="Ensure you select first_name and age where country is 'USA'"
        )


@check50.check(test_correct_results)
def test_dynamic_db():
    """query reflects database updates dynamically"""
    if not os.path.exists("store.db"):
        setup_db()
    conn = sqlite3.connect("store.db")
    conn.execute("INSERT INTO CUSTOMERS VALUES (7, 'Joe', 'Biden', 81, 'USA')")
    conn.commit()
    conn.close()

    rows = run_sql_file("store.db", "usa-customers.sql")
    normalized = sorted([(row[0].strip(), int(row[1])) for row in rows])
    expected = sorted([("John", 31), ("Sarah", 40), ("Joe", 81)])
    if normalized != expected:
        raise check50.Failure(
            "Query returned hardcoded values instead of dynamically querying database rows",
            help="Write a SELECT query using the WHERE country = 'USA' clause"
        )
