import check50


@check50.check()
def exists():
	"""equation.cpp exists"""
	check50.exists("equation.cpp")


@check50.check(exists)
def test1():
	"""4 2 5 3 -> 10"""
	check50.run("g++ equation.cpp -o equation && ./equation").stdin("4 2 5 3", prompt=False).stdout("10", regex=False).exit(0)


@check50.check(exists)
def test2():
	"""1 1 1 1 -> 1"""
	check50.run("g++ equation.cpp -o equation && ./equation").stdin("1 1 1 1", prompt=False).stdout("1", regex=False).exit(0)


@check50.check(exists)
def test3():
	"""0 0 0 0 -> 0"""
	check50.run("g++ equation.cpp -o equation && ./equation").stdin("0 0 0 0", prompt=False).stdout("0", regex=False).exit(0)


@check50.check(exists)
def test4():
	"""10 5 2 1 -> 51"""
	check50.run("g++ equation.cpp -o equation && ./equation").stdin("10 5 2 1", prompt=False).stdout("51", regex=False).exit(0)


@check50.check(exists)
def test5():
	"""3 2 1 0 -> 7"""
	check50.run("g++ equation.cpp -o equation && ./equation").stdin("3 2 1 0", prompt=False).stdout("7", regex=False).exit(0)

