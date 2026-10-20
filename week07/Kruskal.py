from MST_Base import MST_Base


class MST(MST_Base):
    """Minimum spanning tree of a weighted undirected graph, via Kruskal's algorithm.

    The graph is an adjacency matrix: graph[u][v] is the weight of edge u-v, or
    the "no edge" marker (inf in the example below) when u and v are not adjacent.

    Kruskal's algorithm, in one paragraph:
      1. Start with an empty forest: every vertex is its own component.
      2. Sort all edges of the graph by weight.
      3. Go through the edges from lightest to heaviest. If an edge joins two
         different components, add it to the forest (this merges the two
         components); otherwise skip it, since it would close a cycle.
    When the edges run out, the forest is the MST.
    """

    def __init__(self, input_graph):
        super().__init__(input_graph)
        self.edges = []  # List to store edges for Kruskal's algorithm

    def sort_edges(self):
        """Store all edges of the input graph in self.edges, sorted by weight.

        Each edge is a tuple (u, v, weight), listed once (u < v), in ascending
        order of weight.
        """
        self.edges = []
        for u in range(self.n):
            for v in range(u + 1, self.n):  # Avoid duplicates in undirected graph
                if self.graph[u][v] != self.no_edge:
                    self.edges.append((u, v, self.graph[u][v]))
        self.edges.sort(key=lambda x: x[2])  # Sort by weight

    def kruskal(self):
        """Compute the MST of self.graph and store it in self.mst.

        Examine the edges from lightest to heaviest; keep an edge only if its
        endpoints are in different components, then relabel the components.
        """
        self.init_mst()
        self.count_label()  # Initialize component labels
        self.sort_edges()  # Sort edges by weight
        for u, v, weight in self.edges:
            if self.comp[u] != self.comp[v]:  # If u and v are in different components
                self.mst[u][v] = weight
                self.mst[v][u] = weight
                # Update component labels after adding the edge
                self.count_label()

    def compute_mst(self):
        """Public entry point: build the MST (currently by Kruskal's algorithm)."""
        self.kruskal()


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
