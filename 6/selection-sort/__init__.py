import check50

@check50.check()
def exists():
    """selection-sort.cpp exists"""
    check50.exists("selection-sort.cpp")

@check50.check(exists)
def test_compile():
    """selection-sort.cpp compiles successfully"""
    check50.run("g++ selection-sort.cpp -o selection-sort").exit(0)

@check50.check(test_compile)
def test_example():
    """sorts array correctly (Example)"""
    check50.run("./selection-sort").stdin("5\n3 6 1 10 5", prompt=False).stdout("1 3 5 6 10", regex=False).exit(0)

@check50.check(test_compile)
def test_already_sorted():
    """handles already sorted arrays"""
    check50.run("./selection-sort").stdin("4\n1 2 3 4", prompt=False).stdout("1 2 3 4", regex=False).exit(0)

@check50.check(test_compile)
def test_reverse_sorted():
    """handles reverse sorted arrays"""
    check50.run("./selection-sort").stdin("4\n4 3 2 1", prompt=False).stdout("1 2 3 4", regex=False).exit(0)

@check50.check(test_compile)
def test_small_positive():
    """handles small positive arrays with duplicates"""
    check50.run("./selection-sort").stdin("5\n10 50 1 5 1", prompt=False).stdout("1 1 5 10 50", regex=False).exit(0)

@check50.check(test_compile)
def test_mixed_longer():
    """handles a longer positive array with duplicates"""
    check50.run("./selection-sort").stdin("10\n8 3 3 2 7 10 5 2 9 1", prompt=False).stdout("1 2 2 3 3 5 7 8 9 10", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles minimal array size N = 1"""
    check50.run("./selection-sort").stdin("1\n999", prompt=False).stdout("999", regex=False).exit(0)


