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
    """asia-sum.sql exists"""
    check50.exists("asia-sum.sql")


@check50.check(exists)
def test_db_setup():
    """cities database can be created from CSV files"""
    setup_db()
    if not os.path.exists("cities.db"):
        raise check50.Failure("Could not create cities.db from CSV files")


@check50.check(test_db_setup)
def test_sql_clauses():
    """query uses JOIN and SUM()"""
    sql = open("asia-sum.sql").read().upper()
    if "SUM" not in sql or ("JOIN" not in sql and "WHERE" not in sql):
        raise check50.Failure(
            "Query does not use SUM() or JOIN/WHERE filtering",
            help="Use SUM(CITY.POPULATION) and JOIN COUNTRY ON CITY.CountryCode = COUNTRY.Code"
        )


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
    if not rows or not rows[0] or rows[0][0] is None:
        raise check50.Failure("Query returned no results or NULL")
    try:
        val = int(float(str(rows[0][0])))
    except (ValueError, TypeError):
        raise check50.Failure(f"Could not parse numeric result, got: {rows[0][0]}")

    if val != 311021451:
        raise check50.Failure(
            f"Expected the sum to be 311021451, but got: {val}",
            help="Make sure you filter WHERE COUNTRY.Continent = 'Asia' and use SUM(CITY.Population)"
        )


@check50.check(test_correct_sum)
def test_dynamic_db():
    """query reflects dynamic database updates"""
    if not os.path.exists("cities.db"):
        setup_db()
    conn = sqlite3.connect("cities.db")
    conn.execute("UPDATE CITY SET POPULATION = POPULATION + 1000 WHERE NAME = 'Tokyo'")
    conn.commit()
    conn.close()

    rows = run_sql_file("cities.db", "asia-sum.sql")
    val = int(float(str(rows[0][0])))
    if val != 311022451:
        raise check50.Failure(
            "Query returned hardcoded population value instead of dynamically summing database rows",
            help="Write a SQL query using JOIN and SUM() rather than hardcoding static numbers"
        )
