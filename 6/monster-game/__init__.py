import check50

@check50.check()
def exists():
    """monster-game.cpp exists"""
    check50.exists("monster-game.cpp")

@check50.check(exists)
def test_example():
    """counts defeated monsters correctly (Example)"""
    check50.run("g++ monster-game.cpp -o monster-game && ./monster-game").stdin("10\n5\n8 3 12 4 16", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(exists)
def test_defeat_all():
    """handles case where player can defeat all monsters"""
    check50.run("g++ monster-game.cpp -o monster-game && ./monster-game").stdin("100\n3\n10 20 30", prompt=False).stdout("3", regex=False).exit(0)

@check50.check(exists)
def test_defeat_none():
    """handles case where player cannot defeat any monsters"""
    check50.run("g++ monster-game.cpp -o monster-game && ./monster-game").stdin("5\n4\n10 10 10 10", prompt=False).stdout("0", regex=False).exit(0)

@check50.check(exists)
def test_strict_greater():
    """handles strict inequality rule properly (must be strictly greater health)"""
    check50.run("g++ monster-game.cpp -o monster-game && ./monster-game").stdin("10\n3\n9 10 11", prompt=False).stdout("1", regex=False).exit(0)
