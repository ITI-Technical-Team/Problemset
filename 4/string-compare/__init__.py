import check50

@check50.check()
def exists():
    """string-compare.cpp exists"""
    check50.exists("string-compare.cpp")

@check50.check(exists)
def test_example1():
    """5 1 -> Greater"""
    check50.run("g++ string-compare.cpp -o string-compare && ./string-compare").stdin("5 1", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(exists)
def test_example2():
    """5 5 -> Equal"""
    check50.run("g++ string-compare.cpp -o string-compare && ./string-compare").stdin("5 5", prompt=False).stdout("Equal", regex=False).exit(0)

@check50.check(exists)
def test_extra1():
    """-5 5 -> Less"""
    check50.run("g++ string-compare.cpp -o string-compare && ./string-compare").stdin("-5 5", prompt=False).stdout("Less", regex=False).exit(0)

@check50.check(exists)
def test_extra2():
    """-10 -20 -> Greater"""
    check50.run("g++ string-compare.cpp -o string-compare && ./string-compare").stdin("-10 -20", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(exists)
def test_extra3():
    """100 50 -> Greater"""
    check50.run("g++ string-compare.cpp -o string-compare && ./string-compare").stdin("100 50", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(exists)
def test_extra4():
    """0 0 -> Equal"""
    check50.run("g++ string-compare.cpp -o string-compare && ./string-compare").stdin("0 0", prompt=False).stdout("Equal", regex=False).exit(0)

@check50.check(exists)
def test_extra5():
    """1 5 -> Less"""
    check50.run("g++ string-compare.cpp -o string-compare && ./string-compare").stdin("1 5", prompt=False).stdout("Less", regex=False).exit(0)
