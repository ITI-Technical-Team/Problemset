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
    """Execute SQL from a file and return all rows from the last SELECT."""
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
        except sqlite3.Error:
            pass
    conn.close()
    return results


@check50.check()
def exists():
    """asia-sum.sql exists"""
    check50.exists("asia-sum.sql")


@check50.check(exists)
def test_db_setup():
    """cities database can be created from CSV files"""
    setup_db()
    if not os.path.exists("cities.db"):
        raise check50.Failure("Could not create cities.db from CSV files")


@check50.check(test_db_setup)
def test_single_number():
    """query returns exactly one row (the total)"""
    rows = run_sql_file("cities.db", "asia-sum.sql")
    if len(rows) != 1:
        raise check50.Failure(
            f"Expected exactly 1 row (the total population), but got {len(rows)} rows",
            help="Use SUM() to aggregate all values into one result"
        )


@check50.check(test_db_setup)
def test_correct_sum():
    """Asia total population sum is 311021451"""
    rows = run_sql_file("cities.db", "asia-sum.sql")
    if not rows:
        raise check50.Failure("Query returned no results")
    val = int(float(str(rows[0][0])))
    if val != 311021451:
        raise check50.Failure(
            f"Expected the sum to be 311021451, but got: {val}",
            help="Make sure you filter WHERE COUNTRY.Continent = 'Asia' and use SUM(CITY.Population)"
        )


@check50.check(test_db_setup)
def test_not_all_cities_sum():
    """query does not return sum for all cities (only Asia)"""
    rows = run_sql_file("cities.db", "asia-sum.sql")
    if not rows:
        return
    val = int(float(str(rows[0][0])))
    # Total of all cities would be much larger than 311M
    if val > 700000000:
        raise check50.Failure(
            f"The sum ({val}) is too large — make sure you filter for Asia only",
            help="Add WHERE COUNTRY.Continent = 'Asia' to your query"
        )
