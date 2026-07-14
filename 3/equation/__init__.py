import check50

@check50.check()
def exists():
	"""equation.cpp exists"""
	check50.exists("equation.cpp")

@check50.check(exists)
def test_compile():
	"""equation.cpp compiles successfully"""
	check50.run("g++ equation.cpp -o equation").exit(0)

@check50.check(test_compile)
def test1():
	"""4 2 5 3 -> 10"""
	check50.run("./equation").stdin("4 2 5 3", prompt=False).stdout("10", regex=False).exit(0)

@check50.check(test_compile)
def test2():
	"""1 1 1 1 -> 1"""
	check50.run("./equation").stdin("1 1 1 1", prompt=False).stdout("1", regex=False).exit(0)

@check50.check(test_compile)
def test3():
	"""2 2 2 2 -> 4"""
	check50.run("./equation").stdin("2 2 2 2", prompt=False).stdout("4", regex=False).exit(0)

@check50.check(test_compile)
def test4():
	"""10 5 2 1 -> 51"""
	check50.run("./equation").stdin("10 5 2 1", prompt=False).stdout("51", regex=False).exit(0)

@check50.check(test_compile)
def test5():
	"""3 2 1 1 -> 6"""
	check50.run("./equation").stdin("3 2 1 1", prompt=False).stdout("6", regex=False).exit(0)
