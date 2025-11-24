import check50


@check50.check()
def exists():
    """hello.cpp exists"""
    check50.exists("hello.cpp")


@check50.check(exists)
def compiles():
    """hello.cpp compiles with g++"""
    check50.run("g++ -std=c++17 hello.cpp -o hello").exit(0)


@check50.check(compiles)
def prints_hello_world():
    """prints 'hello world'"""
    check50.run("./hello").stdout("hello world", regex=False).exit(0)
