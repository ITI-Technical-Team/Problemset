import check50

@check50.check()
def exists():
    """count.cpp exists"""
    check50.exists("count.cpp")

@check50.check(exists)
def test_compile():
    """count.cpp compiles successfully"""
    check50.run("g++ count.cpp -o count").exit(0)

@check50.check(test_compile)
def test_example1():
    """counts 'l' in 'hello' -> 2"""
    check50.run("./count").stdin("hello\nl", prompt=False).stdout("2", regex=False).exit(0)

@check50.check(test_compile)
def test_extra1():
    """counts 'z' in 'hello' -> 0"""
    check50.run("./count").stdin("hello\nz", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_extra2():
    """counts 'a' in 'aaaaa' -> 5"""
    check50.run("./count").stdin("aaaaa\na", prompt=False).stdout("5", regex=False).exit(0)

@check50.check(test_compile)
def test_extra3():
    """counts 'b' in 'abcde' -> 1"""
    check50.run("./count").stdin("abcde\nb", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_match():
    """handles minimal string with a match: a, count 'a' -> 1"""
    check50.run("./count").stdin("a\na", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test_minimal_no_match():
    """handles minimal string with no match: a, count 'b' -> 0"""
    check50.run("./count").stdin("a\nb", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_case_sensitivity():
    """handles case sensitivity: A, count 'a' -> 0"""
    check50.run("./count").stdin("A\na", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(test_compile)
def test_large_count():
    """handles large string N = 1000 all matching"""
    check50.run("./count").stdin("x" * 1000 + "\nx", prompt=False).stdout("1000", regex=False).exit(0)

