import check50

@check50.check()
def exists():
    """maximum.cpp exists"""
    check50.exists("maximum.cpp")

@check50.check(exists)
def test_example1():
    """counts divisors of max correctly (Example 1)"""
    check50.run("g++ maximum.cpp -o maximum && ./maximum").stdin("7\n3 2 4 1 10 6 8", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(exists)
def test_example2():
    """counts divisors of max correctly (Example 2)"""
    check50.run("g++ maximum.cpp -o maximum && ./maximum").stdin("3\n2 4 11", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(exists)
def test_all_equal():
    """handles arrays where all elements equal the max"""
    check50.run("g++ maximum.cpp -o maximum && ./maximum").stdin("4\n5 5 5 5", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(exists)
def test_mixed_divisors():
    """handles a mixed array with several divisors"""
    check50.run("g++ maximum.cpp -o maximum && ./maximum").stdin("6\n6 3 2 1 12 7", prompt=False).stdout("5", regex=False).exit(0)
