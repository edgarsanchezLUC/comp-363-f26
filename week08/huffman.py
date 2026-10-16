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
        self.__left: Node | None = None
        self.__right: Node | None = None

    def __lt__(self, other: Node) -> bool:
        """Orders nodes by frequency, so that two nodes can be compared with <."""
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
        """A node is a leaf when it has no children."""
        return self.__left is None and self.__right is None

    def __str__(self) -> str:
        return f"[ {self.__symbol}: {self.__frequency} ]"


class Huffman:
    """Builds a Huffman tree for a message, then encodes and decodes with it."""

    _LEFT = "0"
    _RIGHT = "1"
    _NO_TREE_ERROR = "Huffman tree has not been built yet. Call encode() first."

    def __init__(self):
        self.__frequency_table: dict[str, int] = {}
        self.__forest: list[Node] = []
        self.__huffman_root: Node | None = None
        self.__message: str = ""
        self.__varcode: dict[str, str] = {}

    # ---- provided -------------------------------------------------------

    def encode(self, message: str) -> str:
        """Builds the Huffman tree for message and returns the message encoded
        with it. Raises ValueError if the message has fewer than two distinct
        symbols or contains a non-ASCII character. The tree stays on the
        object, so decode() and tree_size_in_bits() can use it afterwards."""
        if not message.isascii() or len(set(message)) < 2:
            raise ValueError("Message must be ASCII with at least 2 distinct symbols.")
        self.__message = message
        self.__compute_frequencies()
        self.__initialize_forest()
        self.__build_huffman_tree()
        self.__derive_codes()
        return self.__encode_message()

    def get_codes(self) -> dict[str, str]:
        """A copy of the symbol -> bit string table."""
        return dict(self.__varcode)

    def get_root(self) -> Node | None:
        """The root of the Huffman tree, or None if encode() has not run."""
        return self.__huffman_root

    def __compute_frequencies(self) -> None:
        self.__frequency_table = {}
        for symbol in self.__message:
            if symbol in self.__frequency_table:
                self.__frequency_table[symbol] += 1
            else:
                self.__frequency_table[symbol] = 1

    def __initialize_forest(self) -> None:
        self.__forest = []
        for symbol, frequency in self.__frequency_table.items():
            self.__forest.append(Node(frequency, symbol))

    def __remove_smallest_node(self) -> Node:
        """Removes from the forest, and returns, the node with least frequency."""
        smallest_index = 0
        for i in range(1, len(self.__forest)):
            if self.__forest[i] < self.__forest[smallest_index]:
                smallest_index = i
        return self.__forest.pop(smallest_index)

    def __build_huffman_tree(self) -> None:
        while len(self.__forest) > 1:
            first = self.__remove_smallest_node()
            second = self.__remove_smallest_node()
            parent = Node(first.get_frequency() + second.get_frequency())
            parent.set_left(first)
            parent.set_right(second)
            self.__forest.append(parent)
        self.__huffman_root = self.__forest[0]

    def __derive_codes(self) -> None:
        """Depth-first traversal with a stack of (node, path so far) pairs."""
        self.__varcode = {}
        stack: list[tuple[Node, str]] = [(self.__huffman_root, "")]  # type: ignore
        while stack:
            node, path = stack.pop()
            if node.is_leaf():
                self.__varcode[node.get_symbol()] = path  # type: ignore
            else:
                stack.append((node.get_left(), path + self._LEFT))  # type: ignore
                stack.append((node.get_right(), path + self._RIGHT))  # type: ignore

    def __encode_message(self) -> str:
        pieces: list[str] = []
        for symbol in self.__message:
            pieces.append(self.__varcode[symbol])
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
        pass

    def tree_size_in_bits(self) -> int:
        """Returns the number of bits needed to transmit the tree, if it is
        sent as a pre-order walk in which

            an internal node costs 1 bit, and
            a leaf costs 1 bit plus 8 bits for its ASCII symbol.

        Raises ValueError (use self._NO_TREE_ERROR) if there is no tree yet.
        """
        pass


def measure_compression(message: str) -> dict[str, int]:
    """Encodes message and returns a dictionary with these keys:

        "ascii_bits"   : bits to store message in plain ASCII (8 per character)
        "message_bits" : bits in the Huffman-encoded message
        "tree_bits"    : bits to transmit the tree (Huffman.tree_size_in_bits)
        "total_bits"   : message_bits + tree_bits
    """
    pass


if __name__ == "__main__":
    # Round-trip check on the example from class. Expected: True
    huffman = Huffman()
    encoded = huffman.encode("hello world")
    print(huffman.decode(encoded) == "hello world")
    print(measure_compression("hello world"))

    # Your own experiments go here: read a plain-text book from Project
    # Gutenberg, keep only its ASCII characters, and call measure_compression.
