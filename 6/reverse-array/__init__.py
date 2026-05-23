import check50

@check50.check()
def exists():
    """reverse-array.cpp exists"""
    check50.exists("reverse-array.cpp")

@check50.check(exists)
def test_example():
    """reverses a typical array (Example 1)"""
    check50.run("g++ reverse-array.cpp -o reverse-array && ./reverse-array").stdin("5\n2 6 9 7 3", prompt=False).stdout("3 7 9 6 2", regex=False).exit(0)

@check50.check(exists)
def test_single():
    """handles array of length 1"""
    check50.run("g++ reverse-array.cpp -o reverse-array && ./reverse-array").stdin("1\n42", prompt=False).stdout("42", regex=False).exit(0)

@check50.check(exists)
def test_even():
    """handles an array of even length"""
    check50.run("g++ reverse-array.cpp -o reverse-array && ./reverse-array").stdin("4\n10 20 30 40", prompt=False).stdout("40 30 20 10", regex=False).exit(0)

@check50.check(exists)
def test_negatives():
    """handles negative values and duplicates"""
    check50.run("g++ reverse-array.cpp -o reverse-array && ./reverse-array").stdin("4\n-1 -1 5 -1", prompt=False).stdout("-1 5 -1 -1", regex=False).exit(0)

@check50.check(exists)
def test_longer():
    """handles a longer mixed array"""
    check50.run("g++ reverse-array.cpp -o reverse-array && ./reverse-array").stdin("10\n5 0 -2 7 7 3 9 -1 4 8", prompt=False).stdout("8 4 -1 9 3 7 7 -2 0 5", regex=False).exit(0)
