class MST_Base:
    """Common machinery for computing the minimum spanning tree of a weighted
    undirected graph. Subclasses supply the algorithm itself in compute_mst().

    The graph is an adjacency matrix: graph[u][v] is the weight of edge u-v, or
    the "no edge" marker (inf in the example in MST.py) when u and v are not
    adjacent.
    """

    def __init__(self, input_graph):
        self.graph = input_graph  # the input: never modified
        self.mst = []  # adjacency matrix of the forest built so far
        self.n = len(input_graph)
        self.comp = []  # comp[v] = label (1..count) of v's component
        self.count = 0  # number of components in the current forest
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

    def compute_mst(self):
        """Build the MST and store it in self.mst. Implemented by subclasses."""
        raise NotImplementedError

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
