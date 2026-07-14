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
    """outputs NO for newcomers"""
    check50.run("./palindrome").stdin("newcomers", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_example3():
    """outputs YES for mam"""
    check50.run("./palindrome").stdin("mam", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_single_char():
    """single character is always a palindrome -> YES"""
    check50.run("./palindrome").stdin("a", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_two_char_yes():
    """handles 2-character palindrome: aa -> YES"""
    check50.run("./palindrome").stdin("aa", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_two_char_no():
    """handles 2-character non-palindrome: ab -> NO"""
    check50.run("./palindrome").stdin("ab", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_large_yes():
    """handles large palindrome of length 1000"""
    check50.run("./palindrome").stdin("a" * 1000, prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile)
def test_large_no():
    """handles large non-palindrome of length 1000"""
    check50.run("./palindrome").stdin("a" * 500 + "b" + "a" * 499, prompt=False).stdout("NO", regex=False).exit(0)

