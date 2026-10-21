from Edge import Edge


class MST:
    """Minimum spanning tree of a weighted undirected graph, via Boruvka's algorithm.

    The graph is an adjacency matrix: graph[u][v] is the weight of edge u-v, or
    the "no edge" marker (inf in the example below) when u and v are not adjacent.

    Boruvka's algorithm, in one paragraph:
      1. Start with an empty forest: every vertex is its own component.
      2. For each component, find its lightest edge leaving the component
         (its "safe edge").
      3. Add all safe edges to the forest. This merges components.
      4. Repeat 2-3 until a single component remains.
    Every round at least halves the number of components, so there are at most
    log2(n) rounds.
    """

    def __init__(self, input_graph):
        self.graph = input_graph  # the input: never modified
        self.mst = []  # adjacency matrix of the forest built so far
        self.n = len(input_graph)
        self.comp = []  # comp[v] = label (1..count) of v's component
        self.count = 0  # number of components in the current forest
        self.safe_edge = []  # safe_edge[c] = Edge(u, v, w), lightest edge leaving component c
        # The "no edge" marker is taken from the diagonal (a vertex has no edge
        # to itself), so the graph can use inf, 0, -1, etc.
        self.no_edge = input_graph[0][0]

    def reach(self, s):
        """Return the vertices reachable from s using only edges in the forest.

        Iterative depth-first search over the *mst* matrix, not the input graph.
        """
        visited = []
        stack = [s]
        while stack:
            u = stack.pop()
            if u not in visited:
                visited.append(u)
                for v in range(self.n):
                    if self.mst[u][v] != self.no_edge:
                        stack.append(v)
        return visited

    def count_label(self):
        """Label each vertex with its component number and count the components.

        Run a search from every vertex not yet labeled; everything it reaches
        belongs to the same component. Labels start at 1, so comp[v] == -1
        would mean "not yet labeled".
        """
        self.count = 0
        self.comp = [-1] * self.n
        marked = []
        for s in range(self.n):
            if s not in marked:
                self.count += 1
                from_s = self.reach(s)
                for v in from_s:
                    self.comp[v] = self.count
                    marked.append(v)

    def init_mst(self):
        """Start with a forest that has no edges."""
        self.mst = [[self.no_edge for _ in range(self.n)] for _ in range(self.n)]

    def reset_safe_edges(self):
        """Forget last round's safe edges.

        One slot per component label; index 0 is unused because labels start
        at 1. None means "no candidate edge seen yet".
        """
        self.safe_edge = [None] * (self.count + 1)

    def find_safe_edge(self, u, v):
        """Consider pair (u, v) as the safe edge of u's component.

        Only call this when u and v are in different components. The caller
        invokes it for (u, v) and (v, u) so that both components see the pair.
        """
        if self.safe_edge[self.comp[u]] is None:
            self.safe_edge[self.comp[u]] = Edge(u, v, self.graph[u][v])
        else:
            # Compare weights in the INPUT graph. self.mst only holds the edges
            # chosen so far, so for candidate edges it still says "no edge" and
            # every comparison would be inf vs. inf: the first pair seen would
            # win, nothing would merge, and boruvka() would loop forever.
            # A non-adjacent pair has weight inf, so any real edge replaces it.
            if self.safe_edge[self.comp[u]].weight > self.graph[u][v]:
                self.safe_edge[self.comp[u]] = Edge(u, v, self.graph[u][v])

    def copy_safe_edges(self):
        """Add every safe edge to the forest (in both directions: undirected).

        Two components may pick the same edge; writing it twice is harmless.
        """
        for edge in self.safe_edge:
            if edge is not None:
                self.mst[edge.u][edge.v] = edge.weight
                self.mst[edge.v][edge.u] = edge.weight

    def boruvka(self):
        """Compute the MST of self.graph and store it in self.mst.

        Each round of the while loop is one Boruvka round: find every
        component's safe edge, add those edges to the forest, then relabel
        the components. The loop ends when one component (the MST) remains.
        """
        self.init_mst()
        self.count_label()
        # NOTE: this assumes the input graph is connected. If it is not, some
        # components have no outgoing edge, nothing merges, and this loop
        # never ends. Of course there is no point in computing an MST of a 
        # disconnected graph, but it would be better to detect that and raise an 
        # exception than to loop forever. This can be done in a later 
        # implementation by checking if any component has no safe edge after a round.
        while self.count > 1:
            self.reset_safe_edges()
            # Examine every pair of vertices that lie in different components.
            for u in range(self.n):
                for v in range(self.n):
                    if self.comp[u] != self.comp[v]:
                        self.find_safe_edge(u, v)
                        self.find_safe_edge(v, u)
            self.copy_safe_edges()
            # Merging changed the components: relabel and recount.
            self.count_label()

    def compute_mst(self):
        """Public entry point: build the MST (currently by Boruvka's algorithm)."""
        self.boruvka()

    def get_mst(self):
        """Return the MST as an adjacency matrix (call compute_mst() first)."""
        return self.mst

    # Each entry maps a report label to a function of the MST object.
    # The sums look only at the lower triangle (j < i) so that each undirected
    # edge is counted once, not twice. This dictionary is a fancy-smancy way 
    # to avoid string literals in the __str__ method. (No "magic" values).   
    REPORT = {
        "Input graph size": lambda self: self.n,
        "MST size": lambda self: sum(
            1 for i in range(self.n) for j in range(i) if self.mst[i][j] != self.no_edge
        ),
        "MST weight": lambda self: sum(
            self.mst[i][j]
            for i in range(self.n)
            for j in range(i)
            if self.mst[i][j] != self.no_edge
        ),
    }

    def __str__(self):
        report_lines = [f"{key}: {value(self)}" for key, value in self.REPORT.items()]
        report_mst_rows = ["MST adjacency matrix:"]
        report_mst_rows += [
            " ".join(str(self.mst[i][j]) for j in range(self.n)) for i in range(self.n)
        ]
        return "\n".join(report_lines + report_mst_rows)


if __name__ == "__main__":
    # input graph: this is the example from the slides deck used in class.
    _ = float("inf")
    g = [
        [_, _, _, 5, 1, _],
        [_, _, 20, 5, _, 10],
        [_, 20, _, 10, _, _],
        [5, 5, 10, _, _, 15],
        [1, _, _, _, _, 20],
        [_, 10, _, 15, 20, _],
    ]

    mst = MST(g)
    mst.compute_mst()
    print(mst)
