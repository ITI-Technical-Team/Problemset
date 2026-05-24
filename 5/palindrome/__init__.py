import check50

@check50.check()
def exists():
    """palindrome.cpp exists"""
    check50.exists("palindrome.cpp")

@check50.check(exists)
def test_compile():
    """palindrome.cpp compiles successfully"""
    check50.run("g++ palindrome.cpp -o palindrome").exit(0)

@check50.check(test_compile)
def test_example1():
    """outputs YES for abba"""
    check50.run("./palindrome").stdin("abba", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_example2():
    """outputs NO for itics50"""
    check50.run("./palindrome").stdin("itics50", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_example3():
    """outputs YES for mam"""
    check50.run("./palindrome").stdin("mam", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_single_char():
    """single character is always a palindrome -> YES"""
    check50.run("./palindrome").stdin("a", prompt=False).stdout("YES", regex=False).exit(0)
