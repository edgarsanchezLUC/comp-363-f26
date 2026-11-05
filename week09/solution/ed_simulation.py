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
    random.seed(seed)
    stats = {tier: {"arrived": 0, "seen": 0, "total_wait": 0,
                    "still_waiting": 0, "turned_away": 0}
             for tier in TIERS}
    stats["room"] = {"peak_waiting": 0, "first_full_minute": None,
                     "waiting_sum": 0, "busy_sum": 0}

    waiting_room = MinHeap363()
    # free_at[d] is the first minute at which doctor d can take a new patient.
    free_at = [0] * num_doctors

    for minute in range(minutes):
        # 1. Doctors: every free doctor takes the most urgent patient, if any.
        for doctor in range(num_doctors):
            if free_at[doctor] <= minute and waiting_room.size() > 0:
                severity, arrived = waiting_room.get()
                stats[severity]["seen"] += 1
                stats[severity]["total_wait"] += minute - arrived
                free_at[doctor] = minute + treatment_minutes(severity)

        # 2. Arrival: at most one patient this minute.
        if arrival_happens(arrival_prob):
            severity = random_tier()
            stats[severity]["arrived"] += 1
            if waiting_room.size() >= capacity:
                stats[severity]["turned_away"] += 1
            else:
                waiting_room.add((severity, minute))

        # 3. Statistics, after both the doctors and the arrival.
        room = stats["room"]
        waiting = waiting_room.size()
        room["waiting_sum"] += waiting
        room["busy_sum"] += sum(1 for f in free_at if f > minute)
        if waiting > room["peak_waiting"]:
            room["peak_waiting"] = waiting
        if waiting == capacity and room["first_full_minute"] is None:
            room["first_full_minute"] = minute

    # Patients still in the waiting room when the clock ran out.
    while waiting_room.size() > 0:
        severity, _ = waiting_room.get()
        stats[severity]["still_waiting"] += 1

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
