import check50
import sqlite3
import csv
import os


def setup_db():
    """Create station.db from included STATION CSV file."""
    check50.include("STATION.csv")
    conn = sqlite3.connect("station.db")
    conn.execute("DROP TABLE IF EXISTS STATION")
    conn.execute("""CREATE TABLE STATION (
        ID INTEGER, CITY TEXT, STATE TEXT,
        LAT_N INTEGER, LONG_W INTEGER
    )""")
    with open("STATION.csv") as f:
        rows = list(csv.DictReader(f))
        data = [(r["ID"], r["CITY"], r["STATE"], r["LAT_N"], r["LONG_W"]) for r in rows]
        conn.executemany(
            "INSERT INTO STATION VALUES (?,?,?,?,?)",
            data + data
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
    """no-vowel-city.sql exists"""
    check50.exists("no-vowel-city.sql")


@check50.check(exists)
def test_db_setup():
    """station database can be created from CSV file"""
    setup_db()
    if not os.path.exists("station.db"):
        raise check50.Failure("Could not create station.db from STATION.csv")


@check50.check(test_db_setup)
def valid_sql_syntax():
    """SQL query has valid syntax (executes without errors)"""
    run_sql_file("station.db", "no-vowel-city.sql")


@check50.check(valid_sql_syntax)
def test_sql_clauses():
    """query uses SELECT DISTINCT and NOT LIKE / NOT REGEXP"""
    sql = open("no-vowel-city.sql").read().upper()
    if "DISTINCT" not in sql or ("LIKE" not in sql and "REGEXP" not in sql and "GLOB" not in sql):
        raise check50.Failure(
            "Query does not use DISTINCT or pattern matching (NOT LIKE)",
            help="Use SELECT DISTINCT CITY FROM STATION WHERE ... NOT LIKE ..."
        )


@check50.check(valid_sql_syntax)
def test_correct_no_vowel_cities():
    """query returns exact list of cities that do not start and do not end with a vowel"""
    rows = run_sql_file("station.db", "no-vowel-city.sql")
    names = set(str(r[0]).strip() for r in rows if r and r[0])

    vowels = set("AEIOUaeiou")
    conn = sqlite3.connect("station.db")
    cur = conn.execute("SELECT DISTINCT CITY FROM STATION")
    all_cities = [r[0] for r in cur.fetchall()]
    conn.close()

    expected = set(c.strip() for c in all_cities if c and c[0] not in vowels and c[-1] not in vowels)

    missing = expected - names
    unexpected = names - expected

    if missing:
        raise check50.Failure(
            f"Query is missing valid cities that do not start and do not end with a vowel: {list(missing)[:3]}",
            help="Use NOT LIKE 'A%' AND NOT LIKE 'E%' ... for start, AND NOT LIKE '%A' AND NOT LIKE '%E' ... for end. Do NOT use NOT LIKE '%A%' which incorrectly removes cities with vowels in the middle!"
        )
    if unexpected:
        raise check50.Failure(
            f"Query returned cities that start or end with a vowel: {list(unexpected)[:3]}",
            help="Make sure your query filters for cities that do NOT start AND do NOT end with a vowel"
        )


@check50.check(valid_sql_syntax)
def test_no_duplicates():
    """results contain no duplicate city names"""
    rows = run_sql_file("station.db", "no-vowel-city.sql")
    names = [str(r[0]) for r in rows]
    if len(names) != len(set(names)):
        from collections import Counter
        dupes = [k for k, v in Counter(names).items() if v > 1]
        raise check50.Failure(
            f"Results contain duplicates: {dupes[:3]}",
            help="Use SELECT DISTINCT to remove duplicate city names"
        )


@check50.check(test_correct_no_vowel_cities)
def test_dynamic_db():
    """query reflects dynamic database updates"""
    conn = sqlite3.connect("station.db")
    conn.execute("INSERT INTO STATION VALUES (9999, 'XYZRST', 'CA', 10, 10)")
    conn.commit()
    conn.close()

    rows = run_sql_file("station.db", "no-vowel-city.sql")
    names = [str(r[0]).strip() for r in rows]
    if "XYZRST" not in names:
        raise check50.Failure(
            "Query returned hardcoded list of city names instead of querying database dynamically",
            help="Write a SQL query using SELECT DISTINCT CITY FROM STATION WHERE ... NOT LIKE ... rather than hardcoding static rows"
        )
