inf = float('inf')

class_graph = [
    [inf, inf, inf, 5,   1,   inf], # Vertex 0 edges
    [inf, inf, 20,  5,   inf, 10 ], # Vertex 1 edges
    [inf, 20,  inf, 10,  inf, 20 ], # Vertex 2 edges
    [5,   5,   10,  inf, inf, 15 ], # Vertex 3 edges
    [1,   inf, inf, inf, inf, 20 ], # Vertex 4 edges
    [inf, 10,  inf, 15,  20,  inf]  # Vertex 5 edges
]


# implement the component labeling python assignment from last week.
def reached(starting_vertex: int, g: list[list[float]]) -> list[int]:
    visited: list[int] = []  # vertices already explored
    gonext: list[int] = [starting_vertex]  # worklist, seeded with the start
    while len(gonext) > 0:
        u = gonext.pop()  # LIFO: explore the most recently found vertex next
        if u not in visited:
            visited.append(u)
            # row u of the adjacency matrix lists u's neighbors
            for v in range(len(g)):
                if g[u][v] != g[0][0] and v not in visited:
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

def count_and_label(g: list[list[float]]) -> tuple[int, list[int]]:
    count = count_components(g)
    labels = label_components(g)
    return count, labels

def initialize_mst(g: list[list[float]]) -> list[list[float]]:
    n = len(g)
    t = [[g[0][0] for _ in range(n)] for _ in range (n)]
    return t


# we are working with floats because edges are infinite unless separately labeled
def boruvka_mst(graph: list[list[float]])-> list[list[float]]:
    # need to build a boruvka minimum spanning tree that takes a graph[u][v] and returns
    # the mst's edges.
    n = len(graph)
    # need to track the number of components and the components
    t = initialize_mst(graph)
    components_count, labels = count_and_label(t)

    # kiinda what we did in class w/ huffman, we want to combine the components until theres only one left
    while components_count > 1:
        # we need to find the cheapest path
        cheapest = {}
        for u in range(n):
            # for each labeled component
            u_component = labels[u]
            for v in range(n):
                # if the labeled component along with v is an edge
                if graph[u][v] != graph[0][0]:
                    # save v as its own component
                    v_component = labels[v]
                    # and compare the two components. IF they are not the same
                    if u_component != v_component:
                        # we can grab the weight between them
                        weight = graph[u][v]
                        # and check if the first component is not the cheapest
                        # or if the weight is cheaper than the current components weight
                        if u_component not in cheapest or weight < cheapest[u_component][0]:
                            # then we can save the info of the cheapest edge
                            cheapest[u_component] = (weight, u, v)

        # add the edge we found to be cheapest to the mst
        for weight, u, v in cheapest.values():
            t[u][v] = weight
            t[v][u] = weight

        components_count, labels = count_and_label(t)

    return t

result1 = boruvka_mst(class_graph)


n = len(result1)
edges = [(u, v, result1[u][v]) for u in range(n) for v in range(u + 1, n) if result1[u][v] != inf]
total_weight = sum(weight for _, _, weight in edges)

print(f"Minimum Spanning Tree: {len(edges)} edges found.")
for u, v, weight in edges:
    print(f"  Edge {u}-{v}: weight {weight}")

print(f"\nTotal Weight: {total_weight}")
print(f"Expected Total: 31 — {'MATCHES! 🎉' if total_weight == 31 else 'Does not match.'}")

