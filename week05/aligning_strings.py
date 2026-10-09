""" diagonal moves -> (i-1,j-1)
    move up -> (i-1,j)
    move left -> (i,j-1)

    loop should stop when both i and j are 0

    when reaching the edge (when i or j is equal to 0):
    i -> move left (i, j-1)
    j -> move up (i-1, j)

    also know match, mismatch and gap cost
    match = 0
    mismatch = 2
    gap = 1

    edges equation -> P(i-1,j) = i * gap  | P(i,j-1) = j * gap
    """

# going off the equation for x and y...
def compute_penalty_matrix(X, Y, match_cost = 0, mismatch_cost = 2, gap_cost = 1):
    m, n = len(X), len(Y)
    # make the matrix full of 0's
    P = [[0] * (n + 1) for _ in range(m + 1)]

    # should be free to start the edges based off the equations we know.
    for i in range(1, m + 1):
        P[i][0] = i * gap_cost
    for j in range(1, n + 1):
        P[0][j] = j * gap_cost

    # rest of the table can be filled
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # if they match, then match cost, otherwise, mismatch cost
            cost = match_cost if X[i - 1] == Y[j - 1] else mismatch_cost
            P[i][j] = min(
                P[i - 1][j - 1] + cost, # matches or mismatches
                P[i - 1][j] + gap_cost, # gap in Y
                P[i][j - 1] + gap_cost # gap in X
            )

    return P

def trace_back_alignment(P, X, Y, match_cost = 0, mismatch_cost = 2, gap_cost = 1):
    """Walks backward through table P from (m, n) to (0, 0) to recover aligned strings."""
    i, j = len(X), len(Y)
    aligned_X = []
    aligned_Y = []

    while i > 0 or j > 0:
        # Edge cases: when one string is exhausted
        if i > 0 and j == 0:
            aligned_X.append(X[i - 1])
            aligned_Y.append("-")
            i -= 1
        elif j > 0 and i == 0:
            aligned_X.append("-")
            aligned_Y.append(Y[j - 1])
            j -= 1
        else:
            # Check which neighbor produced P[i][j]
            sub_cost = match_cost if X[i - 1] == Y[j - 1] else mismatch_cost

            # Option 1: Diagonal move (Match / Mismatch)
            if P[i][j] == P[i - 1][j - 1] + sub_cost:
                aligned_X.append(X[i - 1])
                aligned_Y.append(Y[j - 1])
                i -= 1
                j -= 1
            # Option 2: Up move (Gap in Y)
            elif P[i][j] == P[i - 1][j] + gap_cost:
                aligned_X.append(X[i - 1])
                aligned_Y.append("-")
                i -= 1
            # Option 3: Left move (Gap in X)
            elif P[i][j] == P[i][j - 1] + gap_cost:
                aligned_X.append("-")
                aligned_Y.append(Y[j - 1])
                j -= 1

    # Reverse strings because traceback goes from end to start
    X_bar = "".join(reversed(aligned_X))
    Y_bar = "".join(reversed(aligned_Y))

    return X_bar, Y_bar

def align_strings(X, Y):
    P = compute_penalty_matrix(X, Y)
    cost = P[len(X)][len(Y)]
    X_bar, Y_bar = trace_back_alignment(P,X,Y)
    return cost, X_bar, Y_bar

