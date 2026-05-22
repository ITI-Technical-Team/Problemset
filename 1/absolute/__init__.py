import check50


@check50.check()
def exists():
	"""absolute.cpp exists"""
	check50.exists("absolute.cpp")


@check50.check(exists)
def test1():
	"""handles input 4 7 -> 3"""
	check50.run("g++ absolute.cpp -o absolute && ./absolute").stdin("4 7", prompt=False).stdout("3", regex=False).exit(0)


@check50.check(exists)
def test2():
	"""handles input 9 2 -> 7"""
	check50.run("g++ absolute.cpp -o absolute && ./absolute").stdin("9 2", prompt=False).stdout("7", regex=False).exit(0)


@check50.check(exists)
def test3():
	"""handles input 5 5 -> 0"""
	check50.run("g++ absolute.cpp -o absolute && ./absolute").stdin("5 5", prompt=False).stdout("0", regex=False).exit(0)


@check50.check(exists)
def test4():
	"""handles input 1000000 999999 -> 1"""
	check50.run("g++ absolute.cpp -o absolute && ./absolute").stdin("1000000 999999", prompt=False).stdout("1", regex=False).exit(0)


@check50.check(exists)
def test5():
	"""handles input 1000000 1000000 -> 0"""
	check50.run("g++ absolute.cpp -o absolute && ./absolute").stdin("1000000 1000000", prompt=False).stdout("0", regex=False).exit(0)

