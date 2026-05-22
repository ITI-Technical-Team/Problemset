import check50

@check50.check()
def exists():
    """minimum.cpp exists"""
    check50.exists("minimum.cpp")

@check50.check(exists)
def test1():
    """handles input with negatives: 5 -> 3 -1 5 -13 -10"""
    check50.run("g++ minimum.cpp -o minimum && ./minimum").stdin("5\n3 -1 5 -13 -10", prompt=False).stdout("-13", regex=False).exit(0)

@check50.check(exists)
def test2():
    """handles input with positives: 4 -> 2 4 6 8"""
    check50.run("g++ minimum.cpp -o minimum && ./minimum").stdin("4\n2 4 6 8", prompt=False).stdout("2", regex=False).exit(0)
