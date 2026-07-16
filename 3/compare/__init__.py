import check50

class RobustRun(check50.run):
    def __init__(self, *args, **kwargs):
        self._waited = False
        super().__init__(*args, **kwargs)

    def _wait(self, timeout=5):
        if self._waited:
            return self
        super()._wait(timeout)
        self._waited = True
        return self

    def stdout(self, output=None, *args, **kwargs):
        if output is not None and not kwargs.get("regex", True):
            expected_str = str(output)
            out = super().stdout(output=None)
            if out.split() != expected_str.split():
                raise check50.Mismatch(expected_str, out)
            return self
        return super().stdout(output, *args, **kwargs)

check50.run = RobustRun

@check50.check()
def exists():
	"""compare.cpp exists"""
	check50.exists("compare.cpp")

@check50.check(exists)
def test_compile():
	"""compare.cpp compiles successfully"""
	check50.run("g++ -O2 -Wall -Werror compare.cpp -o compare").exit(0)

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
