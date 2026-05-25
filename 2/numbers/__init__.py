import check50

@check50.check()
def exists():
    """numbers.cpp exists"""
    check50.exists("numbers.cpp")

@check50.check(exists)
def test_compile():
    """numbers.cpp compiles successfully"""
    check50.run("g++ numbers.cpp -o numbers").exit(0)

@check50.check(test_compile)
def prints_3():
    """prints numbers from 1 to 3 (Example 1)"""
    check50.run("./numbers").stdin("3", prompt=False).stdout("1 2 3", regex=False).exit(0)

@check50.check(test_compile)
def prints_5():
    """prints numbers from 1 to 5 (Example 2)"""
    check50.run("./numbers").stdin("5", prompt=False).stdout("1 2 3 4 5", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal value)"""
    check50.run("./numbers").stdin("1", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_n_100():
    """handles edge case N = 100 (maximal value)"""
    expected_out = " ".join(str(i) for i in range(1, 101))
    check50.run("./numbers").stdin("100", prompt=False).stdout(expected_out, regex=False).exit(0)
