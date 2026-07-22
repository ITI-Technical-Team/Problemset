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
    """continent-avg.sql exists"""
    check50.exists("continent-avg.sql")


@check50.check(exists)
def test_db_setup():
    """cities database can be created from CSV files"""
    setup_db()
    if not os.path.exists("cities.db"):
        raise check50.Failure("Could not create cities.db from CSV files")


@check50.check(test_db_setup)
def valid_sql_syntax():
    """SQL query has valid syntax (executes without errors)"""
    run_sql_file("cities.db", "continent-avg.sql")


@check50.check(valid_sql_syntax)
def test_sql_clauses():
    """query uses GROUP BY and AVG()"""
    sql = open("continent-avg.sql").read().upper()
    if "GROUP BY" not in sql or "AVG" not in sql:
        raise check50.Failure(
            "Query does not use GROUP BY or AVG()",
            help="Use GROUP BY COUNTRY.Continent and FLOOR(AVG(CITY.Population))"
        )


@check50.check(valid_sql_syntax)
def test_returns_6_rows():
    """query returns one row per continent (6 continents)"""
    rows = run_sql_file("cities.db", "continent-avg.sql")
    if len(rows) != 6:
        raise check50.Failure(
            f"Expected 6 rows (one per continent), but got {len(rows)}",
            help="Make sure you GROUP BY COUNTRY.Continent"
        )


@check50.check(valid_sql_syntax)
def test_africa_avg():
    """Africa average population is 4929564"""
    rows = run_sql_file("cities.db", "continent-avg.sql")
    africa_row = next((r for r in rows if "Africa" in str(r)), None)
    if africa_row is None:
        raise check50.Failure(
            "Expected 'Africa' in the results",
            help="Make sure you SELECT COUNTRY.Continent in your query"
        )
    avg_val = int(float(str(africa_row[1])))
    if avg_val != 4929564:
        raise check50.Failure(
            f"Africa's average city population should be 4929564 (floored), but got {avg_val}",
            help="Use FLOOR(AVG(CITY.Population)) or CAST(AVG(CITY.Population) AS INTEGER)"
        )


@check50.check(valid_sql_syntax)
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


@check50.check(test_africa_avg)
def test_dynamic_db():
    """query reflects dynamic database updates"""
    if not os.path.exists("cities.db"):
        setup_db()
    conn = sqlite3.connect("cities.db")
    # Increase Cairo (African city) population by 14 (14 cities in Africa) to increase avg by 1
    conn.execute("UPDATE CITY SET POPULATION = POPULATION + 14 WHERE NAME = 'Cairo'")
    conn.commit()
    conn.close()

    rows = run_sql_file("cities.db", "continent-avg.sql")
    africa_row = next((r for r in rows if "Africa" in str(r)), None)
    avg_val = int(float(str(africa_row[1])))
    if avg_val != 4929565:
        raise check50.Failure(
            "Query returned hardcoded population averages instead of dynamically calculating from database rows",
            help="Write a SQL query using JOIN, GROUP BY, and AVG() rather than UNION SELECT hardcoded values"
        )
