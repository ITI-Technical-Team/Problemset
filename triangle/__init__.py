import check50


@check50.check()
def exists():
    """triangle.cpp exists"""
    check50.exists("triangle.cpp")


@check50.check(exists)
def prints_size_3():
    """prints a triangle of size 3"""
    check50.run("g++ triangle.cpp -o triangle && ./triangle").stdin("3", prompt=False).stdout("*\n**\n***", regex=False).exit(0)


@check50.check(exists)
def prints_size_5():
    """prints a triangle of size 5"""
    check50.run("g++ triangle.cpp -o triangle && ./triangle").stdin("5", prompt=False).stdout("*\n**\n***\n****\n*****", regex=False).exit(0)
