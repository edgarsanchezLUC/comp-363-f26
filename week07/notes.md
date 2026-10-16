freq = {}
for char in message:

	if char not in wfreq:
		add char 1
	else:
		freq[char] += 1

Remember: Most greedy algorithms DO NOT WORK

Linear search is a greedy algorithm that works, but not efficiently

Using a tree like object, we can make it read binary without using spaces that separate the dots and dashes. no need for slashes, just a left right.
if we have 110101101, it'll keep going through the tree until it reaches a leaf node, those leafnodes are the ones containing each letter, so once you reach that leaf node, there's no where else to go, so that leafnode (letter) becomes the designated letter we wanted. No need for adding slashes in between dots and dashes.

cursor <- root
for digit in enc:
	if cursor is a leaf node:
		pull the symbol from cursor
		send the cursor back to root
	else:
		if digit == 1:
			cursor <- cursor.left
		else:
			cursor <- cursor.right

First step: Count the frequency
Second step: Build the Huffman tree
Third step: derive the variables
Fourth Step: Encode the message
Fifth Step: Decode the message at the destination

3rd step is the most challenging; you want to produce a table that holds the cursor and its symbol.
* how do we make it so they are labeled like below

H = 111
E = 110
O = 10
L = 01

How do we get from the root the letter _ and how do we guarantee that we reach that letter???
Traversing the tree is the most important thing: Depth First Search

Creating a stack is important. make it at the root of the tree
stack contains a tree node, and a string (the path to the node)
LEFT = 1
RIGHT = 0
stack =[(root,"")]
while len(stack) > 0:
	node.path = stack.pop()
	need some base case that detects a leaf node
	if node.has_left():
		node = node.left
		path = path + LEFT
		stack.push((node.path)	
	if node.has_right():
		node = node.right
		path = path + RIGHT
		stack.push(node.path)

