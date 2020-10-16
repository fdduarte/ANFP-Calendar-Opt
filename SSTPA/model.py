import sys
import os
from gurobipy import Model, GRB, quicksum
import time
sys.path.append(os.path.abspath(os.path.join('..', 'ANFP-Calendar-Opt', 'SSTPA')))

from modules.params.params import N, F, S, I, T, G, R, EL, EV, L, RP, E, PI, EB, V, H, TIMELIMIT, START_TIME, stats, S_full
from modules.model_stats import ModelStats

m = Model("SSTPA V3")

m.setParam('TimeLimit', TIMELIMIT)
m.setParam('MIPFocus', 1)
m.setParam('MIPGap', 0.3)


start_model = time.time()


#################
#*  VARIABLES  *#
#################

# p_itf: P[equipo, puntos, fecha]
# 1 si el equipo i tiene t puntos al
# finalizar la fecha f.
# 0 en otro caso.
#p = m.addVars(I, T, F, vtype=GRB.BINARY, name="p")

# z_ig: z[equipo][patron_resultados]
# 1 si al equipo i se le asigna el patron
# de resultados g.
# 0 en otro caso.
#z = {i: m.addVars(G[i], vtype=GRB.BINARY, name="z") for i in I}

# a_if: a[equipo, fecha]
# 1 si el partido del equipo i en la fecha f
# es atractivo por salir campeon.
# 0 en otro caso.
#a = m.addVars(I, F, vtype=GRB.BINARY, name="a")

# d_if: d[equipo, fecha]
# 1 si el partido del equipo i en la fecha f
# es atractivo por poder descender.
# 0 en otro caso.
#d = m.addVars(I, F, vtype=GRB.BINARY, name="d")

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

#p_jilf: P[equipo, equipo, fecha, fecha]
#discreta, cant de puntos del equipo j al finalizar la fecha f
#con la info de los resultados hasta la fecha l inclusive
#en el MEJOR conjunto de resultados futuros para el equipo i
p_m = m.addVars(I,I,F,F, vtype=GRB.INTEGER, name="p_m")

#p_jilf: P[equipo, equipo, fecha, fecha]
#discreta, cant de puntos del equipo j al finalizar la fecha f
#con la info de los resultados hasta la fecha l inclusive
#en el PEOR conjunto de resultados futuros para el equipo i
p_p = m.addVars(I,I,F,F, vtype=GRB.INTEGER, name="p_p")


# v_nilf : v[partido, equipo, fecha, fecha]
# binaria,  1 si el equipo local gana el partido n
# de la fecha f teniendo informacion finalizada la fecha l
# en el MEJOR conjunto de resultados futuros para el equipo i
v_m = m.addVars(N,I,F,F, vtype=GRB.BINARY, name="v_m")

# v_nilf : v[partido, equipo, fecha, fecha]
# binaria,  1 si el equipo local gana el partido n
# de la fecha f teniendo informacion finalizada la fecha l
# en el MEJOR conjunto de resultados futuros para el equipo i
v_p = m.addVars(N,I,F,F, vtype=GRB.BINARY, name="v_p")


# a_nilf: a[partido,equipo,fecha,fecha]
# 1 si el equipo visitante gana el partido n de la fecha f
# teniendo información finalizada la fecha l
# en el MEJOR conjunto de resultados para el equipo i
a_m = m.addVars(N,I,F,F, vtype=GRB.BINARY, name="a_m")


# a_nilf: a[partido,equipo,fecha,fecha]
# 1 si el equipo visitante gana el partido n de la fecha f
# teniendo información finalizada la fecha l
# en el PEOR conjunto de resultados para el equipo i
a_p = m.addVars(N,I,F,F, vtype=GRB.BINARY, name="a_p")


#e_nilf: e[partido,equipo,fecha,fecha]
#binaria, toma el valor 1 si se empata el 
#partido n de la fecha f, con la info
#de los resultados hasta la fecha l inclusive
# en el MEJOR conjunto de resultados futuros para el euqipo i
e_m = m.addVars(N,I,F,F, vtype=GRB.BINARY, name="e_m")

#e_nilf: e[partido,equipo,fecha,fecha]
#binaria, toma el valor 1 si se empata el 
#partido n de la fecha f, con la info
#de los resultados hasta la fecha l inclusive
# en el PEOR- conjunto de resultados futuros para el euqipo i
e_p = m.addVars(N,I,F,F, vtype=GRB.BINARY, name="e_p")


# alfa_ijl : alfa[equipo,equipo,fecha]
# binaria, toma el valor 1 si el equipo i tiene más
# puntos que el equipo j, en el MEJOR conjunto de 
# resultados futuros para el equipo i considerando que
# se está en la fecha l
alfa_m = m.addVars(I,I,F, vtype=GRB.BINARY, name="alfa_m")

# alfa_ijl : alfa[equipo,equipo,fecha]
# binaria, toma el valor 1 si el equipo i tiene más
# puntos que el equipo j, en el PEOR conjunto de 
# resultados futuros para el equipo i considerando que
# se está en la fecha l
alfa_p = m.addVars(I,I,F, vtype=GRB.BINARY, name="alfa_p")
M = m.addVar(vtype=GRB.INTEGER, name="M")

#beta_il: beta[equipo,fecha]
#discreta, indica la mejor posicion
#que puede alcanzar el equipo i al final del 
#torneo, mirando desde la fecha l en el MEJOR
#conjunto de resultados futuros para el equipo i
beta_m = m.addVars(I,F, vtype=GRB.INTEGER, name="beta_m")

#beta_il: beta[equipo, fecha]
#discreta, indica la mejor posicion
#que puede alcanzar el equipo i al final del 
#torneo, mirando desde la fecha l en el PEOR
#conjunto de resultados futuros para el equipo i
beta_p = m.addVars(I,F, vtype=GRB.INTEGER, name="beta_p")



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
#m.addConstrs((quicksum(p[i, t, f] for t in T) == 1 for i in I
#                                                   for f in F), name="R8")
m.addConstrs((x[n,f] == (v_m[n,i,l,f] + e_m[n,i,l,f] + a_m[n,i,l,f])
                                                                  for n in N
                                                                  for i in I
                                                                  for f in F
                                                                  for l in F
                                                                  if  f > l),name="R8")

# R9
#m.addConstrs((quicksum(z[i][g] for g in G[i]) == 1 for i in I), name="R9")
m.addConstrs((x[n,f] == (v_p[n,i,l,f] + e_p[n,i,l,f] + a_p[n,i,l,f])
                                                                  for n in N
                                                                  for i in I
                                                                  for f in F
                                                                  for l in F
                                                                  if  f > l),name="R9")


# R10
#m.addConstrs((quicksum(x[n, f] * R[i][n] for n in N if EL[i][n] + EV[i][n]  == 1) == quicksum(z[i][g] * RP[g][f] for g in G[i]) for i in I for f in F), name="R10")
m.addConstrs(((p_m[j,i,l,f] == PI[j] + quicksum(quicksum(R[i][n] * x[n][theta] for n in N if EL[i][n] + EV[i][n]  == 1) for theta in F if theta <= l) + quicksum(quicksum(3 * v_m[n,i,l,f] for l in F if l <= f) for n in N if EL[j][n] == 1) + quicksum(quicksum(3 * a_m[n,i,l,f] for l in F if l < f) for n in N if EV[j][n] == 1) + quicksum(quicksum(e_m[n,i,l,f] for l in F if l < f) for n in N if EL[j][n] + EV[j][n] == 1)) for n in N for j in I for i in I for f in F for l in F), name="R10")



# R11
#m.addConstrs( (p[i, t, f] == quicksum(z[i][g] for g in H[i][f][t]) for f in F
#                                                                   for t in T
#                                                                   for i in I), name="R11")
m.addConstrs((p_p[j,i,l,f] == PI[j] + quicksum(quicksum(R[i][n] * x[n][theta] for n in N if EL[i][n] + EV[i][n]  == 1) for theta in F if theta <= l) + quicksum(quicksum(3 * v_p[n,i,l,f] for l in F if l <= f) for n in N if EL[j][n] == 1) + quicksum(quicksum(3 * a_p[n,i,l,f] for l in F if l < f) for n in N if EV[j][n] == 1) + quicksum(quicksum(e_p[n,i,l,f] for l in F if l < f) for n in N if EL[j][n] + EV[j][n] == 1) for n in N for j in I for i in I for f in F for l in F), name="R11")


# R12
#m.addConstrs((a[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h <= t + 3 * (31 - f)) for i in I
#                                                                                                           for j in I
#                                                                                                           for t in T
#                                                                                                           for f in F
#                                                                                                           if f > F[0] and j != i), name="R12")
M=10000
m.addConstrs(((M * (1 - alfa_m[i, j, l] >= p_m[j, i, l, F] - p_m[i, i, l, F])) for i in I
                                                                          for j in I
                                                                          for l in F), name="R12")
# M es un número grande que hay que reemplazar


# R13
#m.addConstrs((a[i, F[0]] <= 1 - EB[i][t] + quicksum(EB[j][h] for h in T if h <= t + 3 * (31 - F[0])) for i in I
#                                                                                                     for j in I
#                                                                                                     for t in T
#                                                                                                     if j != i), name="R13")
m.addConstrs((((M * (alfa_p[i, j, l]) >= p_p[i, i, l, F] - p_p[j, i, l, F])) for i in I
                                                                           for j in I
                                                                           for l in F), name="R13")
# M es un número grande que hay que reemplazar

#R14
for i in I:
  m.addConstrs(((beta_m[i,l]==len(I)-(quicksum(alfa_m[i,j,l] for i,j in I if i!=j))) for l in F),name="R14")


# R15
#m.addConstrs((a[i, f] <= a[i, f - 1] for i in I
#                                     for f in F
#                                     if f > F[0]), name="R15")
for i in I:
  m.addConstrs(((beta_p[i,l]==len(I)-(quicksum(alfa_p[i,j,l] for i,j in I if i!=j))) for l in F),name="R15")


# R16
#m.addConstrs((d[i, f] <= 1 - p[i, t, f - 1] + quicksum(p[j, h, f - 1] for h in T if h >= t - 3 * (31 - f)) for i in I
#                                                                                                           for j in I
#                                                                                                           for t in T
#                                                                                                           for f in F
#                                                                                                           if f > F[0] and j != i), name="R16")

# R17
#m.addConstrs((d[i, F[0]] <= 1 - EB[i][t] + quicksum(EB[j][h] for h in T if h >= t - 3 * (31 - F[0])) for i in I
#                                                                                                     for j in I
#                                                                                                     for t in T
#                                                                                                     if j != i), name="R17")

# R18
#m.addConstrs((d[i, f] <= d[i, f - 1] for i in I
#                                     for f in F
#                                     if f > F[0]), name="R18")


print(f"** RESTRICTIONS TIME: {time.time() - start_model}")



########################
#*  FUNCION OBJETIVO  *#
########################

#m.setObjective(quicksum(quicksum(x[n, f] for n in N) for f in F), GRB.MAXIMIZE)

#m.setObjective(quicksum(quicksum(V[f] * (a[i, f] + d[i, f]) for i in I) for f in F), GRB.MAXIMIZE)

m.setObjective(quicksum(quicksum(beta_m[f,i] - beta_p[f,i] for i in I) for f in F), GRB.MAXIMIZE)

m.optimize()

print(f"** TOTAL TIME: {time.time() - START_TIME}")

ModelStats.parse_gurobi_output(m.getVars(), stats.matches, S_full)
ModelStats.check_valid_output()


