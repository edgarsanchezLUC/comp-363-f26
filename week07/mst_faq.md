# Week 7 — Minimum Spanning Trees: Frequently Asked Questions

Questions from students working on the Week 7 hand-trace, with answers. This is based on the [MST notebook](./mst.ipynb).

## 1. What is a safe edge, and how do I find one between components?

Pick any component, meaning a group of vertices already connected to each other in $T$.
A **safe edge** for that component is the cheapest edge with one
endpoint inside the component and the other endpoint outside it. It is
safe because it is the cheapest edge crossing the cut "this component
versus everything else".

To find it:

1. Use the component lookup table to list the vertices in the component.
2. For each of those vertices, scan its row of the matrix.
3. Skip any entry that is infinity (no edge).
4. Skip any entry whose other endpoint has the same component label. That
   edge stays inside the component and can't be the way out.
5. Take the smallest weight among what's left.

For example, consider a graph with 6 vertices and the following state of
the `comp` list:
```python
[1, 1, 1, 1, 2, 2]
```
There are two components in this graph. Vertices $0, 1, 2$ and $3$ are in
component 1, and vertices $4$ and $5$ are in component 2. Suppose the
edges are 0-1 (2), 1-2 (3), 2-3 (4), 4-5 (1), 3-4 (9), 1-5 (7), and
2-4 (6).

Any edge with one end in $\{0,1,2,3\}$ and the other end in $\{4,5\}$
crosses the cut between the two components. Here those are 3-4 (9),
1-5 (7), and 2-4 (6). Only the cheapest of them, 2-4 (6), is the safe
edge. The edges 0-1, 1-2, 2-3, and 4-5 have both ends in the same
component, so they are not candidates, even though 4-5 (1) is the
cheapest edge in the whole graph.

The comparison is across the whole component, not between two particular
vertices. In this example the only edge leaving vertex 3 is 3-4 (9), but
the cheapest edge leaving the component that contains vertex 3 is 2-4 (6).

## 2. How are the weights of edges determined?

The algorithm does not determine them. They are part of the input:
distances, costs, or whatever the problem is measuring. In the assignment
they are the numbers in the edge list, and they land in the matrix as
`graph[u][v]`. They never change while the algorithm runs. Only the
component labels change.  

## 3. Another example of choosing a component and finding its safe edge

This is a different graph from the assignment's, so you can practice on
it. Five vertices, 0 through 4, with edges 0-1 (7), 0-2 (3), 1-2 (9),
1-3 (4), 2-3 (11), 2-4 (6), 3-4 (8).

Start: {0} {1} {2} {3} {4}.

| Round | Component picked | Edges leaving it | Safe edge added | Components after |
|---|---|---|---|---|
| 1 | {3} | 3-1 (4), 3-4 (8), 3-2 (11) | 1-3 (4) | {0} {1,3} {2} {4} |
| 2 | {0} | 0-1 (7), 0-2 (3) | 0-2 (3) | {0,2} {1,3} {4} |
| 3 | {4} | 4-2 (6), 4-3 (8) | 2-4 (6) | {0,2,4} {1,3} |
| 4 | {1,3} | 1-0 (7), 1-2 (9), 3-4 (8), 3-2 (11) | 0-1 (7) | {0,1,2,3,4} |

In round 4, the edge 1-3 (4) is not a candidate. Both of its endpoints
are inside the component, so it can't be the way out. Of the four edges
that do leave, the cheapest is 0-1 (7).

The edges are 1-3, 0-2, 2-4, 0-1, with total weight
$4 + 3 + 6 + 7 = 20$.

Now redo it starting from a different component, say {2} first. You
should land on the same four edges. That is the cut property at work.
The weights 3, 4, 6, and 7 are all distinct, so this graph has exactly
one minimum spanning tree, and the order of your picks can't change it.

If any step of your trace of the class example feels shaky, bring it to
class. Showing me the step where you got stuck is the fastest way to sort
it out.
