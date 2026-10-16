# Week 8 Assignment — Huffman Encoding

Due Friday, October 23.

## Reading

- [greedy algorithms, with Huffman codes](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
  (Erickson, Chapter 4). Huffman encoding is a greedy algorithm that happens
  to work. As we discussed, greedy algorithms rarely work by themselves; the
  strategy often needs fortification in the form of dynamic programming. For
  now, we are grateful that this one does.
- [Huffman's original 1951 paper](huffman.pdf) — the algorithm in its
  author's own words.
- [slides walking through Huffman's method](https://docs.google.com/presentation/d/1kSXEB7mzumoUm4pw7dhtxJxX7xckzjpUDyWlGfAxzAI/edit?usp=sharing)
  (ignore slide 47 and higher; still in progress).
- [a nephew's tribute to David Huffman](https://www.huffmancoding.com/my-uncle)
  (blog entry).
- [Morse code, a frequency-based code](https://en.wikipedia.org/wiki/Morse_code)
  and [amateur radio, where Morse lives on](https://en.wikipedia.org/wiki/Amateur_radio)
  (Wikipedia). Morse assigns short codes to frequent letters, as Huffman does,
  but it is *not* prefix-free; see below.

## Background

Huffman encoding compresses a message with a prefix-free, variable-length
code that gives shorter codes to more frequent symbols.

In ASCII every character costs 8 bits, so `HELLO WORLD` (11 characters) costs
88 bits:

```text
0100100001000101010011000100110001001111001000000101011101001111010100100100110001000100
```

Morse code gives frequent letters shorter codes: `E`, the most frequent
English letter, is a single dot, and `T`, the next, a single dash.
`HELLO WORLD` in Morse is 32 dots and dashes:

```text
......-...-..---.-----.-..-..-..
```

But we cannot tell the letters apart. Several of those dots and dashes could
equally be `EEEEEETEEETEETTTETTTTTETEETEETEE`. Real Morse resolves this with
a third symbol, a pause between letters and a longer pause between words:

```text
.... / . / .-.. / .-.. / --- // .-- / --- / .-. / .-.. / -..
```

The pauses are what make Morse decodable, because the code for `E` (`.`) is
a prefix of the code for `A` (`.-`). Huffman's codes need no pauses.

### The method

1. **Count frequencies.** For `HELLO WORLD` (the space is shown as `⎵`):

   | H | E | L | O | ⎵ | W | R | D |
   |---|---|---|---|---|---|---|---|
   | 1 | 1 | 3 | 2 | 1 | 1 | 1 | 1 |

2. **Make a forest.** One single-node tree, a *leaf*, per symbol, holding the
   symbol and its frequency.
3. **Merge.** Repeatedly remove the two trees with the least frequencies and
   put back a new tree whose root has no symbol, whose frequency is their sum,
   and whose children are the two you removed. Two out, one in: eventually one
   tree remains, the *Huffman tree*.
4. **Read off the codes.** The code for a symbol is the path from the root to
   its leaf, writing `0` for each step left and `1` for each step right.
5. **Encode** by replacing every symbol with its code. **Decode** by walking
   the tree from the root, one bit at a time, writing down the symbol each
   time you land on a leaf and starting over at the root.

<center>

![Huffman tree for HELLO WORLD](https://raw.githubusercontent.com/lgreco/images/refs/heads/main/huffman/huffman_tree.png)

_A Huffman tree for `HELLO WORLD`. Frequent symbols, like `L` (frequency 3),
sit closer to the root. A node that is not a leaf holds the sum of its
children's frequencies._

</center>

In this tree the path to `L` is left, then right: `01`. The full table is

| H    | E    | L  | O   | ⎵   | W   | R   | D   |
|------|------|----|-----|-----|-----|-----|-----|
| 0000 | 0001 | 01 | 001 | 100 | 101 | 110 | 111 |

and `HELLO WORLD` encodes to

```text
00000001010100110010100111001111
```

which is 32 bits against ASCII's 88.

**Why no code is a prefix of another.** Every symbol sits at a leaf. For the
code for `H`, `0000`, to be the beginning of another symbol's code, that other
symbol would have to lie below `H`, as a child or a descendant. But a leaf
has no children. The same argument holds for every symbol.

<center>

![Encoder schematic](https://raw.githubusercontent.com/lgreco/images/refs/heads/main/huffman/huffman_encoder.png)

---

![Decoder schematic](https://raw.githubusercontent.com/lgreco/images/refs/heads/main/huffman/huffman_decoder.png)

</center>

## The code you are given

[`huffman.py`](huffman.py) holds the encoder we started on Friday, cleaned
up. `Node` and every step of encoding, from frequency table to encoded bit
string, are written. You call `encode(message)` and get a bit string; the tree
stays inside the object. Read it before you write anything, and notice that
it uses the same pieces as the class, in the same order as the five steps
above.

A few things differ from the class's version: a left edge is `"0"` and a right
edge `"1"`, matching the picture and the table above; the helper methods are
private; and `encode` refuses a message with fewer than two distinct symbols
(a one-symbol message has no tree to walk, so its code would be empty) or with
any non-ASCII character.

Two merges can tie, with no rule for which of two equal-frequency trees goes
first. So your code table may differ from the one above: `L` might be `10`.
What cannot differ is the total length of the encoded message. For
`hello world` it is always 32 bits.

## What you write

Three `TODO`s in `huffman.py`:

1. **`Huffman.decode(encoded_message)`**. Walk the tree as described in step 5.
   Build the result in a list and `"".join` it. Raise `ValueError` if no tree
   has been built yet.
2. **`Huffman.tree_size_in_bits()`**. The receiver cannot decode without the
   tree, so the tree has to be sent, and sending it costs bits. Suppose it is
   sent as a pre-order walk: an internal node costs 1 bit; a leaf costs 1 bit
   plus 8 bits for its ASCII symbol. Return the total. (Check: the
   `hello world` tree has 8 leaves, so 15 nodes. How many bits is that?)
3. **`measure_compression(message)`**. Encode `message` and return a
   dictionary with `ascii_bits`, `message_bits`, `tree_bits` and `total_bits`
   (the last is the message plus the tree), as described in the docstring.

As always in this course, each function has exactly one `return`.

## Check your work

| Check | Expected |
|---|---|
| `huffman.decode(huffman.encode(m)) == m` for any valid `m` | `True` |
| `hello world`: `message_bits` | `32`, versus 88 in ASCII |
| `hello world`: `tree_bits` | the number you worked out above |
| `decode` before `encode` | `ValueError` |
| The code for the most frequent symbol | no longer than any other code |

## Measure it

Use `measure_compression` in the `__main__` block to answer the questions
below, in a comment block at the end of your file.

1. **`hello world`.** Report all four numbers. Did Huffman encoding pay for
   itself once the tree is counted? By how much, in bits?
2. **A real book.** Pick a plain-text book from
   [Project Gutenberg](https://www.gutenberg.org/); James Joyce's *Ulysses* is
   my favorite because it is massive. Read it with `open(..., encoding="utf-8")`
   and keep only its ASCII characters (`text.encode("ascii", "ignore").decode()`).
   Report the four numbers and what percentage of the ASCII size the *total*
   is. Now compare the tree's share of that total with the `hello world` case.
3. **In between.** Try a few sentences of your own, of different lengths.
   Roughly how long does an English message have to be before the Huffman
   total beats ASCII? What would have to be true of a message for the tree to
   cost almost nothing?
4. **Two ways to measure a tree.** The package
   [`pympler`](https://pympler.readthedocs.io/en/latest/) measures the memory
   an object occupies in Python: `from pympler import asizeof`, then
   `asizeof.asizeof(huffman.get_root())`. (If it is not installed, run
   `pip install pympler`, or `!pip install pympler` in a notebook cell.)
   Report that number, in bits, next to `tree_size_in_bits()` for the same
   tree and explain in a sentence or two why they differ so much and which one
   the receiver cares about.
5. **Ties.** When two trees tie for least frequent, does it matter which one
   you merge first? Does it change the code lengths, the encoded message's
   total length, or only which symbols get which codes? Run the experiment:
   encode a message, then the same message reversed, and compare.

## What to submit

A single **`.py`** file, your completed `huffman.py`, with your answers in a
comment block at the end, uploaded on Sakai by Friday, October 23. As always,
your best coding skills should shine through this assignment. Come ask
questions on Monday and Wednesday.
