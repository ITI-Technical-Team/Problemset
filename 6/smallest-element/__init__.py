import check50

@check50.check()
def exists():
    """smallest-element.cpp exists"""
    check50.exists("smallest-element.cpp")

@check50.check(exists)
def test_compile():
    """smallest-element.cpp compiles successfully"""
    check50.run("g++ smallest-element.cpp -o smallest-element").exit(0)

@check50.check(test_compile)
def test_example1():
    """finds k-th smallest element correctly (Example 1)"""
    check50.run("./smallest-element").stdin("5 3\n64 25 12 22 11", prompt=False).stdout("22", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """finds k-th smallest element correctly (Example 2)"""
    check50.run("./smallest-element").stdin("6 4\n30 10 20 50 40 60", prompt=False).stdout("40", regex=False).exit(0)

@check50.check(test_compile)
def test_k1():
    """handles k = 1 (absolute smallest)"""
    check50.run("./smallest-element").stdin("4 1\n8 9 7 6", prompt=False).stdout("6", regex=False).exit(0)

@check50.check(test_compile)
def test_kN():
    """handles k = N (absolute largest)"""
    check50.run("./smallest-element").stdin("4 4\n8 9 7 6", prompt=False).stdout("9", regex=False).exit(0)

@check50.check(test_compile)
def test_mid_with_duplicates():
    """handles mid-k with duplicates"""
    check50.run("./smallest-element").stdin("7 4\n5 1 3 3 2 9 5", prompt=False).stdout("3", regex=False).exit(0)
