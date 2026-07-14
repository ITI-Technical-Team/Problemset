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
        conn.executemany(
            "INSERT INTO STATION VALUES (?,?,?,?,?)",
            [(r["ID"], r["CITY"], r["STATE"], r["LAT_N"], r["LONG_W"])
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
    """no-vowel-city.sql exists"""
    check50.exists("no-vowel-city.sql")


@check50.check(exists)
def test_db_setup():
    """station database can be created from CSV file"""
    setup_db()
    if not os.path.exists("station.db"):
        raise check50.Failure("Could not create station.db from STATION.csv")


@check50.check(test_db_setup)
def test_returns_rows():
    """query returns at least one result"""
    rows = run_sql_file("station.db", "no-vowel-city.sql")
    if not rows:
        raise check50.Failure(
            "Query returned no results",
            help="Check your LIKE patterns — exclude cities starting AND ending with vowels (A,E,I,O,U)"
        )


@check50.check(test_db_setup)
def test_no_vowel_start():
    """results have no city starting with a vowel"""
    rows = run_sql_file("station.db", "no-vowel-city.sql")
    vowels = set("AEIOUaeiou")
    bad = [str(r[0]) for r in rows if str(r[0]) and str(r[0])[0] in vowels]
    if bad:
        raise check50.Failure(
            f"Results contain cities starting with a vowel: {bad[:3]}",
            help="Use NOT LIKE 'A%' AND NOT LIKE 'E%' ... for all 5 vowels"
        )


@check50.check(test_db_setup)
def test_no_vowel_end():
    """results have no city ending with a vowel"""
    rows = run_sql_file("station.db", "no-vowel-city.sql")
    vowels = set("AEIOUaeiou")
    bad = [str(r[0]) for r in rows if str(r[0]) and str(r[0])[-1] in vowels]
    if bad:
        raise check50.Failure(
            f"Results contain cities ending with a vowel: {bad[:3]}",
            help="Use NOT LIKE '%a' AND NOT LIKE '%e' ... for all 5 vowels"
        )


@check50.check(test_db_setup)
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


@check50.check(test_db_setup)
def test_correct_count():
    """query returns exactly 28 distinct cities"""
    rows = run_sql_file("station.db", "no-vowel-city.sql")
    if len(rows) != 28:
        raise check50.Failure(
            f"Expected 28 distinct cities (no vowel start AND no vowel end), got {len(rows)}",
            help="Make sure you filter BOTH start AND end of city name for all vowels"
        )
