# Given -- a complete minimum heap. Copy it into heap363.py unchanged.
class MinHeap363:
    """A priority queue that always returns its smallest value, stored as a
    complete binary tree in a Python list.

    storage -- the tree, level by level, left to right; the root is storage[0]
    """

    def __init__(self):
        # The list starts empty: a new heap holds nothing.
        self.storage: list = []

    # ---- index arithmetic and swapping

    def _left_child(self, parent: int) -> int:
        """Return the position of the left child of the node at `parent`."""
        # Each level doubles, so the children of position p sit at 2p+1 and 2p+2.
        return 2 * parent + 1

    def _right_child(self, parent: int) -> int:
        """Return the position of the right child of the node at `parent`."""
        # The right child is always right next to the left child.
        return 2 * parent + 2

    def _parent(self, child: int) -> int:
        """Return the position of the parent of the node at `child`."""
        # The inverse of the two formulas above; // throws away the remainder,
        # so both children of a node land on the same parent.
        return (child - 1) // 2

    def _swap(self, i: int, j: int) -> None:
        """Exchange the values at positions i and j."""
        # Save one value first; otherwise the first assignment would
        # overwrite it and we would lose it.
        temp = self.storage[i]
        # Copy the value at j into position i.
        self.storage[i] = self.storage[j]
        # Put the saved value into position j.
        self.storage[j] = temp

    def _is_leaf(self, position: int) -> bool:
        """Return True if position has no children in storage. A position has
        a child exactly when its left child is inside the list."""
        # The left child is the first child to appear in the list, so if even
        # that one is past the end, the node has no children at all.
        leaf = self._left_child(position) >= len(self.storage)
        return leaf

    # ---- restoring the heap property

    def _bubble_up(self) -> None:
        """Move the last value in storage up until its parent is not greater
        than it, or it reaches the root."""
        # The value that was just added is the last one in the list.
        position = len(self.storage) - 1
        # Keep climbing while we are not at the root (position 0) and the
        # value is smaller than its parent: that pair breaks the heap property.
        while position > 0 and self.storage[position] < self.storage[self._parent(position)]:
            # Swap the value with its parent, moving it one level up.
            self._swap(position, self._parent(position))
            # Follow the value to its new position and check again.
            position = self._parent(position)

    def _sink_down(self) -> None:
        """Move the value at the root down until neither child is smaller
        than it, or it reaches a leaf."""
        # The value that was just moved to the top sits at position 0.
        position = 0
        # Assume the value still has work to do until we find it does not.
        sinking = True
        # A leaf has no children, so there is nowhere further down to go.
        while sinking and not self._is_leaf(position):
            # Assume the left child is the smaller one. It always exists here,
            # because this position is not a leaf.
            smaller = self._left_child(position)
            # The right child might not exist, so check that it is inside
            # the list before we look at it.
            right = self._right_child(position)
            if right < len(self.storage) and self.storage[right] < self.storage[smaller]:
                # The right child exists and is smaller, so it is the one to compare with.
                smaller = right
            if self.storage[position] > self.storage[smaller]:
                # The value is greater than its smaller child: swap them,
                # moving the value one level down.
                self._swap(position, smaller)
                # Follow the value to its new position and check again.
                position = smaller
            else:
                # Neither child is smaller: the heap property holds, so stop.
                sinking = False

    # ---- the priority queue interface

    def size(self) -> int:
        """Return the number of values in the heap."""
        # The list holds exactly the values in the heap, nothing else.
        count = len(self.storage)
        return count

    def peek(self):
        """Return the smallest value without removing it; None if empty."""
        # Pessimistic default: an empty heap has no smallest value.
        smallest = None
        if len(self.storage) > 0:
            # The heap property puts the smallest value at the root.
            smallest = self.storage[0]
        return smallest

    def add(self, value) -> None:
        """Place value in the heap, keeping the minimum heap property."""
        # Put the new value at the end: the next free spot at the bottom.
        self.storage.append(value)
        # It may be smaller than its parent, so let it float up if needed.
        self._bubble_up()

    def get(self):
        """Remove and return the smallest value; None if empty."""
        # Pessimistic default: an empty heap gives back None.
        smallest = None
        if len(self.storage) > 0:
            # The answer is the root.
            smallest = self.storage[0]
            # Remove the last value from the list so there are no gaps.
            last = self.storage.pop()
            # If that was the only value, the heap is now empty and there is
            # nothing to move; otherwise the last value takes the vacant root.
            if len(self.storage) > 0:
                self.storage[0] = last
                # It is probably too big for the top, so let it sink if needed.
                self._sink_down()
        return smallest

    # ---- printing

    def __len__(self) -> int:
        # Lets len(heap) work: it is the same as heap.size().
        return self.size()

    def __str__(self) -> str:
        # Shows the list, which is the whole tree level by level.
        return f"MinHeap363{self.storage}"


# Given -- simulation settings. PLACEHOLDER values.
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

ARRIVAL_PROB = 0.25  # chance of one arrival in any given minute (about 15 per hour)
NUM_DOCTORS = 12
SIM_MINUTES = 7 * 24 * 60  # one week
SEED = 363  # same seed -> same "random" week, so runs can be compared

# Most patients the waiting room can hold at once. PLACEHOLDER.
WAITING_ROOM_CAPACITY = 60

# Given -- experiment with the random module. Change the seed and re-run.
import random

random.seed(SEED)
print("five floats:     ", [round(random.random(), 3) for _ in range(5)])
print("five dice rolls: ", [random.randint(1, 6) for _ in range(5)])
print("one weighted pick:", random.choices(TIERS, weights=TIER_WEIGHTS))

picks = random.choices(TIERS, weights=TIER_WEIGHTS, k=10_000)
print("share of each tier in 10,000 picks:",
      {tier: picks.count(tier) / len(picks) for tier in TIERS})


# TODO -- write the three helpers and simulate().
def random_tier() -> int:
    """Return a random severity from TIERS, chosen according to TIER_WEIGHTS."""
    # TODO
    # make tier come from a random choice of TIERS based off of TIER_WEIGHTS. give only 1
    tier = random.choices(TIERS, weights=TIER_WEIGHTS, k=1)
    return tier


def arrival_happens(arrival_prob: float) -> bool:
    """Return True with probability arrival_prob."""
    happens = False
    # TODO
    # if random chance hits the arrival probability, then happens is true
    if random.random() < arrival_prob:
        happens = True

    return happens


def treatment_minutes(tier: int) -> int:
    """Return a random treatment length for tier, within TREATMENT_MINUTES[tier]."""
    minutes = 0
    # TODO
    minimum_time = TREATMENT_MINUTES[tier][0]
    maximum_time = TREATMENT_MINUTES[tier][1]
    minutes = random.randint(minimum_time, maximum_time)

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
    # TODO
    # need to use the waiting heap created
    waiting_heap = MinHeap363()
    # keep a count of doctors who are busy
    doctor_free_time = [0] * num_doctors

    # we increment per minute
    for minute in range(minutes):
        # every minute, a doctor sees a patient if available
        for i in range(num_doctors):
            if doctor_free_time[i] <= minute and len(waiting_heap) > 0:
                # set the severity and arrival minute of the next patient
                severity, arrival_minute = waiting_heap.get()
                # set the wait time to the current minute the patient was checked out minus the arrival minute
                wait_time = minute - arrival_minute
                # increase the counter for patients seen and total wait time
                stats[severity]["seen"] += 1
                stats[severity]["total_wait"] += wait_time

                # since we are seeing a patient, set the time it will take for them to be treated
                treatment_time = treatment_minutes(severity)
                doctor_free_time[i] = minute + treatment_time

    # if a patient arrives successfully
    if arrival_happens(arrival_prob):
        # make it of a random severity level
        tier = random_tier()
        # increase the counter
        stats[tier]["arrived"] += 1
        # but if we have no room, we turn them away
        if len(waiting_heap) >= capacity:
            stats[tier]["turned_away"] += 1
        # if we do, add it to the waiting heap
        else:
            waiting_heap.add((tier, minute))

    # once we have everything confirmed, update the stats
    current_waiting = len(waiting_heap)
    stats["room"]["waiting_sum"] += current_waiting

    # verify the peak amount of people waiting is less that currently waiting
    if current_waiting > stats["room"]["peak_waiting"]:
        # if it is, then update it to show current waiting is the peak
        stats["room"]["peak_waiting"] = current_waiting
        # if first full minute is still blank and we've gone over capacity,
        # then it's the first time we've gone over capacity; fill it in
        if stats["room"]["first_full_minute"] is None and current_waiting >= capacity:
            stats["room"]["first_full_minute"] = minute

    # mark off the amount of doctors that are currently busy
    busy_doctors = sum(1 for free_time in doctor_free_time if free_time > minute)
    # add it to the stats
    stats["room"]["busy_sum"] += busy_doctors

    # now we need to count the patients that are still waiting at the end of the simulation
    while len(waiting_heap) > 0:
        tier, arrival_minute = waiting_heap.get()
        stats[tier]["still_waiting"] += 1

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


print_report(simulate(NUM_DOCTORS, ARRIVAL_PROB, SIM_MINUTES, seed=SEED))
