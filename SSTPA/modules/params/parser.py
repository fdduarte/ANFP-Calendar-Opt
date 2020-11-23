import pandas as pd


class ChampStats:

  @staticmethod
  def open_excel(name, page):
      """
      :param name: nombre del archivo a abrir
      :param page: nombre de la pagina de interes
      :return: lista por filas de pagina de excel
      """
      file = pd.ExcelFile(name)
      file = file.parse(page)
      column = []
      for key in file.keys():
          buff = []
          for i in range(len(file[key])):
              buff.append(str(file[key][i]).rstrip().replace("\xa0", " "))
          column.append(buff)
      buff = list(zip(*column))
      return buff

  @staticmethod
  def parse_line(line):
    _, home, away, score = line[1:5]
    score = [int(i.strip()) for i in score.split(":")]
    if score[0] > score[1]:
      winner = 'H'
    elif score[0] < score[1]:
      winner = "A"
    else:
      winner = "D"
    return home, away, winner

  def _load_team_stats_in_dates(self):
    """
    :return: {team -> {wins: i, draws: j, loses: k}}
    Función que, del archivo en el formato especificado retorna un
    diccionario con la cantidad de veces que el equipo gano, empato y
    perdio en las fechas indicadas.
    """
    stats = dict()
    for line in self.match_file:
      if line[0] != "nan":
          date = int(float(line[0]))
      else:
        home, away, winner = self.parse_line(line)
        if home not in stats.keys():
          stats[home] = {"wins": 0, "draws": 0, "loses": 0}
        if away not in stats.keys():
          stats[away] = {"wins": 0, "draws": 0, "loses": 0}
        if date in range(self.start_date, self.final_date + 1):
          if winner == "H":
            stats[home]["wins"] += 1
            stats[away]["loses"] += 1
          if winner == "A":
            stats[home]["loses"] += 1
            stats[away]["wins"] += 1
          if winner == "D":
            stats[home]["draws"] += 1
            stats[away]["draws"] += 1
    return stats

  def _load_matches(self):
    """
    :return: { match -> {date: , home: , away: , winner: } }
    Función que, del archivo en el formato especificado retorna un
    diccionario con las caracteristicas del partido.
    """
    matches = {i: [] for i in range(1, 31)}
    match = 30
    for line in self.match_file:
      if line[0] != "nan":
        date = int(float(line[0]))
      else:
        home, away, winner = self.parse_line(line)
        matches[match] = {"date": date, "home": home,
                          "away": away, "winner": winner}
        match -= 1
    return matches

  def _load_team_points(self):
    """
    :return: { team -> points }
    Función que, del archivo en el formato especificado retorna un
    diccionario con las caracteristicas del partido.
    """
    team_points = dict()
    for line in self.match_file:
      if line[0] != "nan":
        date = int(float(line[0]))
      else:
        home, away, winner = self.parse_line(line)
        if home not in team_points.keys():
          team_points[home] = 0
        if away not in team_points.keys():
          team_points[away] = 0
        if date < self.start_date:
          if winner == "H":
            team_points[home] += 3
          if winner == "A":
            team_points[away] += 3
          if winner == "D":
            team_points[home] += 1
            team_points[away] += 1
    return team_points

  def _load_home_away_stats(self):
    """
    :return: { team -> { date: 1 si es local, 0 en otro caso } }
    Función que, del archivo en el formato especificado retorna un
    diccionario con las localias y visitas del equipo.
    """
    team_home_away = dict()
    for line in self.match_file:
      if line[0] != "nan":
        date = int(float(line[0]))
      else:
        home, away, _ = self.parse_line(line)
        if home not in team_home_away.keys():
          team_home_away[home] = dict()
        team_home_away[home][date] = 1
        if away not in team_home_away.keys():
          team_home_away[away] = dict()
        team_home_away[away][date] = 0
    return team_home_away

  def _load_teams(self):
    teams = {}
    for line in self.teams_file:
      _, _, alias, fr_points, home_left = line
      teams[alias] = {"fr_points": int(fr_points), "home_left": int(home_left)}
    return teams


  def load(self):
    self.teams_results = self._load_team_stats_in_dates()
    self.matches = self._load_matches()
    self.team_points = self._load_team_points()
    self.team_home_away = self._load_home_away_stats()
    self.teams = self._load_teams()

  def __init__(self, filename, start_date, final_date):
    self.match_file = self.open_excel(filename, 1)
    self.teams_file = self.open_excel(filename, 0)
    self.start_date = start_date
    self.final_date = final_date
    self.load()
  
  