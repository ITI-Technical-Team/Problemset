import check50

@check50.check()
def exists():
    """bubble-sort.cpp exists"""
    check50.exists("bubble-sort.cpp")

@check50.check(exists)
def test_example():
    """sorts array correctly (Example)"""
    check50.run("g++ bubble-sort.cpp -o bubble-sort && ./bubble-sort").stdin("5\n3 6 1 10 5", prompt=False).stdout("1 3 5 6 10", regex=False).exit(0)

@check50.check(exists)
def test_already_sorted():
    """handles already sorted arrays"""
    check50.run("g++ bubble-sort.cpp -o bubble-sort && ./bubble-sort").stdin("4\n1 2 3 4", prompt=False).stdout("1 2 3 4", regex=False).exit(0)

@check50.check(exists)
def test_reverse_sorted():
    """handles reverse sorted arrays"""
    check50.run("g++ bubble-sort.cpp -o bubble-sort && ./bubble-sort").stdin("4\n4 3 2 1", prompt=False).stdout("1 2 3 4", regex=False).exit(0)

@check50.check(exists)
def test_negatives():
    """handles arrays with negative values and zeroes"""
    check50.run("g++ bubble-sort.cpp -o bubble-sort && ./bubble-sort").stdin("5\n-1 -5 0 5 1", prompt=False).stdout("-5 -1 0 1 5", regex=False).exit(0)

@check50.check(exists)
def test_mixed_longer():
    """handles a longer mixed array with duplicates"""
    check50.run("g++ bubble-sort.cpp -o bubble-sort && ./bubble-sort").stdin("10\n8 3 3 -2 7 0 5 -2 9 1", prompt=False).stdout("-2 -2 0 1 3 3 5 7 8 9", regex=False).exit(0)
