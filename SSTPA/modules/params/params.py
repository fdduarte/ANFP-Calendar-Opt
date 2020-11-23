import sys, os
import pandas as pd
import time
import sys
from modules.params.pat_gen import home_away_patterns, check_homeaway_pattern, results_patterns_gen, check_results_pattern, result_patterns_gen_v4, check_short_result_pattern, patterns_sample
from modules.params.parser import ChampStats


##########################
#* GENERADOR PARAMETROS *#
#*      MODELO V3       *#
##########################


#############################
#* PARAMETROS DE INSTANCIA *#
#############################

START_TIME = time.time()
FECHAINI = 6
FECHAFIN = 10
if (len(sys.argv)) == 3:
  FECHAINI = int(sys.argv[1])
  FECHAFIN = int(sys.argv[2])
THRESHOLD = 100
FILTER = 0.25
TARGET = 10
BREAKS = 2
FILENAME = "SSTPA/modules/params/Datos.xlsx"
TIMELIMIT = (10000) * 60 * 60
print(f"PARAMS:\nFechas: {FECHAINI}-{FECHAFIN}\nTARGET: {TARGET}\nFILTER: {FILTER} (thrs {THRESHOLD})\nBREAKS: {BREAKS}")


# Carga de Datos
stats = ChampStats(FILENAME, FECHAINI, FECHAFIN)


#################
#*  CONJUNTOS  *#
#################

# I: Equipos
I = list(stats.teams.keys())

# N: Partidos
N = list(range((FECHAINI - 1) * 3 + 1, FECHAFIN * 3 + 1))

# Si: S[equipo]
# Patrones de localias asociados al equipo i
full_homeaway_patterns = list(home_away_patterns(BREAKS)).copy()
patterns = list(set([pat[FECHAINI - 6:FECHAFIN - 5] for pat in full_homeaway_patterns]))
patterns = {i + 1: patterns[i] for i in range(len(patterns))}

S_full = dict()
for i in I:
  pat = check_homeaway_pattern(i, stats.team_home_away, full_homeaway_patterns, stats.teams, FECHAINI, BREAKS)
  pat = list(set([p[FECHAINI - 6:FECHAFIN - 5] for p in pat]))
  S_full[i] = {f"{i}-{j + 1}": pat[j] for j in range(len(pat))}
S = {i: list(S_full[i].keys()) for i in I}


# F: Fechas
F = list(range(FECHAINI, FECHAFIN + 1))

# Gi: G[equipo]
# Patrones de resultados asociados al equipo i
full_results_patterns = results_patterns_gen(FILENAME, stats.teams_results, FECHAINI, FECHAFIN)
team_patterns = check_results_pattern(stats.teams_results, full_results_patterns)
G_full = dict()
for i in I:
  pat = list(set([pat for pat in team_patterns[i]]))
  patterns_sample(pat, THRESHOLD, FILTER)
  G_full[i] = {f"{i}-{j + 1}": pat[j] for j in range(len(pat))} # Contiene el valor asociado a la llave patron de Gi
G = {i: list(G_full[i].keys()) for i in I}

# T: Puntos
max_points = max([stats.team_points[i] for i in I]) + 3 * (FECHAFIN + 1 - FECHAINI)
min_points = min([stats.team_points[i] for i in I])
T = list(range(min_points, max_points + 1))


############################
#* PARAMETROS DEL MODELO *#
############################

# M
M = 10**4

# PIi: PI[equipo]
# cantidad de puntos del equipo i la fecha anterior a la primera
# de las fechas que quedan por jugar
PI = {i: stats.team_points[i] for i in I}

# EBit: EB[equipo][puntos]
# 1 si equipo i tiene t puntos la fecha anterior a la primera
# de las fechas que quedan por jugar
# 0 en otro caso
EB = {i: {t: 1 if stats.team_points[i] == t else 0 for t in T} for i in I}


# Rin: R[equipo][partido]:
# Puntos que gana el equipo i al jugar partido n
R = dict()
for i in I:
  R[i] = dict()
  for n in N:
    if i == stats.matches[n]['home']:
      if stats.matches[n]['winner'] == "H":
        R[i][n] = 3
      elif stats.matches[n]['winner'] == "D":
        R[i][n] = 1
      else:
        R[i][n] = 0
    elif i == stats.matches[n]['away']:
      if stats.matches[n]['winner'] == "A":
        R[i][n] = 3
      elif stats.matches[n]['winner'] == "D":
        R[i][n] = 1
      else:
        R[i][n] = 0
    else:
      R[i][n] = 0

# EL: EL[equipo][partido]
# 1 Si el equipo i es local en el partido n
# 0 En otro caso
EL = {i: {n: 1 if stats.matches[n]['home'] == i else 0 for n in N} for i in I}


# EVin: EV[equipo][partido]
# 1 Si el equipo i es visita en el partido n
# 0 En otro caso
EV = {i: {n: 1 if stats.matches[n]['away'] == i else 0 for n in N} for i in I}


# Lsf: L[patron][fecha]
# 1 Si el patron s indica que la fecha f
# es local
# 0 en otro caso
L = dict()
for i in I:
  for s in S[i]:
    L[s] = {f: 1 if S_full[i][s][f - FECHAINI] == "1" else 0 for f in F}

# RPgf: RP[patron][fecha]
# Cantidad de puntos asociados al resultado
# del patrón g en la fecha f
char_to_int = {"W": 3, "L": 0, "D": 1}
RP = dict()
for i in I:
  for gi in G[i]:
    RP[gi] = {f: char_to_int[G_full[i][gi][f - FECHAINI]] for f in F}

# GTift: G[equipo][fecha][puntos]
# Patrones tales que el equipo i tiene
# t puntos en la fecha f
H = dict()
puntos = lambda i, f, g: PI[i] + sum([RP[g][l] for l in range(F[0], f + 1)])
for i in I:
  H[i] = dict()
  for f in F:
    H[i][f] = dict()
    for t in T:
      H[i][f][t] = list()
    for g in G[i]:
      H[i][f][puntos(i, f, g)].append(g)

# Vf: V[fecha]
# Ponderación de atractivo de fecha f
V = {f: 0  if f - 15 <= TARGET else f - 15 for f in F}

print("FINISHED LOADING PARAMS")


      








