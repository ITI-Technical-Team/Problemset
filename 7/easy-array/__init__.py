import check50

@check50.check()
def exists():
    """easy-array.cpp exists"""
    check50.exists("easy-array.cpp")

@check50.check(exists)
def test_example():
    """sums 2D array correctly (Example)"""
    check50.run("g++ easy-array.cpp -o easy-array && ./easy-array").stdin("3 3\n1 2 3\n4 5 6\n7 8 9", prompt=False).stdout("45", regex=False).exit(0)

@check50.check(exists)
def test_small():
    """handles 2x2 array"""
    check50.run("g++ easy-array.cpp -o easy-array && ./easy-array").stdin("2 2\n1 1\n1 1", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(exists)
def test_rectangular():
    """handles non-square array"""
    check50.run("g++ easy-array.cpp -o easy-array && ./easy-array").stdin("2 3\n10 20 30\n40 50 60", prompt=False).stdout("210", regex=False).exit(0)

@check50.check(exists)
def test_larger():
    """handles larger values and size"""
    check50.run("g++ easy-array.cpp -o easy-array && ./easy-array").stdin("4 4\n1000 1 2 3\n4 5 6 7\n8 9 10 11\n12 13 14 15", prompt=False).stdout("1100", regex=False).exit(0)
