import check50

@check50.check()
def exists():
    """summation-2.cpp exists"""
    check50.exists("summation-2.cpp")

@check50.check(exists)
def test1():
    """sums elements correctly (Example 1)"""
    check50.run("g++ summation-2.cpp -o summation-2 && ./summation-2").stdin("5\n1 5 3 2 4", prompt=False).stdout("15", regex=False).exit(0)

@check50.check(exists)
def test2():
    """sums elements correctly (Example 2)"""
    check50.run("g++ summation-2.cpp -o summation-2 && ./summation-2").stdin("7\n1 4 3 4 3 2 5", prompt=False).stdout("22", regex=False).exit(0)
