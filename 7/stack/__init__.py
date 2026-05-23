import check50

@check50.check()
def exists():
    """stack.cpp exists"""
    check50.exists("stack.cpp")

@check50.check(exists)
def test_example():
    """processes stack operations correctly (Example)"""
    check50.run("g++ stack.cpp -o stack && ./stack").stdin("5\n1 1\n1 2\n2\n2\n2", prompt=False).stdout("2\n1\nEmpty!", regex=False).exit(0)

@check50.check(exists)
def test_empty_then_use():
    """prints Empty! when popping an empty stack"""
    check50.run("g++ stack.cpp -o stack && ./stack").stdin("4\n2\n1 5\n2\n2", prompt=False).stdout("Empty!\n5\nEmpty!", regex=False).exit(0)

@check50.check(exists)
def test_lifo():
    """checks LIFO ordering"""
    check50.run("g++ stack.cpp -o stack && ./stack").stdin("6\n1 1\n1 2\n1 3\n2\n2\n2", prompt=False).stdout("3\n2\n1", regex=False).exit(0)

@check50.check(exists)
def test_interleaved():
    """handles interleaved push and pop"""
    check50.run("g++ stack.cpp -o stack && ./stack").stdin("7\n1 10\n1 20\n2\n1 30\n2\n2\n2", prompt=False).stdout("20\n30\n10\nEmpty!", regex=False).exit(0)
