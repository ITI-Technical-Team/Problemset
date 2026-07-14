import check50

@check50.check()
def exists():
    """hashes.cpp exists"""
    check50.exists("hashes.cpp")

@check50.check(exists)
def test_compile():
    """hashes.cpp compiles successfully"""
    check50.run("g++ hashes.cpp -o hashes").exit(0)

@check50.check(test_compile)
def prints_3_hashes():
    """prints three hashes (Example 1)"""
    check50.run("./hashes").stdin("3", prompt=False).stdout("###", regex=False).exit(0)

@check50.check(test_compile)
def prints_5_hashes():
    """prints five hashes (Example 2)"""
    check50.run("./hashes").stdin("5", prompt=False).stdout("#####", regex=False).exit(0)

@check50.check(test_compile)
def test_n_1():
    """handles edge case N = 1 (minimal value)"""
    check50.run("./hashes").stdin("1", prompt=False).stdout("#", regex=False).exit(0)

@check50.check(test_compile)
def test_n_100():
    """handles edge case N = 100 (maximal value)"""
    check50.run("./hashes").stdin("100", prompt=False).stdout("#" * 100, regex=False).exit(0)
