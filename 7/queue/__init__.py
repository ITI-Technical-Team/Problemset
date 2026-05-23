import check50

@check50.check()
def exists():
    """queue.cpp exists"""
    check50.exists("queue.cpp")

@check50.check(exists)
def test_example():
    """processes queue operations correctly (Example)"""
    check50.run("g++ queue.cpp -o queue && ./queue").stdin("5\n1 1\n1 2\n2\n2\n2", prompt=False).stdout("1\n2\nEmpty!", regex=False).exit(0)

@check50.check(exists)
def test_empty_then_use():
    """prints Empty! when dequeuing an empty queue"""
    check50.run("g++ queue.cpp -o queue && ./queue").stdin("4\n2\n1 5\n2\n2", prompt=False).stdout("Empty!\n5\nEmpty!", regex=False).exit(0)

@check50.check(exists)
def test_interleaved():
    """handles interleaved enqueue and dequeue"""
    check50.run("g++ queue.cpp -o queue && ./queue").stdin("7\n1 10\n1 20\n1 30\n2\n2\n1 40\n2", prompt=False).stdout("10\n20\n30", regex=False).exit(0)

@check50.check(exists)
def test_multiple_empty():
    """handles multiple empty dequeues"""
    check50.run("g++ queue.cpp -o queue && ./queue").stdin("5\n2\n2\n1 7\n2\n2", prompt=False).stdout("Empty!\nEmpty!\n7\nEmpty!", regex=False).exit(0)
