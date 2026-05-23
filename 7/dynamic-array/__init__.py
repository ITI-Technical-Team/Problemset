import check50

@check50.check()
def exists():
    """dynamic-array.cpp exists"""
    check50.exists("dynamic-array.cpp")

@check50.check(exists)
def test_example():
    """prints sequence order correctly (Example)"""
    check50.run("g++ dynamic-array.cpp -o dynamic-array && ./dynamic-array").stdin("5\n13\n2\n7\n11\n20\n-1", prompt=False).stdout("5 13 2 7 11 20", regex=False).exit(0)

@check50.check(exists)
def test_single_value():
    """handles a single value before sentinel"""
    check50.run("g++ dynamic-array.cpp -o dynamic-array && ./dynamic-array").stdin("42\n-1", prompt=False).stdout("42", regex=False).exit(0)

@check50.check(exists)
def test_duplicates():
    """handles duplicates and preserves order"""
    check50.run("g++ dynamic-array.cpp -o dynamic-array && ./dynamic-array").stdin("3\n3\n3\n7\n3\n-1", prompt=False).stdout("3 3 3 7 3", regex=False).exit(0)

@check50.check(exists)
def test_longer_mixed():
    """handles longer mixed sequence"""
    check50.run("g++ dynamic-array.cpp -o dynamic-array && ./dynamic-array").stdin("8\n1000000000\n1\n999\n5\n12\n12\n7\n2\n-1", prompt=False).stdout("8 1000000000 1 999 5 12 12 7 2", regex=False).exit(0)
