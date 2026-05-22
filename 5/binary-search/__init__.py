import check50

@check50.check()
def exists():
    """binary-search.cpp exists"""
    check50.exists("binary-search.cpp")

@check50.check(exists)
def test_example1():
    """outputs correct YES/NO for multiple queries"""
    check50.run("g++ binary-search.cpp -o binary-search && ./binary-search").stdin("5 3\n1 2 3 4 5\n5\n3\n6", prompt=False).stdout("YES\nYES\nNO", regex=False).exit(0)

@check50.check(exists, timeout=1.5)
def test_efficiency():
    """tests efficiency over large number of queries (detects O(N^2) solutions)"""
    # 100k elements, 100k queries. Linear search would TLE.
    N, Q = 100000, 100000
    elements = " ".join(str(i) for i in range(1, N + 1))
    queries = "\n".join("-1" for _ in range(Q))
    stdin_content = f"{N} {Q}\n{elements}\n{queries}"
    expected_out = "\n".join("NO" for _ in range(Q))
    check50.run("g++ -O2 binary-search.cpp -o binary-search && ./binary-search").stdin(stdin_content, prompt=False).stdout(expected_out, regex=False).exit(0)
