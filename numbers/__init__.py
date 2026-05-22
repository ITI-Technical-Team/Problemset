import check50


@check50.check()
def exists():
    """numbers.cpp exists"""
    check50.exists("numbers.cpp")


@check50.check(exists)
def prints_3():
    """prints numbers from 1 to 3"""
    check50.run("g++ numbers.cpp -o numbers && ./numbers").stdin("3", prompt=False).stdout("1 2 3", regex=False).exit(0)


@check50.check(exists)
def prints_5():
    """prints numbers from 1 to 5"""
    check50.run("g++ numbers.cpp -o numbers && ./numbers").stdin("5", prompt=False).stdout("1 2 3 4 5", regex=False).exit(0)
