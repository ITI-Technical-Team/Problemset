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
    """continent-avg.sql exists"""
    check50.exists("continent-avg.sql")


@check50.check(exists)
def test_db_setup():
    """cities database can be created from CSV files"""
    setup_db()
    if not os.path.exists("cities.db"):
        raise check50.Failure("Could not create cities.db from CSV files")


@check50.check(test_db_setup)
def test_returns_6_rows():
    """query returns one row per continent (6 continents)"""
    rows = run_sql_file("cities.db", "continent-avg.sql")
    if len(rows) != 6:
        raise check50.Failure(
            f"Expected 6 rows (one per continent), but got {len(rows)}",
            help="Make sure you GROUP BY COUNTRY.Continent"
        )


@check50.check(test_db_setup)
def test_africa_avg():
    """Africa average population is 4929564"""
    rows = run_sql_file("cities.db", "continent-avg.sql")
    # Look for Africa row
    africa_row = next((r for r in rows if "Africa" in str(r)), None)
    if africa_row is None:
        raise check50.Failure(
            "Expected 'Africa' in the results",
            help="Make sure you SELECT COUNTRY.Continent in your query"
        )
    # The avg value (second column) should be 4929564
    avg_val = int(float(str(africa_row[1])))
    if avg_val != 4929564:
        raise check50.Failure(
            f"Africa's average city population should be 4929564 (floored), but got {avg_val}",
            help="Use FLOOR(AVG(CITY.Population)) or CAST(AVG(CITY.Population) AS INTEGER)"
        )


@check50.check(test_db_setup)
def test_asia_avg():
    """Asia average population is 11107908"""
    rows = run_sql_file("cities.db", "continent-avg.sql")
    asia_row = next((r for r in rows if "Asia" in str(r)), None)
    if asia_row is None:
        raise check50.Failure(
            "Expected 'Asia' in the results",
            help="Make sure you SELECT COUNTRY.Continent in your query"
        )
    avg_val = int(float(str(asia_row[1])))
    if avg_val != 11107908:
        raise check50.Failure(
            f"Asia's average city population should be 11107908 (floored), but got {avg_val}",
            help="Use FLOOR(AVG(CITY.Population)) or CAST(AVG(CITY.Population) AS INTEGER)"
        )


@check50.check(test_db_setup)
def test_uses_floor():
    """average is floored (not rounded) to nearest integer"""
    rows = run_sql_file("cities.db", "continent-avg.sql")
    for row in rows:
        val = row[1]
        if isinstance(val, float) and val != int(val):
            raise check50.Failure(
                f"Average should be floored to an integer, but got decimal: {val}",
                help="Use FLOOR() or CAST(... AS INTEGER) to round down"
            )
