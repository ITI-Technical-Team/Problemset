import check50

@check50.check()
def exists():
    """triangle.cpp exists"""
    check50.exists("triangle.cpp")

@check50.check(exists)
def test_compile():
    """triangle.cpp compiles successfully"""
    check50.run("g++ triangle.cpp -o triangle").exit(0)

@check50.check(test_compile)
def prints_size_3():
    """prints a triangle of size 3 (Example 1)"""
    check50.run("./triangle").stdin("3", prompt=False).stdout("*\n**\n***", regex=False).exit(0)

@check50.check(test_compile)
def prints_size_5():
    """prints a triangle of size 5 (Example 2)"""
    check50.run("./triangle").stdin("5", prompt=False).stdout("*\n**\n***\n****\n*****", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal value)"""
    check50.run("./triangle").stdin("1", prompt=False).stdout("*", regex=False).exit(0)

@check50.check(test_compile)
def test_n_100():
    """handles edge case N = 100 (maximal value)"""
    expected_out = "\n".join("*" * i for i in range(1, 101))
    check50.run("./triangle").stdin("100", prompt=False).stdout(expected_out, regex=False).exit(0)
