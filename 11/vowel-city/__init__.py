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
        # Insert all rows twice to create duplicate cities
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
        except sqlite3.Error:
            pass
    conn.close()
    return results


@check50.check()
def exists():
    """vowel-city.sql exists"""
    check50.exists("vowel-city.sql")


@check50.check(exists)
def test_db_setup():
    """station database can be created from CSV file"""
    setup_db()
    if not os.path.exists("station.db"):
        raise check50.Failure("Could not create station.db from STATION.csv")


@check50.check(test_db_setup)
def test_returns_rows():
    """query returns at least one result"""
    rows = run_sql_file("station.db", "vowel-city.sql")
    if not rows:
        raise check50.Failure(
            "Query returned no results",
            help="Use LIKE 'A%' OR LIKE 'E%' ... for cities starting with vowels"
        )


@check50.check(test_db_setup)
def test_vowel_start():
    """all results start with a vowel"""
    rows = run_sql_file("station.db", "vowel-city.sql")
    vowels = set("AEIOUaeiou")
    bad = [str(r[0]) for r in rows if str(r[0]) and str(r[0])[0] not in vowels]
    if bad:
        raise check50.Failure(
            f"Results contain cities NOT starting with a vowel: {bad[:3]}",
            help="Use LIKE 'A%' OR LIKE 'E%' ... for all 5 vowels at the start"
        )


@check50.check(test_db_setup)
def test_vowel_end():
    """all results end with a vowel"""
    rows = run_sql_file("station.db", "vowel-city.sql")
    vowels = set("AEIOUaeiou")
    bad = [str(r[0]) for r in rows if str(r[0]) and str(r[0])[-1] not in vowels]
    if bad:
        raise check50.Failure(
            f"Results contain cities NOT ending with a vowel: {bad[:3]}",
            help="Use LIKE '%a' OR LIKE '%e' ... for all 5 vowels at the end"
        )


@check50.check(test_db_setup)
def test_no_duplicates():
    """results contain no duplicate city names"""
    rows = run_sql_file("station.db", "vowel-city.sql")
    names = [str(r[0]) for r in rows]
    if len(names) != len(set(names)):
        from collections import Counter
        dupes = [k for k, v in Counter(names).items() if v > 1]
        raise check50.Failure(
            f"Results contain duplicates: {dupes[:3]}",
            help="Use SELECT DISTINCT to remove duplicate city names"
        )


@check50.check(test_db_setup)
def test_correct_count():
    """query returns exactly 24 distinct cities"""
    rows = run_sql_file("station.db", "vowel-city.sql")
    if len(rows) != 24:
        raise check50.Failure(
            f"Expected 24 distinct cities (vowel start AND vowel end), got {len(rows)}",
            help="Make sure you filter for BOTH vowel start AND vowel end using OR within each condition"
        )
