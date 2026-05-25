import check50

@check50.check()
def exists():
    """search.cpp exists"""
    check50.exists("search.cpp")

@check50.check(exists)
def test_compile():
    """search.cpp compiles successfully"""
    check50.run("g++ search.cpp -o search").exit(0)

@check50.check(test_compile)
def test1():
    """finds element that exists (Example 1)"""
    check50.run("./search").stdin("6 2\n1 2 3 4 5 6", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test2():
    """outputs notfound if element doesn't exist (Example 2)"""
    check50.run("./search").stdin("3 3\n5 22 1", prompt=False).stdout("notfound", regex=False).exit(0)

@check50.check(test_compile)
def test_first_element():
    """handles element found at first index (index 0)"""
    check50.run("./search").stdin("5 99\n99 2 3 4 5", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_last_element():
    """handles element found at last index (index N-1)"""
    check50.run("./search").stdin("5 99\n1 2 3 4 99", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_duplicate_target():
    """returns the first index if multiple copies of the target exist"""
    check50.run("./search").stdin("5 99\n1 99 3 99 5", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal size)"""
    check50.run("./search").stdin("1 99\n99", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1000():
    """handles N = 1000 with target at the very end"""
    stdin_data = "1000 99999\n" + " ".join(str(i) for i in range(999)) + " 99999"
    check50.run("./search").stdin(stdin_data, prompt=False).stdout("999", regex=False).exit(0)

