import check50


@check50.check()
def exists():
    """summation.cpp exists"""
    check50.exists("summation.cpp")


@check50.check(exists)
def sums_5_numbers():
    """sums five numbers"""
    check50.run("g++ summation.cpp -o summation && ./summation").stdin("5\n2 4 3 1 5", prompt=False).stdout("15", regex=False).exit(0)


@check50.check(exists)
def sums_7_numbers():
    """sums seven numbers"""
    check50.run("g++ summation.cpp -o summation && ./summation").stdin("7\n1 5 2 10 -4 -3 6", prompt=False).stdout("17", regex=False).exit(0)
