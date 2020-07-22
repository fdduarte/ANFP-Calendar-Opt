import sys
import os
from gurobipy import Model, GRB, quicksum
import time
sys.path.append(os.path.abspath(os.path.join('..', 'ANFP-Calendar-Opt', 'SSTPA')))

from modules.params.params import N, F, S, I, T, G, R, EL, EV, L, RP, E, EB, V, H, TIMELIMIT, START_TIME, stats, S_full, Xi, Pi, Ai, Di
from modules.model_stats import ModelStats

m = Model("SSTPA V3")

m.setParam('TimeLimit', TIMELIMIT)
m.setParam('MIPFocus', 1)
m.setParam('MIPGap', 0.3)


start_model = time.time()


#################
#*  VARIABLES  *#
#################

# x_nf: x[partido, fecha]
# 1 si el partido n se programa finalmente
# en la fecha f
# 0 en otro caso.
x = m.addVars(N, F, vtype=GRB.BINARY, name="x")
for n in N:
  for f in F:
    x[n, f].start = Xi[n][f]

# y_is: y[equipo][patron_localias]
# 1 si al equipo i se le asigna el patron
# de localias s
# 0 en otro caso
y = {i: m.addVars(S[i], vtype=GRB.BINARY, name="y") for i in I}
for i in I:
  y[i][S[i][0]].start = 1 # Patrón 0 es el patron correspondiente al equipo
  for s in range(1, len(S[i])):
    y[i][S[i][s]].start = 0



# p_itf: P[equipo, puntos, fecha]
# 1 si el equipo i tiene t puntos al
# finalizar la fecha f.
# 0 en otro caso.
p = m.addVars(I, T, F, vtype=GRB.BINARY, name="p")
for i in I:
  for t in T:
    for f in F:
      p[i, t, f].start = Pi[i][t][f]

# z_ig: z[equipo][patron_resultados]
# 1 si al equipo i se le asigna el patron
# de resultados g.
# 0 en otro caso.
z = {i: m.addVars(G[i], vtype=GRB.BINARY, name="z") for i in I}
for i in I:
  z[i][G[i][0]].start = 1 # Patrón 0 es el patron correspondiente al equipo
  for g in range(1, len(G[i])):
    z[i][G[i][g]].start = 0

# a_if: a[equipo, fecha]
# 1 si el partido del equipo i en la fecha f
# es atractivo por salir campeon.
# 0 en otro caso.
a = m.addVars(I, F, vtype=GRB.BINARY, name="a")
for i in I:
  for f in F:
    a[i, f].start = Ai[i][f]

# d_if: d[equipo, fecha]
# 1 si el partido del equipo i en la fecha f
# es atractivo por poder descender.
# 0 en otro caso.
d = m.addVars(I, F, vtype=GRB.BINARY, name="d")
for i in I:
  for f in F:
    d[i, f].start = Di[i][f]

print(f"** VARIABLES TIME: {time.time() - start_model}")


#####################
#*  RESTRICCIONES  *#
#####################

# R2
m.addConstrs((quicksum(x[n, f] for f in F) == 1 for n in N), name="R2")

# R3
m.addConstrs((quicksum(x[n, f] for n in N if EL[i][n] + EV[i][n] == 1) == 1 for i in I
                                                                            for f in F), name="R3")

# R4
for i in I:
  m.addConstr((quicksum(y[i][s] for s in S[i]) == 1), name="R4")


# R6
for i in I:
  m.addConstrs((quicksum(x[n, f] for n in N if EL[i][n] == 1) == quicksum(y[i][s] for s in S[i] if L[s][f] == 1) for f in F), name="R6")

# R7
for i in I:
  m.addConstrs((quicksum(x[n, f] for n in N if EV[i][n] == 1) == quicksum(y[i][s] for s in S[i] if L[s][f] == 0) for f in F), name="R7")

# R8
m.addConstrs((quicksum(p[i, t, f] for t in T) == 1 for i in I
                                                   for f in F), name="R8")

# R9
m.addConstrs((quicksum(z[i][g] for g in G[i]) == 1 for i in I), name="R9")

# R10
m.addConstrs((quicksum(x[n, f] * R[i][n] for n in N if EL[i][n] + EV[i][n]  == 1) == quicksum(z[i][g] * RP[g][f] for g in G[i]) for i in I for f in F), name="R10")
                                                  
# R11
m.addConstrs( (p[i, t, f] == quicksum(z[i][g] for g in H[i][f][t]) for f in F
                                                                   for t in T
                                                                   for i in I), name="R11")

# R12
m.addConstrs((a[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h <= t + 3 * (31 - f)) for i in I
                                                                                                           for j in I
                                                                                                           for t in T
                                                                                                           for f in F
                                                                                                           if f > F[0] and j != i), name="R12")

# R13
m.addConstrs((a[i, F[0]] <= 1 - EB[i][t] + quicksum(EB[j][h] for h in T if h <= t + 3 * (31 - F[0])) for i in I
                                                                                                     for j in I
                                                                                                     for t in T
                                                                                                     if j != i), name="R13")

# R15
m.addConstrs((a[i, f] <= a[i, f - 1] for i in I
                                     for f in F
                                     if f > F[0]), name="R15")

# R16
m.addConstrs((d[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h >= t - 3 * (31 - f)) for i in I
                                                                                                           for j in I
                                                                                                           for t in T
                                                                                                           for f in F
                                                                                                           if f > F[0] and j != i), name="R16")

# R17
m.addConstrs((d[i, F[0]] <= 1 - EB[i][t] + quicksum(EB[j][h] for h in T if h >= t - 3 * (31 - F[0])) for i in I
                                                                                                     for j in I
                                                                                                     for t in T
                                                                                                     if j != i), name="R17")

# R18
m.addConstrs((d[i, f] <= d[i, f - 1] for i in I
                                     for f in F
                                     if f > F[0]), name="R18")


print(f"** RESTRICTIONS TIME: {time.time() - start_model}")



########################
#*  FUNCION OBJETIVO  *#
########################

#m.setObjective(quicksum(quicksum(x[n, f] for n in N) for f in F), GRB.MAXIMIZE)

m.setObjective(quicksum(quicksum(V[f] * (a[i, f] + d[i, f]) for i in I) for f in F), GRB.MAXIMIZE)

m.optimize()

print(f"** TOTAL TIME: {time.time() - START_TIME}")

ModelStats.parse_gurobi_output(m.getVars(), stats.matches, S_full)
ModelStats.check_valid_output()
