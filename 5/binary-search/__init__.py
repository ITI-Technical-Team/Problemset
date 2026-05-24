import check50

@check50.check()
def exists():
    """binary-search.cpp exists"""
    check50.exists("binary-search.cpp")

@check50.check(exists)
def test_compile():
    """binary-search.cpp compiles successfully"""
    check50.run("g++ binary-search.cpp -o binary-search").exit(0)

@check50.check(test_compile)
def test_example1():
    """outputs correct YES/NO for multiple queries"""
    check50.run("./binary-search").stdin("5 3\n1 2 3 4 5\n5\n3\n6", prompt=False).stdout("YES\nYES\nNO", regex=False).exit(0)

@check50.check(test_compile, timeout=15)
def test_efficiency():
    """solution runs in time on large input (O(N*Q) solutions will exceed the time limit)"""
    # N=100000 elements, Q=10000 queries (all missing: -1).
    # Benchmarked WITHOUT fast I/O:
    #   O(Q log N) binary search: ~0.13s  -> well within the 2s timeout
    #   O(Q * N)  linear  search: ~6.00s  -> far exceeds the 2s timeout
    N, Q = 100000, 10000
    elements = " ".join(str(i) for i in range(1, N + 1))
    queries = "\n".join("-1" for _ in range(Q))
    stdin_content = f"{N} {Q}\n{elements}\n{queries}"
    expected_out = "\n".join("NO" for _ in range(Q))

    # Write input to a file to avoid pipe buffer deadlocks with large stdin.
    with open("efficiency_input.txt", "w") as f:
        f.write(stdin_content)

    # 'timeout 2' enforces a strict 2-second wall-clock limit on the student binary.
    # Exit code 124 means the process was killed -> check50 sees a non-zero exit.
    check50.run("timeout 2 ./binary-search < efficiency_input.txt").stdout(expected_out, regex=False).exit(0)
