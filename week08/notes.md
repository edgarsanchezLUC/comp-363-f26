# Notes

## Binary Tree Nodes based off depth

For a full binary tree, there are 2^L -1 nodes, where L is the amount of levels it has.

For a binary tree with only the first node in the last depth, we have 2^L-1 nodes

Therefor, there will always nodes between [2^L-1] and [2^L -1]

## Min Heap Property (Priority Queues)
The value of a parent is always less  than or equal to the values of both its children
The root of a CBT exhibiting the min heap property is always the smallest value of the tree.

In order to meet this criteria, you need to add a comparator to see if a new node would be a leaf or parent

When a new child is added to the tree, you compare whether the child is less than the parent, if true, you switch them and follow the child as it switches.