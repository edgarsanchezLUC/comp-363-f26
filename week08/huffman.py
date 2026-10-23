"""
huffman.py -- COMP 363, Week 08

A Huffman encoder built from the code we wrote in class on Friday, October 16,
cleaned up. Node, and the whole encoding path of Huffman (frequencies, forest,
tree, codes, encode), are provided. Three pieces are left for you, each marked
TODO:

    Huffman.decode()           -- turn a bit string back into the message
    Huffman.tree_size_in_bits() -- what it costs to send the tree itself
    measure_compression()      -- the numbers the assignment asks you to report

Conventions used throughout: a left edge is "0" and a right edge is "1", so the
code for a symbol is the path from the root to its leaf. A message must have
at least two distinct symbols, and all of them must be ASCII.
"""

from __future__ import annotations


class Node:
    """A binary tree node for a basic Huffman encoder."""

    def __init__(self, frequency: int, symbol: str | None = None):
        """
        frequency : the symbol's frequency for a leaf node, or the sum of the
                    frequencies below it for an internal node.
        symbol    : the symbol of a leaf node; None for an internal node.
        """
        self.__frequency: int = frequency
        self.__symbol: str | None = symbol
        # A new node starts with no children. Merging two trees (see
        # Huffman.__build_huffman_tree) is what gives a node its children.
        self.__left: Node | None = None
        self.__right: Node | None = None

    def __lt__(self, other: Node) -> bool:
        """Orders nodes by frequency, so that two nodes can be compared with <.
        Python's < operator calls this method; it is the same job that
        Comparable.compareTo does in Java, except it only answers yes or no."""
        return self.__frequency < other.get_frequency()

    def set_left(self, left: Node | None) -> None:
        self.__left = left

    def set_right(self, right: Node | None) -> None:
        self.__right = right

    def get_left(self) -> Node | None:
        return self.__left

    def get_right(self) -> Node | None:
        return self.__right

    def get_symbol(self) -> str | None:
        return self.__symbol

    def get_frequency(self) -> int:
        return self.__frequency

    def is_leaf(self) -> bool:
        """A node is a leaf when it has no children. Every symbol lives in a
        leaf, and only symbols live in leaves; that is why no code can be a
        prefix of another."""
        return self.__left is None and self.__right is None

    def __str__(self) -> str:
        return f"[ {self.__symbol}: {self.__frequency} ]"


class Huffman:
    """Builds a Huffman tree for a message, then encodes and decodes with it."""

    # Direction labels, kept as class constants so that encoding and decoding
    # cannot disagree about them. They are strings because a code is built by
    # concatenating them into a path.
    _LEFT = "0"
    _RIGHT = "1"
    _NO_TREE_ERROR = "Huffman tree has not been built yet. Call encode() first."

    def __init__(self):
        # symbol -> how many times it appears in the message
        self.__frequency_table: dict[str, int] = {}
        # Trees waiting to be merged. It starts as one single-node tree per
        # symbol and shrinks by one with every merge.
        self.__forest: list[Node] = []
        # The finished tree. It is an attribute, not a return value, so decode()
        # and tree_size_in_bits() can use it long after encode() has finished.
        self.__huffman_root: Node | None = None
        self.__message: str = ""
        # symbol -> bit string, e.g. "l" -> "01"
        self.__varcode: dict[str, str] = {}

    # ---- provided -------------------------------------------------------

    def encode(self, message: str) -> str:
        """Builds the Huffman tree for message and returns the message encoded
        with it. Raises ValueError if the message has fewer than two distinct
        symbols or contains a non-ASCII character. The tree stays on the
        object, so decode() and tree_size_in_bits() can use it afterwards."""
        # Guard first: with a single distinct symbol the tree is one leaf, its
        # path is empty, and every code would be "". Non-ASCII symbols would
        # break the 8-bits-per-symbol accounting used in tree_size_in_bits().
        # set(message) keeps one copy of each character, so its length is the
        # number of distinct symbols. isascii() is True only if every character
        # is in the ASCII range. "raise" stops the method here with an error,
        # so nothing below runs on a bad message.
        if not message.isascii() or len(set(message)) < 2:
            raise ValueError("Message must be ASCII with at least 2 distinct symbols.")
        # Remember the message on the object, so that the helper methods below
        # can read it without having it passed to them one by one.
        self.__message = message
        # The five steps from the assignment, in order. Each step reads what
        # the one before it left in the object's attributes.
        self.__compute_frequencies()   # fills the frequency table
        self.__initialize_forest()     # turns the table into single-node trees
        self.__build_huffman_tree()    # merges the forest into one tree
        self.__derive_codes()          # walks the tree to find every code
        # The only return in this method: the bit string for the message.
        return self.__encode_message()

    def get_codes(self) -> dict[str, str]:
        """A copy of the symbol -> bit string table. It is a copy so that
        changing what you get back cannot corrupt the object's own table."""
        # dict(...) builds a new dictionary with the same entries.
        return dict(self.__varcode)

    def get_root(self) -> Node | None:
        """The root of the Huffman tree, or None if encode() has not run."""
        return self.__huffman_root

    def __compute_frequencies(self) -> None:
        # Step 1. A dictionary keeps the code short. An array indexed by
        # ord(symbol) would be much smaller in memory, as we saw in class.
        # Start empty so a second call to encode() does not add to old counts.
        self.__frequency_table = {}
        # Look at the message one character at a time, from first to last.
        for symbol in self.__message:
            if symbol in self.__frequency_table:
                # We have seen this symbol before: it has an entry, so count
                # one more occurrence of it.
                self.__frequency_table[symbol] += 1
            else:
                # First time we meet this symbol: create its entry, already
                # counting this occurrence.
                self.__frequency_table[symbol] = 1

    def __initialize_forest(self) -> None:
        # Step 2. One leaf per distinct symbol, holding the symbol and its count.
        # Start with an empty forest, for the same reason as above.
        self.__forest = []
        # .items() hands us each (symbol, count) pair of the dictionary, so we
        # can unpack both parts in the for statement.
        for symbol, frequency in self.__frequency_table.items():
            # A leaf: it has the symbol and the frequency, and no children.
            # Node's constructor takes the frequency first, then the symbol.
            # Putting the new leaf at the end of the list adds it to the forest.
            self.__forest.append(Node(frequency, symbol))

    def __remove_smallest_node(self) -> Node:
        """Removes from the forest, and returns, the node with least frequency."""
        # A linear scan, remembering the index of the smallest node so far.
        # list.pop(i) removes the item AT position i and returns it. (list.remove
        # takes a value, not a position, and returns nothing.) If two nodes tie,
        # the earlier one wins because < is strict; that is the tie-breaking rule.
        # Presume the first node is the smallest, until a smaller one shows up.
        smallest_index = 0
        # Check every other position. range(1, n) is 1, 2, ..., n-1.
        for i in range(1, len(self.__forest)):
            # Comparing two Nodes with < calls Node.__lt__, which compares
            # their frequencies.
            if self.__forest[i] < self.__forest[smallest_index]:
                # Found a smaller one: from now on, compare against this one.
                smallest_index = i
        # Take the winner out of the forest and hand it to the caller. This is
        # the single return of the method.
        return self.__forest.pop(smallest_index)

    def __build_huffman_tree(self) -> None:
        # Step 3, the greedy step. Every pass removes two trees and adds one,
        # so the forest shrinks by one and the loop ends with exactly one tree.
        while len(self.__forest) > 1:
            # Remove the two least frequent trees. The first call removes the
            # smallest; the second then finds the smallest of what is left,
            # which is the second smallest overall.
            first = self.__remove_smallest_node()
            second = self.__remove_smallest_node()
            # The parent has no symbol, only the combined frequency. The two
            # removed trees are not lost: they hang below the parent.
            # (Leaving out the symbol makes it None, which marks an internal node.)
            parent = Node(first.get_frequency() + second.get_frequency())
            # Attach the two trees as children. The smaller one goes left.
            parent.set_left(first)
            parent.set_right(second)
            # Put the new, bigger tree back in the forest. It may be merged
            # again on a later pass, exactly like a leaf.
            self.__forest.append(parent)
        # The lone survivor is the root of the whole Huffman tree. With one
        # tree left, it is at position 0 of the list.
        self.__huffman_root = self.__forest[0]

    def __derive_codes(self) -> None:
        """Depth-first traversal with a stack of (node, path so far) pairs.

        About the "# type: ignore" comments below: type checkers, such as the
        one built into many editors, read the type hints (like `Node | None`)
        and warn when something that might be None is used as if it were a
        Node. Here the warning is a false alarm. The tree was built by
        encode() before this method runs, so the root is not None, and an
        internal node always has both children. The checker cannot see that,
        so "# type: ignore" tells it to stay quiet on that one line. It has no
        effect when the program runs.
        """
        # Step 4. The stack holds work still to do. Each entry remembers where
        # a node is in the tree, as the string of turns taken from the root.
        # Start over with an empty table, in case encode() is called again.
        self.__varcode = {}
        # The root, with an empty path: no turns taken yet.
        stack: list[tuple[Node, str]] = [(self.__huffman_root, "")]  # type: ignore
        # Work until nothing is left on the stack.
        while stack:
            # pop() takes the most recently added entry, the last in, first out
            # behavior that makes this a depth-first walk. Unpack the pair into
            # the node and the path that leads to it.
            node, path = stack.pop()
            if node.is_leaf():
                # Arrived at a symbol: the path taken to get here is its code.
                self.__varcode[node.get_symbol()] = path  # type: ignore
            else:
                # An internal node always has two children. Push both, each
                # with the path extended by the turn that leads to it.
                # Gluing "0" or "1" to the end of the path string records
                # the turn, since the path is read from the root downward.
                stack.append((node.get_left(), path + self._LEFT))  # type: ignore
                stack.append((node.get_right(), path + self._RIGHT))  # type: ignore

    def __encode_message(self) -> str:
        # Step 5. Look up each symbol's code. Pieces are collected in a list
        # and joined once at the end: adding to a string one piece at a time
        # copies it again and again, which is painfully slow on a book.
        pieces: list[str] = []
        # Go through the message in order, so the codes come out in order.
        for symbol in self.__message:
            # The table gives this symbol's code, a string like "01".
            pieces.append(self.__varcode[symbol])
        # "".join glues all the pieces together with nothing in between,
        # producing the final bit string.
        return "".join(pieces)

    # ---- TODO -----------------------------------------------------------

    def decode(self, encoded_message: str) -> str:
        """Returns the message that encoded_message stands for, using the
        tree this object built in encode(). Raises ValueError (use
        self._NO_TREE_ERROR) if there is no tree yet.

        Walk the tree from the root, one bit at a time (self._LEFT for a
        left step, self._RIGHT for a right step). Each time you land on a
        leaf, record its symbol and go back to the root. Build the result in
        a list and join it, rather than adding to a string one character at
        a time.
        """
        # Hints:
        #  - Guard first: if there is no tree, raise ValueError. Do not
        #    return from inside the loop; set one result and return it once.
        if self.__huffman_root is None:
            raise ValueError(self._NO_TREE_ERROR)
        result: list[str] = []
        #  - Keep a "cursor" node, starting at the root.
        cursor = self.__huffman_root
        #    A 0 bit moves it to
        #    its left child, a 1 bit to its right child (compare each bit with
        #    self._LEFT instead of typing "0", so the constants stay the only
        #    place the convention lives).
        for bit in encoded_message:
            if bit == self._LEFT:
                cursor = cursor.get_left()
            elif bit == self._RIGHT:
                cursor = cursor.get_right()
            else:
                raise ValueError(f"Invalid bit in encoded message: {bit}")

        #  - After every step ask whether the cursor is a leaf. If it is, its
        #    symbol is the next character of the message; then reset the
        #    cursor to the root. If it is not, keep reading bits.
            if cursor.is_leaf():
                result.append(cursor.get_symbol)
                cursor = self.__huffman_root
        #  - Never look ahead: the code is prefix-free, so the first leaf you
        #    reach is the symbol.
        message = "".join(result)
        return message

    def tree_size_in_bits(self) -> int:
        """Returns the number of bits needed to transmit the tree, if it is
        sent as a pre-order walk in which

            an internal node costs 1 bit, and
            a leaf costs 1 bit plus 8 bits for its ASCII symbol.

        Raises ValueError (use self._NO_TREE_ERROR) if there is no tree yet.
        """
        # Hints:
        #  - This is the same depth-first traversal as __derive_codes, so a
        #    stack of nodes is enough this time; no paths are needed.
        #  - Visit every node once. Add 1 for each, and 8 more when the node
        #    is a leaf. For a tree with n leaves, how many nodes are there in
        #    total? Use that to check your answer.
        if self.__huffman_root is None:
            raise ValueError(self._NO_TREE_ERROR)

        # need similar structure to __derive_codes, but only Nodes, no str
        total_bits: int = 0
        stack: list[Node] = [self.__huffman_root]

        # while in the stack
        while stack:
            # pop current for the current node
            node = stack.pop()
            # increase total bits
            total_bits += 1
            # if node is a leaf, we add 8 more
            if node.is_leaf():
                total_bits += 8
            # if not, we take it as a parent node so we move on to it's next available node
            # by adding the left and right child to the stack
            else:
                stack.append(node.get_left())
                stack.append(node.get_right())
        # we keep going until there's no more
        # and we return the total number of bits
        return total_bits


def measure_compression(message: str) -> dict[str, int]:
    """Encodes message and returns a dictionary with these keys:

        "ascii_bits"   : bits to store message in plain ASCII (8 per character)
        "message_bits" : bits in the Huffman-encoded message
        "tree_bits"    : bits to transmit the tree (Huffman.tree_size_in_bits)
        "total_bits"   : message_bits + tree_bits
    """
    # Hints:
    #  - Build a Huffman object and encode the message with it; the length
    #    of the bit string it returns is message_bits.

    # initialize self
    huff = Huffman()

    # use what we already have to start message encode
    encoded = huff.encode(message)
    # ascii bits are the num of chars in the original message times Eight
    #  - ASCII costs 8 bits for every character of the message, repeats
    #    included.
    ascii_bits = len(message) * 8
    # message_bits are the # of chars in the encoded message
    message_bits = len(encoded)
    tree_bits = huff.tree_size_in_bits()
    total_bits = message_bits + tree_bits

    #  - Fill in a result dictionary and return it once, at the end.
    results = {
        "ascii_bits": ascii_bits,
        "message_bits": message_bits,
        "tree_bits": tree_bits,
        "total_bits": total_bits,
    }
    return results


if __name__ == "__main__":
    # Round-trip check on the example from class: whatever encode() produces,
    # decode() must turn back into the original message. Expected: True
    huffman = Huffman()
    encoded = huffman.encode("hello world")
    print(huffman.decode(encoded) == "hello world")
    print(measure_compression("hello world"))

    # Your own experiments go here: read a plain-text book from Project
    # Gutenberg, compress it, and call measure_compression.



