import check50

@check50.check()
def exists():
    """linear-search.cpp exists"""
    check50.exists("linear-search.cpp")

@check50.check(exists)
def test_example1():
    """finds 0 in array -> 1"""
    check50.run("g++ linear-search.cpp -o linear-search && ./linear-search").stdin("3\n3 0 1\n0", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(exists)
def test_example2():
    """outputs -1 if target missing -> -1"""
    check50.run("g++ linear-search.cpp -o linear-search && ./linear-search").stdin("5\n1 3 0 4 5\n10", prompt=False).stdout("-1", regex=False).exit(0)

@check50.check(exists)
def test_example3():
    """returns first position for duplicates -> 0"""
    check50.run("g++ linear-search.cpp -o linear-search && ./linear-search").stdin("4\n2 3 2 1\n2", prompt=False).stdout("0", regex=False).exit(0)

