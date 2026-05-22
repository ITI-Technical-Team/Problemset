import check50

@check50.check()
def exists():
    """print-kth-element.cpp exists"""
    check50.exists("print-kth-element.cpp")

@check50.check(exists)
def test1():
    """finds 2nd element in 6 elements"""
    check50.run("g++ print-kth-element.cpp -o print-kth-element && ./print-kth-element").stdin("6 2\n1 2 3 4 5 6", prompt=False).stdout("2", regex=False).exit(0)

@check50.check(exists)
def test2():
    """finds 1st element in 3 elements"""
    check50.run("g++ print-kth-element.cpp -o print-kth-element && ./print-kth-element").stdin("3 1\n5 22 1", prompt=False).stdout("5", regex=False).exit(0)
