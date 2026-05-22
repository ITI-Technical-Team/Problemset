import check50

@check50.check()
def exists():
    """search.cpp exists"""
    check50.exists("search.cpp")

@check50.check(exists)
def test1():
    """finds element that exists (Example 1)"""
    check50.run("g++ search.cpp -o search && ./search").stdin("6 2\n1 2 3 4 5 6", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(exists)
def test2():
    """outputs notfound if element doesn't exist (Example 2)"""
    check50.run("g++ search.cpp -o search && ./search").stdin("3 3\n5 22 1", prompt=False).stdout("notfound", regex=False).exit(0)
