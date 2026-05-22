import check50

@check50.check()
def exists():
    """second-maximum.cpp exists"""
    check50.exists("second-maximum.cpp")

@check50.check(exists)
def test_example1():
    """finds second maximum correctly (Example 1)"""
    check50.run("g++ second-maximum.cpp -o second-maximum && ./second-maximum").stdin("5\n9 5 10 1 3", prompt=False).stdout("9", regex=False).exit(0)

@check50.check(exists)
def test_example2():
    """finds second maximum correctly (Example 2)"""
    check50.run("g++ second-maximum.cpp -o second-maximum && ./second-maximum").stdin("6\n1 8 4 9 2 3", prompt=False).stdout("8", regex=False).exit(0)

@check50.check(exists)
def test_negatives():
    """handles array of negative numbers"""
    check50.run("g++ second-maximum.cpp -o second-maximum && ./second-maximum").stdin("4\n-1 -5 -2 -10", prompt=False).stdout("-2", regex=False).exit(0)

@check50.check(exists)
def test_duplicates():
    """handles arrays with duplicate maximum values"""
    check50.run("g++ second-maximum.cpp -o second-maximum && ./second-maximum").stdin("5\n10 10 9 8 7", prompt=False).stdout("9", regex=False).exit(0)
