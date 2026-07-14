import check50

@check50.check()
def exists():
	"""hello.cpp exists"""
	check50.exists("hello.cpp")

@check50.check(exists)
def test_compile():
	"""hello.cpp compiles successfully"""
	check50.run("g++ hello.cpp -o hello").exit(0)

@check50.check(test_compile)
def test1():
	"""Mohamed 24 -> Hello Mohamed, you are 24 years old."""
	check50.run("./hello").stdin("Mohamed 24", prompt=False).stdout("Hello Mohamed, you are 24 years old.", regex=False).exit(0)

@check50.check(test_compile)
def test2():
	"""Mazen 50 -> Hello Mazen, you are 50 years old."""
	check50.run("./hello").stdin("Mazen 50", prompt=False).stdout("Hello Mazen, you are 50 years old.", regex=False).exit(0)

@check50.check(test_compile)
def test3():
	"""John 30 -> Hello John, you are 30 years old."""
	check50.run("./hello").stdin("John 30", prompt=False).stdout("Hello John, you are 30 years old.", regex=False).exit(0)

@check50.check(test_compile)
def test4():
	"""Alice 22 -> Hello Alice, you are 22 years old."""
	check50.run("./hello").stdin("Alice 22", prompt=False).stdout("Hello Alice, you are 22 years old.", regex=False).exit(0)
