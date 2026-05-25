import check50

@check50.check()
def exists():
    """minimum.cpp exists"""
    check50.exists("minimum.cpp")

@check50.check(exists)
def test_compile():
    """minimum.cpp compiles successfully"""
    check50.run("g++ minimum.cpp -o minimum").exit(0)

@check50.check(test_compile)
def test1():
    """handles input with negatives: 5 -> 3 -1 5 -13 -10"""
    check50.run("./minimum").stdin("5\n3 -1 5 -13 -10", prompt=False).stdout("-13", regex=False).exit(0)

@check50.check(test_compile)
def test2():
    """handles input with positives: 4 -> 2 4 6 8"""
    check50.run("./minimum").stdin("4\n2 4 6 8", prompt=False).stdout("2", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal size)"""
    check50.run("./minimum").stdin("1\n999", prompt=False).stdout("999", regex=False).exit(0)

@check50.check(test_compile)
def test_all_zeroes():
    """handles edge case of all zeroes"""
    check50.run("./minimum").stdin("5\n0 0 0 0 0", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_duplicate_minimum():
    """handles duplicates of the minimum value"""
    check50.run("./minimum").stdin("5\n4 2 5 2 6", prompt=False).stdout("2", regex=False).exit(0)

@check50.check(test_compile)
def test_all_negative():
    """handles all negative elements"""
    check50.run("./minimum").stdin("4\n-10 -20 -30 -40", prompt=False).stdout("-40", regex=False).exit(0)

