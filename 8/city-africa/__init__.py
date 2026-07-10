import check50
import sqlite3
import csv
import os


def setup_db():
    """Create cities.db from included CSV files using Python's sqlite3 module."""
    check50.include("CITY.csv", "COUNTRY.csv")
    conn = sqlite3.connect("cities.db")
    conn.execute("DROP TABLE IF EXISTS COUNTRY")
    conn.execute("DROP TABLE IF EXISTS CITY")
    conn.execute("""CREATE TABLE COUNTRY (
        CODE TEXT, NAME TEXT, CONTINENT TEXT,
        CAPITAL TEXT, AREA REAL, POPULATION INTEGER
    )""")
    conn.execute("""CREATE TABLE CITY (
        ID INTEGER, NAME TEXT, COUNTRYCODE TEXT,
        DISTRICT TEXT, POPULATION INTEGER
    )""")
    with open("COUNTRY.csv") as f:
        conn.executemany(
            "INSERT INTO COUNTRY VALUES (?,?,?,?,?,?)",
            [(r["CODE"], r["NAME"], r["CONTINENT"], r["CAPITAL"],
              r["AREA"], r["POPULATION"])
             for r in csv.DictReader(f)]
        )
    with open("CITY.csv") as f:
        conn.executemany(
            "INSERT INTO CITY VALUES (?,?,?,?,?)",
            [(r["ID"], r["NAME"], r["COUNTRYCODE"], r["DISTRICT"], r["POPULATION"])
             for r in csv.DictReader(f)]
        )
    conn.commit()
    conn.close()


def run_sql_file(db_path, sql_file):
    """Execute SQL from a file against a SQLite database and return rows."""
    sql = open(sql_file).read()
    conn = sqlite3.connect(db_path)
    # Strip comments and split on semicolons; run last non-empty statement
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    results = []
    for stmt in statements:
        try:
            cur = conn.execute(stmt)
            rows = cur.fetchall()
            if rows:
                results = rows
        except sqlite3.Error:
            pass
    conn.close()
    return results


@check50.check()
def exists():
    """city-africa.sql exists"""
    check50.exists("city-africa.sql")


@check50.check(exists)
def test_db_setup():
    """cities database can be created from CSV files"""
    setup_db()
    if not os.path.exists("cities.db"):
        raise check50.Failure("Could not create cities.db from CSV files")


@check50.check(test_db_setup)
def test_returns_rows():
    """query returns at least one city in Africa"""
    rows = run_sql_file("cities.db", "city-africa.sql")
    if not rows:
        raise check50.Failure(
            "Query returned no results",
            help="Make sure your JOIN is correct and you are filtering by Continent = 'Africa'"
        )


@check50.check(test_db_setup)
def test_cairo_in_results():
    """query results include 'Cairo'"""
    rows = run_sql_file("cities.db", "city-africa.sql")
    names = [str(r[0]).strip() for r in rows]
    if "Cairo" not in names:
        raise check50.Failure(
            "Expected 'Cairo' in results (it is a city in Africa)",
            help="Check your JOIN condition: CITY.CountryCode = COUNTRY.Code"
        )


@check50.check(test_db_setup)
def test_nairobi_in_results():
    """query results include 'Nairobi'"""
    rows = run_sql_file("cities.db", "city-africa.sql")
    names = [str(r[0]).strip() for r in rows]
    if "Nairobi" not in names:
        raise check50.Failure(
            "Expected 'Nairobi' in results (it is a city in Africa)",
            help="Make sure you filter WHERE COUNTRY.Continent = 'Africa'"
        )


@check50.check(test_db_setup)
def test_no_non_african_cities():
    """query does not include cities from other continents"""
    rows = run_sql_file("cities.db", "city-africa.sql")
    names = [str(r[0]).strip() for r in rows]
    non_african = ["Beijing", "London", "Paris", "New York", "Tokyo", "Sydney"]
    found = [c for c in non_african if c in names]
    if found:
        raise check50.Failure(
            f"Query should only return African cities, but found: {found}",
            help="Check your WHERE clause – make sure it filters by Continent = 'Africa'"
        )


@check50.check(test_db_setup)
def test_correct_count():
    """query returns exactly 14 African cities"""
    rows = run_sql_file("cities.db", "city-africa.sql")
    if len(rows) != 14:
        raise check50.Failure(
            f"Expected 14 African cities, but got {len(rows)}",
            help="Make sure you are selecting CITY.Name (not country name) and joining correctly"
        )
