import check50


@check50.check()
def exists():
	"""operations.cpp exists"""
	check50.exists("operations.cpp")


@check50.check(exists)
def test1():
	"""5 3 -> 8, 2, 15, 1"""
	check50.run("g++ operations.cpp -o operations && ./operations").stdin("5 3", prompt=False).stdout("8\n2\n15\n1", regex=False).exit(0)


@check50.check(exists)
def test2():
	"""10 4 -> 14, 6, 40, 2"""
	check50.run("g++ operations.cpp -o operations && ./operations").stdin("10 4", prompt=False).stdout("14\n6\n40\n2", regex=False).exit(0)


@check50.check(exists)
def test3():
	"""1 1 -> 2, 0, 1, 1"""
	check50.run("g++ operations.cpp -o operations && ./operations").stdin("1 1", prompt=False).stdout("2\n0\n1\n1", regex=False).exit(0)


@check50.check(exists)
def test4():
	"""5 5 -> 10, 0, 25, 1"""
	check50.run("g++ operations.cpp -o operations && ./operations").stdin("5 5", prompt=False).stdout("10\n0\n25\n1", regex=False).exit(0)


@check50.check(exists)
def test5():
	"""100000000 100000000 -> big results"""
	check50.run("g++ operations.cpp -o operations && ./operations").stdin("100000000 100000000", prompt=False).stdout("200000000\n0\n10000000000000000\n1", regex=False).exit(0)

