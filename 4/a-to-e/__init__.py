import check50

@check50.check()
def exists():
    """a-to-e.cpp exists"""
    check50.exists("a-to-e.cpp")

@check50.check(exists)
def test_example1():
    """handles input: 3 ace -> YES"""
    check50.run("g++ a-to-e.cpp -o a-to-e && ./a-to-e").stdin("3\nace", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(exists)
def test_extra1():
    """handles input with f: 4 abcf -> NO"""
    check50.run("g++ a-to-e.cpp -o a-to-e && ./a-to-e").stdin("4\nabcf", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(exists)
def test_extra2():
    """handles all valid chars: 5 abcde -> YES"""
    check50.run("g++ a-to-e.cpp -o a-to-e && ./a-to-e").stdin("5\nabcde", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(exists)
def test_extra3():
    """handles z: 1 z -> NO"""
    check50.run("g++ a-to-e.cpp -o a-to-e && ./a-to-e").stdin("1\nz", prompt=False).stdout("NO", regex=False).exit(0)
