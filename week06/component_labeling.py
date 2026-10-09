# built reached in graphs.ipynb
def reached(starting_vertex: int, g: list[list[int]]) -> list[int]:
    visited: list[int] = []  # vertices already explored
    gonext: list[int] = [starting_vertex]  # worklist, seeded with the start
    while len(gonext) > 0:
        u = gonext.pop()  # LIFO: explore the most recently found vertex next
        if u not in visited:
            visited.append(u)
            # row u of the adjacency matrix lists u's neighbors
            for v in range(len(g)):
                if g[u][v] != 0 and v not in visited:
                    gonext.append(v)  # found a new vertex to explore
    return visited

# built count components in graphs.ipynb
def count_components(g: list[list[int]]) -> int:
    """
    Count the number of connected components in an undirected graph.

    Parameters
    ----------
    g : list[list[int]]
        The adjacency matrix representing the undirected graph.

    Returns
    -------
    int
        The number of connected components in the graph.
    """

    components: int = 0
    marked: list[int] = []  # vertices already swept into some component
    # Try every vertex as a potential "new" starting point: a graph
    # doesn't have to be fully connected (vertex 5 in the class example
    # can't reach anything), so no single reached() call is guaranteed
    # to touch every vertex -- we have to give each one a chance to start
    # a component of its own.
    for starting_vertex in range(len(g)):
        if starting_vertex not in marked:
            # Not marked yet means nobody's reached() call has swept this
            # vertex in before, so we've found a vertex in a component we
            # haven't counted -- that's one more component.
            components += 1
            # Sweep in everything reachable from here -- the whole
            # component -- so none of its vertices re-trigger the count
            # above when the loop reaches them later.
            marked.extend(reached(starting_vertex, g))
    return components

# label components will follow count components' structure
# to be placed on top of reached
# same concept as count components except for recording the current label

def label_components(g: list[list[int]]) -> list[int]:
    component_id: int = 0
    labeled: list[int] = [-1] * len(g) # following the structure of count_components
    # try every vertex as a starting point and keep track of everything that's
    # been parsed through. Record the current label into the list to be returned
    # which would be labels[v] and then move on to the next vertex
    for starting_vertex in range(len(g)):
        if labeled[starting_vertex] == -1: # if not labeled just yet
            # then we need to get all reachable vertices in this component
            members = reached(starting_vertex, g)
            # now that we have reachable vertices, we need to assign an id
            for v in members:
                labeled[v] = component_id

            # once id is used, we can move on to the next id
            component_id += 1
    return labeled


g = [     # grabbed the graph from graphs.ipynb
    [0, 1, 1, 0, 0, 0], # neighbors of vertex 0
    [1, 0, 0, 0, 0, 0], # neighbors of vertex 1
    [1, 0, 0, 0, 0, 0], # neighbors of vertex 2
    [0, 0, 0, 0, 1, 0], # neighbors of vertex 3
    [0, 0, 0, 1, 0, 0], # neighbors of vertex 4
    [0, 0, 0, 0, 0, 0], # neighbors of vertex 5
]

print(label_components(g)) # shows the labels assigned for testing if it worked