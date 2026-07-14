import check50

@check50.check()
def exists():
    """replacement.cpp exists"""
    check50.exists("replacement.cpp")

@check50.check(exists)
def test_compile():
    """replacement.cpp compiles successfully"""
    check50.run("g++ replacement.cpp -o replacement").exit(0)

@check50.check(test_compile)
def test1():
    """swaps elements correctly (Example 1)"""
    check50.run("./replacement").stdin("5 2 4\n1 2 3 4 5", prompt=False).stdout("1 4 3 2 5", regex=False).exit(0)

@check50.check(test_compile)
def test2():
    """swaps elements correctly (Example 2)"""
    check50.run("./replacement").stdin("4 1 4\n5 3 2 6", prompt=False).stdout("6 3 2 5", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1"""
    check50.run("./replacement").stdin("1 1 1\n999", prompt=False).stdout("999", regex=False).exit(0)

@check50.check(test_compile)
def test_identity_swap():
    """handles swapping an element with itself (a = b)"""
    check50.run("./replacement").stdin("5 3 3\n1 2 3 4 5", prompt=False).stdout("1 2 3 4 5", regex=False).exit(0)

@check50.check(test_compile)
def test_endpoint_swap():
    """handles swapping first and last elements (a = 1, b = n)"""
    check50.run("./replacement").stdin("5 1 5\n10 20 30 40 50", prompt=False).stdout("50 20 30 40 10", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1000():
    """handles N = 1000 with swapping the endpoints"""
    stdin_data = "1000 1 1000\n" + " ".join(str(i) for i in range(1, 1001))
    expected_out = "1000 " + " ".join(str(i) for i in range(2, 1000)) + " 1"
    check50.run("./replacement").stdin(stdin_data, prompt=False).stdout(expected_out, regex=False).exit(0)

