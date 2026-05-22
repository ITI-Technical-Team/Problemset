import check50

@check50.check()
def exists():
    """perfect-square.cpp exists"""
    check50.exists("perfect-square.cpp")

@check50.check(exists)
def test_example1():
    """outputs correct YES for 25"""
    check50.run("g++ perfect-square.cpp -o perfect-square && ./perfect-square").stdin("25", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(exists)
def test_example2():
    """outputs correct NO for 10"""
    check50.run("g++ perfect-square.cpp -o perfect-square && ./perfect-square").stdin("10", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(exists, timeout=1.0)
def test_efficiency():
    """handles very large square efficiency (approx O(1) expected over multiple loops not fully needed, just checks large inputs quickly)"""
    # Just an exact edge case, limits usually apply natively in math ops.
    check50.run("g++ perfect-square.cpp -o perfect-square && ./perfect-square").stdin("999999999", prompt=False).stdout("NO", regex=False).exit(0)
    check50.run("g++ perfect-square.cpp -o perfect-square && ./perfect-square").stdin("1000000000", prompt=False).stdout("NO", regex=False).exit(0)
    check50.run("g++ perfect-square.cpp -o perfect-square && ./perfect-square").stdin("9999800001", prompt=False).stdout("YES", regex=False).exit(0)
