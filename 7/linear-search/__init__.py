import check50

@check50.check()
def exists():
    """linear-search.cpp exists"""
    check50.exists("linear-search.cpp")

@check50.check(exists)
def test_compile():
    """linear-search.cpp compiles successfully"""
    check50.run("g++ linear-search.cpp -o linear-search").exit(0)

@check50.check(test_compile)
def test_example1():
    """finds 0 in array -> 1"""
    check50.run("./linear-search").stdin("3\n3 0 1\n0", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """outputs -1 if target missing -> -1"""
    check50.run("./linear-search").stdin("5\n1 3 0 4 5\n10", prompt=False).stdout("-1", regex=False).exit(0)

@check50.check(test_compile)
def test_example3():
    """returns first position for duplicates -> 0"""
    check50.run("./linear-search").stdin("4\n2 3 2 1\n2", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_first_element():
    """finds target at index 0 -> 0"""
    check50.run("./linear-search").stdin("5\n7 1 2 3 4\n7", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_last_element():
    """finds target at last index -> 4"""
    check50.run("./linear-search").stdin("5\n1 2 3 4 9\n9", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1_match():
    """handles minimal size N = 1 with a match"""
    check50.run("./linear-search").stdin("1\n99\n99", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1_mismatch():
    """handles minimal size N = 1 with no match"""
    check50.run("./linear-search").stdin("1\n99\n10", prompt=False).stdout("-1", regex=False).exit(0)

