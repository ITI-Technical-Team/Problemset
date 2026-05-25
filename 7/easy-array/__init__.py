import check50

@check50.check()
def exists():
    """easy-array.cpp exists"""
    check50.exists("easy-array.cpp")

@check50.check(exists)
def test_compile():
    """easy-array.cpp compiles successfully"""
    check50.run("g++ easy-array.cpp -o easy-array").exit(0)

@check50.check(test_compile)
def test_example():
    """sums 2D array correctly (Example)"""
    check50.run("./easy-array").stdin("3 3\n1 2 3\n4 5 6\n7 8 9", prompt=False).stdout("45", regex=False).exit(0)

@check50.check(test_compile)
def test_small():
    """handles 2x2 array"""
    check50.run("./easy-array").stdin("2 2\n1 1\n1 1", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test_rectangular():
    """handles non-square array"""
    check50.run("./easy-array").stdin("2 3\n10 20 30\n40 50 60", prompt=False).stdout("210", regex=False).exit(0)

@check50.check(test_compile)
def test_larger():
    """handles larger values and size"""
    # Sum: 1000 + (1+2+3+4+5+6+7+8+9+10+11+12+13+14+15) = 1000 + 120 = 1120.
    check50.run("./easy-array").stdin("4 4\n1000 1 2 3\n4 5 6 7\n8 9 10 11\n12 13 14 15", prompt=False).stdout("1120", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal():
    """handles minimal 1x1 array size"""
    check50.run("./easy-array").stdin("1 1\n999", prompt=False).stdout("999", regex=False).exit(0)

@check50.check(test_compile)
def test_negatives():
    """handles all negative elements"""
    check50.run("./easy-array").stdin("2 2\n-1 -2\n-3 -4", prompt=False).stdout("-10", regex=False).exit(0)

@check50.check(test_compile)
def test_large_sum():
    """handles large sum exceeding 32-bit signed integer limits"""
    check50.run("./easy-array").stdin("2 2\n2000000000 2000000000\n2000000000 2000000000", prompt=False).stdout("8000000000", regex=False).exit(0)

