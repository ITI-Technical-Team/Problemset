import check50


@check50.check()
def exists():
    """hashes.cpp exists"""
    check50.exists("hashes.cpp")


@check50.check(exists)
def prints_3_hashes():
    """prints three hashes"""
    check50.run("g++ hashes.cpp -o hashes && ./hashes").stdin("3", prompt=False).stdout("###", regex=False).exit(0)


@check50.check(exists)
def prints_5_hashes():
    """prints five hashes"""
    check50.run("g++ hashes.cpp -o hashes && ./hashes").stdin("5", prompt=False).stdout("#####", regex=False).exit(0)
