class Edge:
    
    def __init__(self, u, v, weight):
        self.u = u
        self.v = v
        self.weight = weight

    def __str__(self):
        return f"({self.u}, {self.v}, {self.weight})"