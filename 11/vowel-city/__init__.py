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
    """vowel-city.sql exists"""
    check50.exists("vowel-city.sql")


@check50.check(exists)
def test_db_setup():
    """station database can be created from CSV file"""
    setup_db()
    if not os.path.exists("station.db"):
        raise check50.Failure("Could not create station.db from STATION.csv")


@check50.check(test_db_setup)
def valid_sql_syntax():
    """SQL query has valid syntax (executes without errors)"""
    run_sql_file("station.db", "vowel-city.sql")


@check50.check(valid_sql_syntax)
def test_sql_clauses():
    """query uses SELECT DISTINCT and pattern matching"""
    sql = open("vowel-city.sql").read().upper()
    if "DISTINCT" not in sql or ("LIKE" not in sql and "REGEXP" not in sql and "GLOB" not in sql):
        raise check50.Failure(
            "Query does not use DISTINCT or pattern matching (LIKE)",
            help="Use SELECT DISTINCT CITY FROM STATION WHERE ... LIKE ..."
        )


@check50.check(valid_sql_syntax)
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


@check50.check(valid_sql_syntax)
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


@check50.check(valid_sql_syntax)
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


@check50.check(test_vowel_start)
def test_dynamic_db():
    """query reflects dynamic database updates"""
    conn = sqlite3.connect("station.db")
    conn.execute("INSERT INTO STATION VALUES (9999, 'Acacia', 'CA', 10, 10)")
    conn.commit()
    conn.close()

    rows = run_sql_file("station.db", "vowel-city.sql")
    names = [str(r[0]).strip() for r in rows]
    if "Acacia" not in names:
        raise check50.Failure(
            "Query returned hardcoded list of city names instead of querying database dynamically",
            help="Write a SQL query using SELECT DISTINCT CITY FROM STATION WHERE ... LIKE ... rather than hardcoding static rows"
        )
