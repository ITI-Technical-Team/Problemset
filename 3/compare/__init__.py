import check50

@check50.check()
def exists():
	"""compare.cpp exists"""
	check50.exists("compare.cpp")

@check50.check(exists)
def test_compile():
	"""compare.cpp compiles successfully"""
	check50.run("g++ compare.cpp -o compare").exit(0)

@check50.check(test_compile)
def test1():
	"""5 1 -> Greater"""
	check50.run("./compare").stdin("5 1", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(test_compile)
def test2():
	"""5 5 -> Equal"""
	check50.run("./compare").stdin("5 5", prompt=False).stdout("Equal", regex=False).exit(0)

@check50.check(test_compile)
def test3():
	"""4 9 -> Less"""
	check50.run("./compare").stdin("4 9", prompt=False).stdout("Less", regex=False).exit(0)

@check50.check(test_compile)
def test4():
	"""0 0 -> Equal"""
	check50.run("./compare").stdin("0 0", prompt=False).stdout("Equal", regex=False).exit(0)

@check50.check(test_compile)
def test5():
	"""-1 1 -> Less"""
	check50.run("./compare").stdin("-1 1", prompt=False).stdout("Less", regex=False).exit(0)

@check50.check(test_compile)
def test6():
	"""-5 -5 -> Equal"""
	check50.run("./compare").stdin("-5 -5", prompt=False).stdout("Equal", regex=False).exit(0)

@check50.check(test_compile)
def test7():
	"""-10 -20 -> Greater"""
	check50.run("./compare").stdin("-10 -20", prompt=False).stdout("Greater", regex=False).exit(0)

@check50.check(test_compile)
def test8():
	"""100 50 -> Greater"""
	check50.run("./compare").stdin("100 50", prompt=False).stdout("Greater", regex=False).exit(0)
