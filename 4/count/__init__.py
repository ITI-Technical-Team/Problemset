import check50

@check50.check()
def exists():
    """count.cpp exists"""
    check50.exists("count.cpp")

@check50.check(exists)
def test_example1():
    """counts 'l' in 'hello' -> 2"""
    check50.run("g++ count.cpp -o count && ./count").stdin("hello\nl", prompt=False).stdout("2", regex=False).exit(0)

@check50.check(exists)
def test_extra1():
    """counts 'z' in 'hello' -> 0"""
    check50.run("g++ count.cpp -o count && ./count").stdin("hello\nz", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(exists)
def test_extra2():
    """counts 'a' in 'aaaaa' -> 5"""
    check50.run("g++ count.cpp -o count && ./count").stdin("aaaaa\na", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(exists)
def test_extra3():
    """counts 'b' in 'abcde' -> 1"""
    check50.run("g++ count.cpp -o count && ./count").stdin("abcde\nb", prompt=False).stdout("1", regex=False).exit(0)
