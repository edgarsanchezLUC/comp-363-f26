"""SOLUTION -- Week 9, emergency department simulation, posted after the deadline.

ed_simulation.py: the settings and the report functions are given; the three
random helpers and simulate() are the solution.
"""
import random

from heap363 import MinHeap363

# Given -- simulation settings.
LIFE_THREATENING = 1
SEVERE = 2
NON_LIFE_THREATENING = 3
TIERS = [LIFE_THREATENING, SEVERE, NON_LIFE_THREATENING]

# Share of arrivals with each severity, in the same order as TIERS. Must add up to 1.
TIER_WEIGHTS = [0.10, 0.35, 0.55]

# Treatment length in minutes for each severity: (shortest, longest), inclusive.
TREATMENT_MINUTES = {
    LIFE_THREATENING: (60, 180),
    SEVERE: (30, 90),
    NON_LIFE_THREATENING: (10, 30),
}

ARRIVAL_PROB = 0.25          # chance of one arrival in any given minute (about 15 per hour)
NUM_DOCTORS = 12
SIM_MINUTES = 7 * 24 * 60    # one week
SEED = 363                   # same seed -> same "random" week, so runs can be compared

# Most patients the waiting room can hold at once. PLACEHOLDER.
WAITING_ROOM_CAPACITY = 60

# Whole-run constants for the bookkeeping below.
ROOM = "room"                 # key of the room/doctor statistics entry
NO_SEED = None


def random_tier() -> int:
    """Return a random severity from TIERS, chosen according to TIER_WEIGHTS."""
    # choices() returns a list of picks (one, by default); [0] is the item.
    tier = random.choices(TIERS, weights=TIER_WEIGHTS)[0]
    return tier


def arrival_happens(arrival_prob: float) -> bool:
    """Return True with probability arrival_prob."""
    # random() is in [0, 1): below p with probability p; p = 0 never, p = 1 always.
    happens = random.random() < arrival_prob
    return happens


def treatment_minutes(tier: int) -> int:
    """Return a random treatment length for tier, within TREATMENT_MINUTES[tier]."""
    shortest, longest = TREATMENT_MINUTES[tier]
    # randint includes both ends, which is what the table's "inclusive" says.
    minutes = random.randint(shortest, longest)
    return minutes


def simulate(num_doctors: int, arrival_prob: float, minutes: int,
             capacity: int = WAITING_ROOM_CAPACITY,
             seed: int | None = None) -> dict:
    """Run the ED for `minutes` minutes and return the statistics.

    Each minute: every free doctor calls in the most urgent waiting patient
    from a MinHeap363; then at most one new patient arrives and is added to
    the heap as (severity, arrival_minute), or turned away if the heap
    already holds `capacity` patients; then the statistics are updated.
    """
    # Seeding fixes the sequence of random numbers: the same seed gives the
    # same simulated week, and None gives a different week every run.
    random.seed(seed)
    # One counter dictionary per severity, built with a dictionary comprehension
    # (a loop over TIERS written inside the braces). Each tier gets its own
    # dictionary, so the counters do not mix.
    stats = {tier: {"arrived": 0, "seen": 0, "total_wait": 0,
                    "still_waiting": 0, "turned_away": 0}
             for tier in TIERS}
    # Whole-room numbers live under their own key, next to the tiers.
    stats["room"] = {"peak_waiting": 0, "first_full_minute": None,
                     "waiting_sum": 0, "busy_sum": 0}

    # The priority queue: the smallest (severity, arrival) tuple comes out first.
    # Tuples compare element by element, so the lowest severity number wins, and
    # among equals the earliest arrival does.
    waiting_room = MinHeap363()
    # free_at[d] is the first minute at which doctor d can take a new patient.
    free_at = [0] * num_doctors

    # One pass of the loop is one simulated minute.
    for minute in range(minutes):
        # 1. Doctors: every free doctor takes the most urgent patient, if any.
        for doctor in range(num_doctors):
            # Free means the current treatment is over; and someone must be waiting.
            if free_at[doctor] <= minute and waiting_room.size() > 0:
                # get() returns the most urgent tuple; unpack it into its two parts.
                severity, arrived = waiting_room.get()
                # Count the patient as seen, and add the minutes they waited
                # (now minus arrival) to their tier's total.
                stats[severity]["seen"] += 1
                stats[severity]["total_wait"] += minute - arrived
                # The doctor is busy until the treatment ends.
                free_at[doctor] = minute + treatment_minutes(severity)

        # 2. Arrival: at most one patient this minute.
        if arrival_happens(arrival_prob):
            # Draw the new patient's severity.
            severity = random_tier()
            # Arrivals count even if the patient is then turned away.
            stats[severity]["arrived"] += 1
            if waiting_room.size() >= capacity:
                # Waiting room full: this patient leaves and never enters the heap.
                stats[severity]["turned_away"] += 1
            else:
                # The key is a tuple (severity, arrival minute), as the docstring says.
                waiting_room.add((severity, minute))

        # 3. Statistics, after both the doctors and the arrival.
        # A short name for the room's entry, to keep the lines below readable.
        room = stats["room"]
        waiting = waiting_room.size()
        # Running sums: dividing by the number of minutes later gives averages.
        room["waiting_sum"] += waiting
        # A doctor is busy at this minute while free_at is still in the future.
        # The expression counts those doctors (1 for each one that is busy).
        room["busy_sum"] += sum(1 for f in free_at if f > minute)
        # Track the highest queue length ever seen.
        if waiting > room["peak_waiting"]:
            room["peak_waiting"] = waiting
        # Record the first minute the room reached capacity, only once (None
        # means "has not happened yet").
        if waiting == capacity and room["first_full_minute"] is None:
            room["first_full_minute"] = minute

    # Patients still in the waiting room when the clock ran out.
    # Draining the heap visits each leftover patient exactly once.
    while waiting_room.size() > 0:
        # _ is the conventional name for a value we do not need (the arrival minute).
        severity, _ = waiting_room.get()
        stats[severity]["still_waiting"] += 1

    # The single return: all the statistics, for print_report to display.
    return stats


# Given -- turning statistics into a report.
TIER_NAMES = {LIFE_THREATENING: "life-threatening",
              SEVERE: "severe",
              NON_LIFE_THREATENING: "non-life-threatening"}


def average_wait(stats: dict, tier: int) -> float | None:
    """Average wait, in minutes, of the patients of `tier` who were seen."""
    average = None
    if stats[tier]["seen"] > 0:
        average = stats[tier]["total_wait"] / stats[tier]["seen"]
    return average


def print_report(stats: dict) -> None:
    print(f"{'severity':22s} {'arrived':>8s} {'seen':>6s} {'waiting':>8s} {'turned away':>12s} {'avg wait (min)':>15s}")
    for tier in TIERS:
        s = stats[tier]
        avg = average_wait(stats, tier)
        shown = "--" if avg is None else f"{avg:.1f}"
        print(f"{TIER_NAMES[tier]:22s} {s['arrived']:8d} {s['seen']:6d} "
              f"{s['still_waiting']:8d} {s['turned_away']:12d} {shown:>15s}")
    room = stats["room"]
    print(f"waiting room: peak {room['peak_waiting']}, first full at minute {room['first_full_minute']}")


if __name__ == "__main__":
    print_report(simulate(NUM_DOCTORS, ARRIVAL_PROB, SIM_MINUTES, seed=SEED))
