from MST_Base import MST_Base


class MST(MST_Base):
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
        super().__init__(input_graph)
        self.safe_edge = []  # safe_edge[c] = [u, v], lightest edge leaving component c

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
            self.safe_edge[self.comp[u]] = [u, v]
        else:
            a, b = self.safe_edge[self.comp[u]]
            # Compare weights in the INPUT graph. self.mst only holds the edges
            # chosen so far, so for candidate edges it still says "no edge" and
            # every comparison would be inf vs. inf: the first pair seen would
            # win, nothing would merge, and boruvka() would loop forever.
            # A non-adjacent pair has weight inf, so any real edge replaces it.
            if self.graph[a][b] > self.graph[u][v]:
                self.safe_edge[self.comp[u]] = [u, v]

    def copy_safe_edges(self):
        """Add every safe edge to the forest (in both directions: undirected).

        Two components may pick the same edge; writing it twice is harmless.
        """
        for edge in self.safe_edge:
            if edge is not None:
                u, v = edge
                self.mst[u][v] = self.graph[u][v]
                self.mst[v][u] = self.graph[v][u]

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
