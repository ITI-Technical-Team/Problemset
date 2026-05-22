import check50

@check50.check()
def exists():
    """palindrome.cpp exists"""
    check50.exists("palindrome.cpp")

@check50.check(exists)
def test_example1():
    """outputs correct YES for abba"""
    check50.run("g++ palindrome.cpp -o palindrome && ./palindrome").stdin("abba", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(exists)
def test_example2():
    """outputs correct NO for itics50"""
    check50.run("g++ palindrome.cpp -o palindrome && ./palindrome").stdin("itics50", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(exists)
def test_example3():
    """outputs correct YES for mam"""
    check50.run("g++ palindrome.cpp -o palindrome && ./palindrome").stdin("mam", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(exists, timeout=1.0)
def test_efficiency():
    """handles very large strings efficiently"""
    N = 1000
    pali_str = "a" * N
    non_pali_str = "a" * (N-1) + "b"
    check50.run("g++ palindrome.cpp -o palindrome && ./palindrome").stdin(pali_str, prompt=False).stdout("YES", regex=False).exit(0)
    check50.run("g++ palindrome.cpp -o palindrome && ./palindrome").stdin(non_pali_str, prompt=False).stdout("NO", regex=False).exit(0)
