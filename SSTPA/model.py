import sys
import os
from gurobipy import Model, GRB, quicksum
import time
sys.path.append(os.path.abspath(os.path.join('..', 'ANFP-Calendar-Opt', 'SSTPA')))

from modules.params.params import I, T, F, S, N, G1, G2, EL, EV, R, L, PV1, PV2, PE1, VG1, VG2, RP1, RP2, PE2, NE, NV, V, EB, FH, SH, H1, H2, START_TIME, FECHAINI, FECHAFIN, FIRST_HALF, SECOND_HALF, TIMELIMIT, stats
from modules.model_stats import ModelStats

m = Model("SSTPA V4")

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

# y_is: y[equipo][patron_localias]
# 1 si al equipo i se le asigna el patron
# de localias s
# 0 en otro caso
y = {i: m.addVars(S[i], vtype=GRB.BINARY, name="y") for i in I}

# z1_ig: z1[equipo, patron_resultados]
# 1 si al equipo i se le asigna el patron
# de resultados g perteneciente a G1.
# 0 en otro caso.
z1 = m.addVars(I, G1, vtype=GRB.BINARY, name="g1")

# z2_ig: z1[equipo, patron_resultados]
# 1 si al equipo i se le asigna el patron
# de resultados g perteneciente a G2.
# 0 en otro caso.
z2 = m.addVars(I, G2, vtype=GRB.BINARY, name="g1")

# p_itf: P[equipo, puntos, fecha]
# 1 si el equipo i tiene t puntos al
# finalizar la fecha f.
# 0 en otro caso.
p = m.addVars(I, T, F, vtype=GRB.BINARY, name="p")

# a_if: a[equipo, fecha]
# 1 si el partido del equipo i en la fecha f
# es atractivo por salir campeon.
# 0 en otro caso.
a = m.addVars(I, F, vtype=GRB.BINARY, name="a")

# d_if: d[equipo, fecha]
# 1 si el partido del equipo i en la fecha f
# es atractivo por poder descender.
# 0 en otro caso.
d = m.addVars(I, F, vtype=GRB.BINARY, name="d")

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
m.addConstrs((quicksum(z1[i, g] for g in G1) == 1 for i in I), name="R9")

# R10
m.addConstrs((quicksum(z2[i, g] for g in G2) == 1 for i in I), name="R10")

# R11
m.addConstrs((quicksum(PV1[g][FECHAINI + FIRST_HALF - 1] * z1[i, g] for g in G1) + quicksum(PV2[g][FECHAFIN] * z2[i, g] for g in G2) == NV[i] for i in I), name="R11")

# R12
m.addConstrs((quicksum(PE1[g][FECHAINI + FIRST_HALF - 1] * z1[i, g] for g in G1) + quicksum(PE2[g][FECHAFIN] * z2[i, g] for g in G2) == NE[i] for i in I), name="R12")

# R13
m.addConstrs((quicksum(x[n, f] * R[i][n] for n in N if EL[i][n] + EV[i][n] == 1) == quicksum(z1[i, g] * RP1[g][f] for g in G1 if VG1[i][g] == 1) for i in I
                                                                                                                                                 for f in FH), name="R13")

# R14
m.addConstrs((quicksum(x[n, f] * R[i][n] for n in N if EL[i][n] + EV[i][n] == 1) == quicksum(z2[i, g] * RP2[g][f] for g in G2 if VG2[i][g] == 1) for i in I
                                                                                                                                                 for f in SH), name="R14")

# R15
m.addConstrs((p[i, t, f] == quicksum(z1[i, g] for g in H1[i][f][t]) for i in I
                                                                   for f in FH
                                                                   for t in T), name="R15")

# R16
m.addConstrs((1 + p[i, t, f] >= p[i, h, SH[0]] + quicksum(z2[i, g] for g in H2[i][f][t - h]) for i in I
                                                                                         for f in SH
                                                                                         for t in T
                                                                                         for h in T
                                                                                         if t >= h), name="R16")

# R17
m.addConstrs((a[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h <= t + 3 * (31 - f)) for i in I
                                                                                                           for j in I
                                                                                                           for t in T
                                                                                                           for f in F
                                                                                                           if f > F[0] and j != i), name="R17")

# R18
m.addConstrs((a[i, F[0]] <= 1 - EB[i][t] + quicksum(EB[j][h] for h in T if h <= t + 3 * (31 - F[0])) for i in I
                                                                                                     for j in I
                                                                                                     for t in T
                                                                                                     if j != i), name="R18")

# R20
m.addConstrs((a[i, f] <= a[i, f - 1] for i in I
                                     for f in F
                                     if f > F[0]), name="R20")

# R21
m.addConstrs((d[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h >= t + 3 * (31 - f)) for i in I
                                                                                                           for j in I
                                                                                                           for t in T
                                                                                                           for f in F
                                                                                                           if f > F[0] and j != i), name="R21")

# R22
m.addConstrs((d[i, F[0]] <= 1 - EB[i][t] + quicksum(EB[j][h] for h in T if h >= t + 3 * (31 - F[0])) for i in I
                                                                                                     for j in I
                                                                                                     for t in T
                                                                                                     if j != i), name="R22")

# R24
m.addConstrs((d[i, f] <= d[i, f - 1] for i in I
                                     for f in F
                                     if f > F[0]), name="R24")

print(f"** RESTRICTIONS TIME: {time.time() - start_model}")



########################
#*  FUNCION OBJETIVO  *#
########################

#m.setObjective(quicksum(quicksum(x[n, f] for n in N) for f in F), GRB.MAXIMIZE)

m.setObjective(quicksum(quicksum(V[f] * (a[i, f] + d[i, f]) for i in I) for f in F), GRB.MAXIMIZE) ## CAMBIAR POR PARAMM

m.optimize()

print(f"\n** TOTAL TIME: {time.time() - START_TIME}")

ModelStats.parse_gurobi_output(m.getVars(), stats.matches)