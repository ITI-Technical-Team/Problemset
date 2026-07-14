import check50

@check50.check()
def exists():
    """second-maximum.cpp exists"""
    check50.exists("second-maximum.cpp")

@check50.check(exists)
def test_compile():
    """second-maximum.cpp compiles successfully"""
    check50.run("g++ second-maximum.cpp -o second-maximum").exit(0)

@check50.check(test_compile)
def test_example1():
    """finds second maximum correctly (Example 1)"""
    check50.run("./second-maximum").stdin("5\n9 5 10 1 3", prompt=False).stdout("9", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """finds second maximum correctly (Example 2)"""
    check50.run("./second-maximum").stdin("6\n1 8 4 9 2 3", prompt=False).stdout("8", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal():
    """handles minimal array size N = 2 with distinct values"""
    check50.run("./second-maximum").stdin("2\n5 10", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_large_values():
    """handles large values near 10^5"""
    check50.run("./second-maximum").stdin("4\n99999 100000 99998 5", prompt=False).stdout("99999", regex=False).exit(0)

@check50.check(test_compile)
def test_sorted():
    """handles already sorted distinct array"""
    check50.run("./second-maximum").stdin("5\n2 4 6 8 10", prompt=False).stdout("8", regex=False).exit(0)

@check50.check(test_compile)
def test_reverse_sorted():
    """handles reverse sorted distinct array"""
    check50.run("./second-maximum").stdin("5\n10 8 6 4 2", prompt=False).stdout("8", regex=False).exit(0)

