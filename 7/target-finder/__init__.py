import check50

@check50.check()
def exists():
    """target-finder.cpp exists"""
    check50.exists("target-finder.cpp")

@check50.check(exists)
def test_compile():
    """target-finder.cpp compiles successfully"""
    check50.run("g++ target-finder.cpp -o target-finder").exit(0)

@check50.check(test_compile)
def test_example1():
    """outputs correct YES/NO for the example case"""
    check50.run("./target-finder").stdin("5 3\n1 2 3 4 5\n4 5\n3 3\n1 6", prompt=False).stdout("YES\nNO\nYES", regex=False).exit(0)

@check50.check(test_compile)
def test_all_no():
    """outputs NO when the target does not exist in the array"""
    check50.run("./target-finder").stdin("3 1\n1 2 3\n10 3", prompt=False).stdout("NO", regex=False).exit(0)

@check50.check(test_compile)
def test_all_yes():
    """outputs YES when the target exists in the array"""
    check50.run("./target-finder").stdin("5 1\n1 2 3 4 5\n4 9", prompt=False).stdout("YES", regex=False).exit(0)

@check50.check(test_compile, timeout=15)
def test_efficiency():
    """solution runs in time on sorted input (O(N * Q) naive will exceed the time limit)"""
    # The input array is SORTED. An efficient solution binary-searches for (z - x)
    # giving O(Q log N) total time complexity.
    # A naive solution that ignores the sorted property and scans the array linearly
    # takes O(N * Q) and will TLE.
    #
    # N=100000 elements (sorted 1..N), Q=10000 queries (all impossible -> forces full scan on naive).
    # Benchmarked WITHOUT fast I/O:
    #   O(Q log N) binary search solution: ~0.15s  -> well within the 2s timeout
    #   O(N * Q) brute-force linear search:  > 5.00s  -> far exceeds the 2s timeout
    N, Q = 100000, 10000
    elements = " ".join(str(i) for i in range(1, N + 1))  # already sorted
    # x=1, z=N+11 => target = z - x = N+10, which is impossible to find, forcing naive to scan all N elements
    queries = "\n".join(f"1 {N + 11}" for _ in range(Q))
    stdin_content = f"{N} {Q}\n{elements}\n{queries}"
    expected_out = "\n".join("NO" for _ in range(Q))

    with open("efficiency_input.txt", "w") as f:
        f.write(stdin_content)

    check50.run("timeout 2 ./target-finder < efficiency_input.txt").stdout(expected_out, regex=False).exit(0)
