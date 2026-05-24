import check50

@check50.check()
def exists():
    """minimum-difference.cpp exists"""
    check50.exists("minimum-difference.cpp")

@check50.check(exists)
def test_compile():
    """minimum-difference.cpp compiles successfully"""
    check50.run("g++ minimum-difference.cpp -o minimum-difference").exit(0)

@check50.check(test_compile)
def test_example1():
    """finds minimum difference correctly (Example 1)"""
    check50.run("./minimum-difference").stdin("6\n1 5 3 19 18 25", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """finds minimum difference correctly (Example 2)"""
    check50.run("./minimum-difference").stdin("5\n4 9 1 32 13", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(test_compile)
def test_duplicates():
    """handles arrays with duplicate values (difference of 0)"""
    check50.run("./minimum-difference").stdin("4\n5 12 5 20", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_negatives():
    """handles arrays with negative values"""
    check50.run("./minimum-difference").stdin("4\n-10 -5 0 5", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_mixed_longer():
    """handles longer mixed arrays"""
    check50.run("./minimum-difference").stdin("10\n15 3 27 8 9 30 21 22 5 100", prompt=False).stdout("1", regex=False).exit(0)
