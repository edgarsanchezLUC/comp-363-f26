from ed_simulation import *
import inspect
import random

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

# Given -- tests for the simulation. Run this cell after every change.
#
# How to read a test: the lines before the asserts set up a situation (a
# number of doctors, an arrival rate, a number of minutes, a seed); the asserts
# say what must be true afterwards. The seed is different in each test only so
# that the tests do not all examine the same week.


# ---- The random helpers
# Each helper is tested on its own, before simulate() uses it, so a mistake in a
# helper is found here and not hidden inside a whole simulated week.


def test_ed_random_tier_follows_weights():
    # Why: random_tier must pick severity 1, 2 and 3 in the proportions of
    # TIER_WEIGHTS. A single pick proves nothing, so we make many.
    # Fixing the seed makes this test give the same answer every time.
    random.seed(1)
    # 20,000 picks. `for _ in range(...)` repeats the call that many times; the
    # underscore means we do not need the loop counter.
    picks = [random_tier() for _ in range(20_000)]
    # zip pairs each severity with its weight: (1, 0.10), (2, 0.35), (3, 0.55).
    for tier, weight in zip(TIERS, TIER_WEIGHTS):
        # The share of picks that were this severity.
        share = picks.count(tier) / len(picks)
        # Random results never match a weight exactly, so we accept a margin of
        # 0.02. With 20,000 picks, a correct helper stays well inside it; a
        # helper that ignores the weights does not.
        assert abs(share - weight) < 0.02, f"tier {tier}: share {share:.3f}, expected about {weight}"


def test_ed_arrival_happens_extremes_and_rate():
    # Why: arrival_happens(p) must be True with probability p. The two extremes
    # have exact answers, so we test those exactly; the middle we test as a rate.
    random.seed(2)
    # Probability 0 must never happen. any(...) is true if even one call came
    # back True, so `not any(...)` says none of the 1000 calls did.
    assert not any(arrival_happens(0.0) for _ in range(1000)), "probability 0 never happens"
    # Probability 1 must always happen: all(...) needs every one of the 1000.
    assert all(arrival_happens(1.0) for _ in range(1000)), "probability 1 always happens"
    # In between, count the Trues (True counts as 1 when we add) and divide.
    share = sum(arrival_happens(0.25) for _ in range(20_000)) / 20_000
    # About a quarter of the calls should be True, give or take 0.02.
    assert abs(share - 0.25) < 0.02, f"probability 0.25 happened {share:.3f} of the time"


def test_ed_treatment_minutes_in_range():
    # Why: a treatment time must fall inside the interval for its severity, and
    # the ends of the interval must be reachable (an off-by-one in randint or
    # in your range would make the longest or shortest time impossible).
    random.seed(3)
    for tier in TIERS:
        # The interval for this severity, from the settings cell.
        low, high = TREATMENT_MINUTES[tier]
        # Draw 5000 times; the braces make a set, which keeps each different
        # value once, so `seen` is the collection of all times that occurred.
        seen = {treatment_minutes(tier) for _ in range(5000)}
        # Nothing shorter than low or longer than high ever appeared.
        assert min(seen) >= low and max(seen) <= high, f"tier {tier}: out of [{low}, {high}]"
        # And both ends did appear: 5000 draws from an interval of at most 121
        # values will almost certainly hit both.
        assert low in seen and high in seen, f"tier {tier}: both ends must be possible"


# ---- The bookkeeping


def test_ed_nobody_arrives():
    # Why: with arrival_prob = 0 the ED stays empty, so every counter must be
    # exactly zero. This catches counters that start at the wrong value, or
    # that change without a patient.
    stats = simulate(num_doctors=3, arrival_prob=0.0, minutes=600, seed=4)
    for tier in TIERS:
        # Comparing two dictionaries: equal only if every key has the same value.
        assert stats[tier] == {"arrived": 0, "seen": 0, "total_wait": 0, "still_waiting": 0, "turned_away": 0}
    room = stats["room"]
    # An empty room has no peak and never became full; `is None` is how we ask
    # whether first_full_minute still holds None ("it never happened").
    assert room["peak_waiting"] == 0 and room["first_full_minute"] is None
    assert room["waiting_sum"] == 0 and room["busy_sum"] == 0


def test_ed_everyone_is_counted():
    # Why: this is the most important test. Nobody may vanish: every patient who
    # arrived is in exactly one of three groups when the clock stops.
    # 4 doctors and a busy arrival rate mean all three groups will occur.
    stats = simulate(num_doctors=4, arrival_prob=0.3, minutes=2000, seed=5)
    # About 0.3 x 2000 = 600 patients should arrive. More than 400 shows that
    # arrivals really happen at the rate you were given.
    assert sum(stats[t]["arrived"] for t in TIERS) > 400, "about 600 arrivals expected"
    for tier in TIERS:
        s = stats[tier]
        # arrived = seen + still waiting + turned away. If this fails, a patient
        # was counted twice or not at all: check the turned-away branch, and
        # that you count the patients still in the heap after the loop.
        assert s["arrived"] == s["seen"] + s["still_waiting"] + s["turned_away"], f"tier {tier}: {s}"


# ---- The clock and the doctors


def test_ed_plenty_of_doctors_means_one_minute_wait():
    # Why: when there is no shortage of doctors, the wait comes only from the
    # order of the steps inside one minute. Treatment comes before arrival in
    # each minute, so a patient who arrives in minute m is called in at m + 1.
    # (1000 doctors, but at most one arrival per minute.)
    stats = simulate(num_doctors=1000, arrival_prob=0.5, minutes=500, seed=6)
    for tier in TIERS:
        s = stats[tier]
        # Make sure the test is meaningful: this severity did have patients.
        assert s["arrived"] > 0
        # Everyone waited exactly 1 minute, so the total wait equals the number
        # of patients seen (1 minute each).
        assert s["total_wait"] == s["seen"], f"tier {tier}: everyone should wait exactly 1 minute: {s}"
    # Only a patient who arrived in the very last minute can still be waiting,
    # because the clock stopped before the doctors could call them in.
    assert sum(stats[t]["still_waiting"] for t in TIERS) <= 1, "only the last minute's arrival can still be waiting"


def test_ed_statistics_are_possible():
    # Why: the per-minute statistics have hard limits. Here they are checked
    # against what could physically happen, which catches updating them at the
    # wrong moment, or twice a minute.
    doctors, minutes = 4, 2000
    stats = simulate(num_doctors=doctors, arrival_prob=0.3, minutes=minutes, capacity=20, seed=5)
    room = stats["room"]
    # Doctor-minutes busy: more than none (they had patients), and never more
    # than every doctor being busy in every minute. A chained comparison
    # `0 < x <= y` means both `0 < x` and `x <= y`.
    assert 0 < room["busy_sum"] <= doctors * minutes, f"busy_sum {room['busy_sum']}"
    # Waiting-room size added up over the minutes: never more than a full room
    # (20 patients) in every minute.
    assert 0 < room["waiting_sum"] <= 20 * minutes, f"waiting_sum {room['waiting_sum']}"
    # The peak is at least 1 (somebody waited) and never above the capacity.
    assert 0 < room["peak_waiting"] <= 20


def test_ed_overloaded_doctor_is_always_busy():
    # Why: one doctor facing a flood of patients should never be idle, so
    # busy_sum should be nearly one for every minute. It checks that you count a
    # doctor as busy for the whole treatment, not just the first minute of it.
    stats = simulate(num_doctors=1, arrival_prob=0.9, minutes=3000, capacity=10, seed=3)
    # 95% of 3000 minutes, not 100%: the doctor really is idle in the first
    # minute, before the first patient has arrived.
    assert stats["room"]["busy_sum"] >= 0.95 * 3000, f"busy_sum {stats['room']['busy_sum']} of 3000"


# ---- The waiting room


def test_ed_small_waiting_room_turns_patients_away():
    # Why: one doctor, half a patient per minute and a room of 5 seats is far
    # more than the ED can handle, so the room must fill and refuse people.
    stats = simulate(num_doctors=1, arrival_prob=0.5, minutes=1000, capacity=5, seed=9)
    room = stats["room"]
    # Somebody must have been turned away.
    assert sum(stats[t]["turned_away"] for t in TIERS) > 0, "a 5-seat room with 1 doctor must turn patients away"
    # The peak must be exactly the capacity: reaching it shows the room filled,
    # and never exceeding it shows nobody was added to a full room.
    assert room["peak_waiting"] == 5, f"peak {room['peak_waiting']}, expected exactly the capacity, 5"
    # The room filled at some minute, so first_full_minute is no longer None.
    assert room["first_full_minute"] is not None
    # Turned-away patients still arrived, so they still have to balance.
    for tier in TIERS:
        s = stats[tier]
        assert s["arrived"] == s["seen"] + s["still_waiting"] + s["turned_away"], f"tier {tier}: {s}"


def test_ed_big_waiting_room_never_fills():
    # Why: the opposite case. With 1000 doctors the room is almost always
    # empty, so nobody may be turned away, even though the capacity is only 50.
    # It catches a turn-away rule that fires when it should not.
    stats = simulate(num_doctors=1000, arrival_prob=0.5, minutes=500, capacity=50, seed=6)
    # all(...) is true when every severity has zero turned away.
    assert all(stats[t]["turned_away"] == 0 for t in TIERS)
    # The room was never full, so first_full_minute is still None.
    assert stats["room"]["first_full_minute"] is None
    # A patient waits one minute at most, and only one arrives per minute.
    assert stats["room"]["peak_waiting"] <= 1, "with 1000 doctors at most one patient waits, for one minute"


# ---- The priority queue


def test_ed_priority_matters_when_busy():
    # Why: the whole point of the heap. In a busy week, severe patients must be
    # seen sooner than mild ones. 11 doctors is busy but not overwhelmed, so
    # every severity gets seen and has an average wait to compare.
    stats = simulate(num_doctors=11, arrival_prob=0.25, minutes=SIM_MINUTES, seed=7)
    # The average wait of each severity, in the order of TIERS.
    waits = [average_wait(stats, tier) for tier in TIERS]
    # average_wait gives None when nobody of a severity was seen.
    assert None not in waits, f"every tier should have patients seen: {waits}"
    # A life-threatening patient should not wait more than half an hour.
    assert waits[0] < 30, f"life-threatening waited {waits[0]:.0f} min on average"
    # The chain says: severity 1 waits less than 2, and 2 waits less than 3.
    # If the waits come out the other way round or all equal, the heap is not
    # being asked for the most urgent patient.
    assert waits[0] < waits[1] < waits[2], f"waits should grow with the tier number: {waits}"


def test_ed_uses_the_heap():
    # Why: the assignment is about using the heap, and a sorted list would
    # produce the same numbers, so we look at the source code of simulate itself.
    # inspect.getsource returns the text of the function as one long string.
    src = inspect.getsource(simulate)
    # The waiting room must be created from our class.
    assert "MinHeap363()" in src, "the waiting room must be a MinHeap363"
    # And the shortcuts must be absent from the text.
    for banned in ["heapq", "sorted(", ".sort("]:
        assert banned not in src, f"simulate may not use {banned}"


# ---- The seed


def test_ed_same_seed_same_week():
    # Why: simulate calls random.seed(seed), so two runs with the same seed
    # must produce exactly the same week. This is what makes experiments
    # repeatable. It fails when randomness comes from somewhere simulate did
    # not seed, or when the results depend on anything that changes between runs.
    a = simulate(num_doctors=10, arrival_prob=0.25, minutes=3000, seed=8)
    b = simulate(num_doctors=10, arrival_prob=0.25, minutes=3000, seed=8)
    # The two results are dictionaries, so == compares every value inside.
    assert a == b, "the same seed must reproduce the same results"


# Run every function above whose name starts with "test_ed".
run_tests("test_ed")