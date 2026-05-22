import check50

@check50.check()
def exists():
    """replacement.cpp exists"""
    check50.exists("replacement.cpp")

@check50.check(exists)
def test1():
    """swaps elements correctly (Example 1)"""
    check50.run("g++ replacement.cpp -o replacement && ./replacement").stdin("5 2 4\n1 2 3 4 5", prompt=False).stdout("1 4 3 2 5", regex=False).exit(0)

@check50.check(exists)
def test2():
    """swaps elements correctly (Example 2)"""
    check50.run("g++ replacement.cpp -o replacement && ./replacement").stdin("4 1 4\n5 3 2 6", prompt=False).stdout("6 3 2 5", regex=False).exit(0)
