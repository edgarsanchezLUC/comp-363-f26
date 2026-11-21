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