import itertools
import os
import random
import math


def homeaway_filter(breaks):
  def valid_homeaway_pattern(string):
    """
    :param string: string con patron de 1s y 0s
    :return: (bool) Indica si el patron es valido o no
    """
    local = string.count("0")
    visit = string.count("1")
    if local < 7 or visit < 7:
      return False
    if "111" in string or "000" in string:
      return False
    if string.count("00") > breaks or string.count("11") > breaks:
      return False
    return True
  return valid_homeaway_pattern

def check_homeaway_pattern(team, home_match, full_patterns, teams, start_date, breaks):
  """
  :param team: string alias equipo
  :home_match: Diccionario home_match[equipo][fecha]
  :full_patterns: Conjunto de patrones para 15 fechas
  :return: Conjunto de patrones que son posibles para
  el equipo
  """
  team_pat = ""
  for date in range(16, 31):
    team_pat += str(home_match[team][date])
  if start_date == 16:
    correct_pat = [team_pat] # Se agrega sol inicial como primer patrón
    for pattern in full_patterns:
      # Se revisa si el patrón calza con las localias y visitas faltantes.
      cond1 = pattern.count("1") == teams[team]['home_left']
      # Revisa ultimas fechas de primera rueda para evitar tres partidos L o V.
      if home_match[team][14] and home_match[team][15]:
        cond2 = pattern[0] == "0"
      elif not home_match[team][14] and not home_match[team][15]:
        cond2 = pattern[0] == "1"
      # Además, revisa si se lleva un break de la primera rueda.
      elif home_match[team][15] and pattern[0] == 1:
        cond2 = pattern.count("11") <= breaks - 1
      elif not home_match[team][15] and pattern[0] == 0:
        cond2 = pattern.count("00") <= breaks - 1
      else:
        cond2 = True
      # Si se cumplen las condiciones, el patrón es correcto.
      if cond1 and cond2:
        correct_pat.append(pattern)
    return correct_pat
  correct_pat1 = list()
  pattern_start = ""
  # Genera un string con las fechas ya jugadas. Luego, se revisa si
  # El comienzo del patron calza con el string generado.
  for date in range(16, start_date):
    pattern_start += str(home_match[team][date])
  for pattern in full_patterns:
    if pattern[:start_date - 16] == pattern_start:
      correct_pat1.append(pattern)
  correct_pat2 = list()
  # Se revisa si se llevo un break de rueda pasada.
  for pattern in correct_pat1:
    if home_match[team][15] == "1" and pattern[0] == "1":
      if pattern.count("11") <= breaks - 1:
        correct_pat2.append(pattern)
    elif not home_match[team][15] == "0" and pattern[0] == "0":
      if pattern.count("00") <= breaks - 1:
        correct_pat2.append(pattern)
    else:
      correct_pat2.append(pattern)
  # Por último, se revisa que calzen localías restantes
  correct_pat1 = list()
  for pattern in correct_pat2:
    if pattern.count("1") == teams[team]['home_left']:
      correct_pat1.append(pattern)
  correct_pat1.insert(0, team_pat) # Se inserta patron del equipo en el inicio
  return correct_pat1

def check_results_pattern(teams_stats, patterns):
  """
  :param teams_stats: (dict) diccionario con equipos y cantidad de partidos W,D,L
  :param patterns: (dict) conunto de patrones {int numero: str patron}
  :return: Diccionario {equipo: [patrones_utiles]}
  """
  team_patterns = dict()
  for team in teams_stats.keys():
    team_patterns[team] = list()
  for pattern in patterns:
    for team in teams_stats.keys():
      if pattern.count("D") == teams_stats[team]['draws'] and pattern.count("W") == teams_stats[team]['wins'] and pattern.count("L") == teams_stats[team]['loses']:
        team_patterns[team].append(pattern)
  return team_patterns

def results_patterns_gen(filename, teams_stats, start_date, end_date): # estandarizar una función q llame a las dos
  """
  :param dates: (int) cantidad de fechas a programar
  :param teams_stats: (dict) diccionario con equipos y cantidad de partidos W,D,L
  :return: (list) patrones de resultados.
  """
  dates = end_date - start_date + 1
  permutations = ["".join(seq) for seq in itertools.product("WDL", repeat=dates)]
  patterns = set()
  for team in teams_stats.keys():
    stats = ["W" for _ in range(teams_stats[team]['wins'])]
    stats.extend(["L" for _ in range(teams_stats[team]['loses'])])
    stats.extend(["D" for _ in range(teams_stats[team]['draws'])])
    stats = "".join(stats)
    patterns.add(stats)
  permutations_filtered = set()
  for perm in permutations:
    for pat in patterns:
      if pat.count("D") == perm.count("D") and pat.count("W") == perm.count("W") and pat.count("L") == perm.count("L"):
        permutations_filtered.add(perm)
  return list(permutations_filtered)

def result_patterns_gen_v4(length):
  return ["".join(seq) for seq in itertools.product("WDL", repeat=length)]


def home_away_patterns(breaks):
  return filter(homeaway_filter(breaks), ["".join(seq) for seq in itertools.product("01", repeat=15)])

def patterns_sample(patterns, threshold, relative_size, seed=1):
  """
  :param patterns: (list) Lista de patrones.
  :param threshold: (int) Valor mínimo al cual se le aplica el sampleo.
  :param relative_size: (float) porcentaje de sampleo.
  :param seed: (int)
  funcion que aplica sampleo a patrones para reduccion de dimencionaloidad.
  :return: (list) Patrones filtrados.
  """
  random.seed(seed)
  if (len(patterns)) > threshold:
    k = int(math.floor(len(patterns) * relative_size))
    random.sample(patterns, k)






