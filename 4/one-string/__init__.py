import check50

@check50.check()
def exists():
    """one-string.cpp exists"""
    check50.exists("one-string.cpp")

@check50.check(exists)
def test_example1():
    """concatenates string and sheet -> stringsheet"""
    check50.run("g++ one-string.cpp -o one-string && ./one-string").stdin("string\nsheet", prompt=False).stdout("stringsheet", regex=False).exit(0)

@check50.check(exists)
def test_extra1():
    """concatenates a and b -> ab"""
    check50.run("g++ one-string.cpp -o one-string && ./one-string").stdin("a\nb", prompt=False).stdout("ab", regex=False).exit(0)

@check50.check(exists)
def test_extra2():
    """concatenates hello and world -> helloworld"""
    check50.run("g++ one-string.cpp -o one-string && ./one-string").stdin("hello\nworld", prompt=False).stdout("helloworld", regex=False).exit(0)
