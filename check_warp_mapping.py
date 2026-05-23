# Check mapping of control points to verify if they match
control_points = [
    ((128.7505, 35.8893), (47, 428)),  # West Gate
    ((128.7642, 35.8875), (991, 274)), # East Gate
    ((128.7542, 35.8858), (545, 673)), # Main Gate
    ((128.7582, 35.8928), (296, 8))     # North Loop
]

M = []
Y_x = []
Y_y = []
for (lon, lat), (x, y) in control_points:
    M.append((lon, lat, 1.0))
    Y_x.append(x)
    Y_y.append(y)

MTM = [[0.0]*3 for _ in range(3)]
for i in range(3):
    for j in range(3):
        MTM[i][j] = sum(M[k][i] * M[k][j] for k in range(len(control_points)))

MT_Yx = [sum(M[k][i] * Y_x[k] for k in range(len(control_points))) for i in range(3)]
MT_Yy = [sum(M[k][i] * Y_y[k] for k in range(len(control_points))) for i in range(3)]

def det3x3(mat):
    return (mat[0][0]*(mat[1][1]*mat[2][2] - mat[1][2]*mat[2][1]) -
            mat[0][1]*(mat[1][0]*mat[2][2] - mat[1][2]*mat[2][0]) +
            mat[0][2]*(mat[1][0]*mat[2][1] - mat[1][1]*mat[2][0]))

def solve3x3(mat, vec):
    d = det3x3(mat)
    m0 = [[vec[i] if j == 0 else mat[i][j] for j in range(3)] for i in range(3)]
    m1 = [[vec[i] if j == 1 else mat[i][j] for j in range(3)] for i in range(3)]
    m2 = [[vec[i] if j == 2 else mat[i][j] for j in range(3)] for i in range(3)]
    return det3x3(m0)/d, det3x3(m1)/d, det3x3(m2)/d

A, B, C = solve3x3(MTM, MT_Yx)
D, E, F = solve3x3(MTM, MT_Yy)

print(f"Coefficients:")
print(f"  A = {A:.5f}, B = {B:.5f}, C = {C:.5f}")
print(f"  D = {D:.5f}, E = {E:.5f}, F = {F:.5f}")

print("\nControl point mappings:")
for (lon, lat), (x, y) in control_points:
    x_est = A * lon + B * lat + C
    y_est = D * lon + E * lat + F
    print(f"  ({lon}, {lat}) -> Actual ({x}, {y}) vs Est ({x_est:.1f}, {y_est:.1f})")
