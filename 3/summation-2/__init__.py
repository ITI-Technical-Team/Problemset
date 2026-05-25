import check50

@check50.check()
def exists():
    """summation-2.cpp exists"""
    check50.exists("summation-2.cpp")

@check50.check(exists)
def test_compile():
    """summation-2.cpp compiles successfully"""
    check50.run("g++ summation-2.cpp -o summation-2").exit(0)

@check50.check(test_compile)
def test1():
    """sums elements correctly (Example 1)"""
    check50.run("./summation-2").stdin("5\n1 5 3 2 4", prompt=False).stdout("15", regex=False).exit(0)

@check50.check(test_compile)
def test2():
    """sums elements correctly (Example 2)"""
    check50.run("./summation-2").stdin("7\n1 4 3 4 3 2 5", prompt=False).stdout("22", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal boundary)"""
    check50.run("./summation-2").stdin("1\n999", prompt=False).stdout("999", regex=False).exit(0)

@check50.check(test_compile)
def test_zeroes():
    """handles edge case of all zeroes"""
    check50.run("./summation-2").stdin("5\n0 0 0 0 0", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_large_sum():
    """handles N = 5 with large elements (exceeding 32-bit integer limits)"""
    check50.run("./summation-2").stdin("5\n2000000000 2000000000 2000000000 2000000000 2000000000", prompt=False).stdout("10000000000", regex=False).exit(0)

