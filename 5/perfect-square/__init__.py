import check50

@check50.check()
def exists():
    """perfect-square.cpp exists"""
    check50.exists("perfect-square.cpp")

@check50.check(exists)
def test_compile():
    """perfect-square.cpp compiles successfully"""
    check50.run("g++ perfect-square.cpp -o perfect-square").exit(0)

@check50.check(test_compile)
def test_example1():
    """outputs YES for 25"""
    check50.run("./perfect-square").stdin("25", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """outputs NO for 10"""
    check50.run("./perfect-square").stdin("10", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_zero():
    """outputs YES for 0 (0 = 0^2)"""
    check50.run("./perfect-square").stdin("0", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_one():
    """outputs YES for 1"""
    check50.run("./perfect-square").stdin("1", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_large_square():
    """outputs YES for 9999800001 (99999^2)"""
    check50.run("./perfect-square").stdin("9999800001", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_large_non_square():
    """outputs NO for 999999999"""
    check50.run("./perfect-square").stdin("999999999", prompt=False).stdout("NO", regex=False).exit(0)
