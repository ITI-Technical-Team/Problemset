import check50

@check50.check()
def exists():
    """length.cpp exists"""
    check50.exists("length.cpp")

@check50.check(exists)
def test_compile():
    """length.cpp compiles successfully"""
    check50.run("g++ length.cpp -o length").exit(0)

@check50.check(test_compile)
def test_example1():
    """outputs correct sizes for 2 strings: 2 NewComers PortSaid"""
    check50.run("./length").stdin("2\nNewComers\nPortSaid", prompt=False).stdout("9\n8", regex=False).exit(0)

@check50.check(test_compile)
def test_extra1():
    """outputs size for 1 string: 1 hello"""
    check50.run("./length").stdin("1\nhello", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_extra2():
    """outputs sizes for 3 strings: 3 a bb ccc"""
    check50.run("./length").stdin("3\na\nbb\nccc", prompt=False).stdout("1\n2\n3", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1, minimal length string"""
    check50.run("./length").stdin("1\nx", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_large_length():
    """handles edge case N = 1, large string of length 1000"""
    check50.run("./length").stdin("1\n" + "y" * 1000, prompt=False).stdout("1000", regex=False).exit(0)

@check50.check(test_compile)
def test_multiple_various_sizes():
    """handles N = 5 with various string sizes"""
    check50.run("./length").stdin("5\na\nab\nabc\nabcd\nabcde", prompt=False).stdout("1\n2\n3\n4\n5", regex=False).exit(0)

