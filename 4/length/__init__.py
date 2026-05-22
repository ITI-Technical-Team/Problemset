import check50

@check50.check()
def exists():
    """length.cpp exists"""
    check50.exists("length.cpp")

@check50.check(exists)
def test_example1():
    """outputs correct sizes for 2 strings: 2 NewComers PortSaid"""
    check50.run("g++ length.cpp -o length && ./length").stdin("2\nNewComers\nPortSaid", prompt=False).stdout("9\n8", regex=False).exit(0)

@check50.check(exists)
def test_extra1():
    """outputs size for 1 string: 1 hello"""
    check50.run("g++ length.cpp -o length && ./length").stdin("1\nhello", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(exists)
def test_extra2():
    """outputs sizes for 3 strings: 3 a bb ccc"""
    check50.run("g++ length.cpp -o length && ./length").stdin("3\na\nbb\nccc", prompt=False).stdout("1\n2\n3", regex=False).exit(0)
