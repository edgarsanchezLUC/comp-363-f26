from heap363 import MinHeap363

# Given -- the test runner. Use it as run_tests("test_heap") or run_tests("test_ed").
def run_tests(prefix: str) -> None:
    """Run every test function whose name starts with `prefix`, print `ok` or
    `FAIL` for each, and finish with a count of how many passed."""
    # globals() is a dictionary of everything defined so far in this notebook:
    # every function and variable, stored under its name. .items() hands us each
    # (name, thing) pair, and sorted() puts them in alphabetical order so the
    # tests always run in the same order.
    # We keep a pair only if the name starts with `prefix` and the thing is a
    # function (callable), so that is how we find the tests without listing them.
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith(prefix) and callable(fn)]
    # Count the tests that pass, starting from zero.
    passed = 0
    for name, fn in tests:
        # try / except: run the test, but if it fails do not crash the whole
        # notebook. A failing assert makes Python "raise" an error. The code in
        # the try block is what we attempt; the code in except runs only if it fails.
        try:
            # Calling the test function. If every assert in it holds, it just
            # returns and prints nothing.
            fn()
            # We only reach this line when the test did not raise an error.
            print(f"ok    {name}")
            passed += 1
        except Exception as err:   # AssertionError, TypeError, IndexError...
            # `err` is the error that was raised. type(err).__name__ is its kind
            # (for a failed assert, AssertionError) and str(err) is the message
            # written after the comma in the assert, which says what went wrong.
            print(f"FAIL  {name}: {type(err).__name__}: {err}")
    # The summary line. The \n at the start leaves a blank line before it.
    print(f"\n{passed} of {len(tests)} checks passed")

# Given -- tests for the heap.
# The imports bring in two modules (ready-made sets of tools): `random` for
# random numbers and `inspect`, which a later test uses to read the source code
# of a function.
import inspect
import random


def heap_property_ok(heap: MinHeap363) -> bool:
    """True if every parent in heap.storage is <= both of its children."""
    # Not a test: a checking tool that several tests share. It looks directly
    # at the list, so it does not trust the heap's own methods to judge them.
    a = heap.storage
    # Assume the property holds until we find a pair that breaks it.
    ok = True
    # Visit every position except the root. Each one is a child of exactly one
    # parent, so checking each child against its parent checks every pair.
    for child in range(1, len(a)):
        # (child - 1) // 2 is the parent position. A parent greater than its
        # child breaks the minimum heap property.
        if a[(child - 1) // 2] > a[child]:
            ok = False
    return ok


# ---- The basics


def test_heap_empty():
    # Why: the failure cases in the interface table must behave as promised.
    h = MinHeap363()
    assert h.size() == 0, "a new heap has size 0"
    # `is None` asks whether the answer is exactly None, "no value".
    assert h.peek() is None, "peek on an empty heap returns None"
    assert h.get() is None, "get on an empty heap returns None"
    # A failed operation must leave everything as it was.
    assert h.size() == 0, "a failed get changes nothing"


def test_heap_single_value():
    # Why: the smallest possible heap is where an off-by-one hides, because the
    # only value is both the root and the last value in the list.
    h = MinHeap363()
    h.add(42)
    assert h.size() == 1
    assert h.peek() == 42, "peek returns the only value"
    # peek only looks; if it removed the value, the size would drop to 0.
    assert h.size() == 1, "peek does not remove"
    assert h.get() == 42, "get returns the only value"
    assert h.size() == 0, "and the heap is empty again"
    # Getting from the now-empty heap is the failure case again.
    assert h.get() is None


# ---- The two repairs


def test_heap_is_leaf():
    # Why: _is_leaf decides when _sink_down stops. We test it alone, on a list
    # we build by hand: [1, 2, 3, 4] is the pyramid
    #         1
    #       2   3
    #     4
    h = MinHeap363()
    # Setting the list directly, without add, builds this exact situation.
    h.storage = [1, 2, 3, 4]
    assert not h._is_leaf(0), "the root has two children"
    # Position 1 has its left child at 2 * 1 + 1 = 3, which is in the list.
    assert not h._is_leaf(1), "position 1 has a left child at 3"
    # Position 2 would have children at 5 and 6, past the end of the list.
    assert h._is_leaf(2), "position 2 would have children at 5 and 6"
    assert h._is_leaf(3), "position 3 is the last leaf"


def test_heap_bubble_up_class_example():
    # From class: 2, 8, 4 is a minimum heap; adding 1 floats to the root.
    # Why: this follows one value up two levels. The expected list can be
    # checked by hand: 1 lands at position 3, swaps with its parent 8 (position
    # 1), then with its parent 2 (position 0).
    h = MinHeap363()
    for v in [2, 8, 4]:
        h.add(v)
    h.add(1)
    # Comparing whole lists checks every position, not just the root.
    assert h.storage == [1, 2, 4, 8], f"expected [1, 2, 4, 8], got {h.storage}"


def test_heap_sink_down_swaps_with_smaller_child():
    # 3 moves to the root and must swap with 1 (the smaller child), not 2.
    # Why: swapping with the larger child would put 2 above 1 and break the
    # rule. Only a heap that picks the smaller child passes.
    h = MinHeap363()
    # A valid minimum heap built by hand:   0
    #                                     2   1
    #                                   3
    h.storage = [0, 2, 1, 3]
    # get removes 0, moves the last value (3) to the root, and sinks it.
    assert h.get() == 0
    assert h.storage == [1, 2, 3], f"expected [1, 2, 3], got {h.storage}"


# ---- Order


def test_heap_ascending_and_descending_adds():
    # Why: already-sorted input is the easiest case for add (nothing moves) and
    # reverse-sorted input is the hardest (everything floats to the top).
    # Both must give the same ordered output.
    for values in ([1, 2, 3, 4, 5, 6, 7], [7, 6, 5, 4, 3, 2, 1]):
        h = MinHeap363()
        for v in values:
            h.add(v)
        # One get per value added; `for _ in values` repeats len(values) times.
        out = [h.get() for _ in values]
        assert out == [1, 2, 3, 4, 5, 6, 7], f"added {values}, got {out}"


def test_heap_duplicates():
    # Why: the comparisons are strict (< and >), so equal values must not swap
    # forever or get lost. Repeated values must all come back.
    h = MinHeap363()
    for v in [2, 1, 2, 1, 2]:
        h.add(v)
    out = [h.get() for _ in range(5)]
    assert out == [1, 1, 2, 2, 2], f"got {out}"


def test_heap_random_matches_sorted():
    # Why: hand-picked examples can miss a case. Here we compare the heap with
    # a method we trust, Python's sorted(), on many random lists. The sizes 31,
    # 32 and 33 sit around a full bottom row of the pyramid (31 = 1+2+4+8+16
    # values), where mistakes with the last value tend to show up.
    random.seed(9)
    for n in [2, 3, 10, 31, 32, 33, 200]:
        # n random values between 0 and 100; with n = 200 there are many repeats.
        values = [random.randint(0, 100) for _ in range(n)]
        h = MinHeap363()
        for v in values:
            h.add(v)
        assert h.size() == n
        out = [h.get() for _ in range(n)]
        # sorted(values) is the known right answer: the same values in order.
        assert out == sorted(values), f"n={n}: values came out out of order"
        # Every value has been taken out, so one more get fails safely.
        assert h.get() is None


def test_heap_tuples():
    # The simulation stores (severity, arrival_minute) pairs. Python compares tuples
    # element by element, so a smaller first element wins and ties go to the second.
    # Why: this is the exact use the ED makes of the heap. Within one severity,
    # the patient who arrived earlier must come out first.
    h = MinHeap363()
    for patient in [(3, 1), (2, 2), (1, 3), (2, 4), (1, 5)]:
        h.add(patient)
    out = [h.get() for _ in range(5)]
    # Severity 1 first, oldest first: (1, 3) before (1, 5); then the 2s; then 3.
    assert out == [(1, 3), (1, 5), (2, 2), (2, 4), (3, 1)], f"got {out}"


# ---- The rule itself


def test_heap_property_holds():
    # Why: the other tests look at what comes out. This one looks at the list
    # itself after every single operation, so a heap that is broken inside,
    # even if it happens to give right answers, is caught.
    random.seed(363)
    h = MinHeap363()
    # 300 random operations, a mix of adds and gets.
    for _ in range(300):
        # random.random() is between 0 and 1: add about 60% of the time, and
        # get the other 40%, so the heap grows but also shrinks.
        if random.random() < 0.6:
            h.add(random.randint(-50, 50))
        else:
            h.get()
        # The checking tool above must still say yes, whatever just happened.
        assert heap_property_ok(h), f"heap property broken: {h.storage}"


# Run every function above whose name starts with "test_heap".
run_tests("test_heap")