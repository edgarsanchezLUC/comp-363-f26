n = len(G)
T = [[0 for i in range(n)]for j in range(n)]
for i in range(n):
	for j in range(n):
		T[i][j] = float('inf')

T = [[float('inf') for i in range(n)] for j in range(n)]
T = [[float('inf') for _ in range(n)] for _ in range(n)]

Work Flow
Inpupt: adjacency matrix G
T = e
Work Flow
Inpupt: adjacency matrix G
T = edgeless copy of G # all work is done in here
while T has more than 1 components:
	select a component from T
	find a safe edge out of thae component # it leads to another component in T
	connect the two components via safe edge
	recount components
return all safe edges
edgeless copy of G
while T has more than 1 components:
	select a component from T
	find a safe edge out of that component
	connect the two components via safe edge
	recount components
return all safe edges

