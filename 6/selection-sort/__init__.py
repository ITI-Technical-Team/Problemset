import check50

@check50.check()
def exists():
    """selection-sort.cpp exists"""
    check50.exists("selection-sort.cpp")

@check50.check(exists)
def test_example():
    """sorts array correctly (Example)"""
    check50.run("g++ selection-sort.cpp -o selection-sort && ./selection-sort").stdin("5\n3 6 1 10 5", prompt=False).stdout("1 3 5 6 10", regex=False).exit(0)

@check50.check(exists)
def test_already_sorted():
    """handles already sorted arrays"""
    check50.run("g++ selection-sort.cpp -o selection-sort && ./selection-sort").stdin("4\n1 2 3 4", prompt=False).stdout("1 2 3 4", regex=False).exit(0)

@check50.check(exists)
def test_reverse_sorted():
    """handles reverse sorted arrays"""
    check50.run("g++ selection-sort.cpp -o selection-sort && ./selection-sort").stdin("4\n4 3 2 1", prompt=False).stdout("1 2 3 4", regex=False).exit(0)

@check50.check(exists)
def test_negatives():
    """handles arrays with negative values and zeroes"""
    check50.run("g++ selection-sort.cpp -o selection-sort && ./selection-sort").stdin("5\n-1 -5 0 5 1", prompt=False).stdout("-5 -1 0 1 5", regex=False).exit(0)
