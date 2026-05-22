import check50

@check50.check()
def exists():
    """target-finder.cpp exists"""
    check50.exists("target-finder.cpp")

@check50.check(exists)
def test_example1():
    """outputs correct YES/NO for pair sums"""
    check50.run("g++ target-finder.cpp -o target-finder && ./target-finder").stdin("5 3\n1 2 3 4 5\n4 5\n3 3\n1 6", prompt=False).stdout("YES\nNO\nYES", regex=False).exit(0)

@check50.check(exists, timeout=1.5)
def test_efficiency():
    """tests efficiency over large arrays and queries"""
    from random import randint
    N, Q = 100000, 100000
    elements = " ".join(str(i) for i in range(1, N + 1))
    # Query sums that definitely don't exist
    queries = "\n".join(f"{N+10} {N+11}" for _ in range(Q))
    stdin_content = f"{N} {Q}\n{elements}\n{queries}"
    expected_out = "\n".join("NO" for _ in range(Q))
    check50.run("g++ -O2 target-finder.cpp -o target-finder && ./target-finder").stdin(stdin_content, prompt=False).stdout(expected_out, regex=False).exit(0)
