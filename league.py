import csv
import os
import collections

# model:
# players = {
#     0: {'name': 'Jan Skrle'},
# }
# games = {
#     (1,2): [('w', '+')]
# }


class Error(Exception):
    pass


class League(object):
    def __init__(self, datafile):
        self._players = None
        self._games = None
        self._score = None
        self.datafile = datafile
        self.from_csv()
        self._timestamp = 0

    def flush(self):
        self._players = {}
        self._games = collections.defaultdict(list)
        self._score = collections.Counter()

    def get_players(self):
        return self._players.copy()

    def get_games(self):
        return self._games.copy()

    def get_score(self):
        return self._score.copy()

    def refresh(self):
        if self._timestamp < self._get_timestamp():
            self.from_csv()

    @staticmethod
    def parse_match(text):
        text = text.upper()
        try:
            sign = text[-1]
            color = text[-2]
            opponent = int(text[:-2])
            assert sign in '+-='
            assert color in 'WB'
        except (IndexError, ValueError, AssertionError):
            raise Error('Bad game result format: {}'.format(text))
        return opponent, color, sign

    def _get_timestamp(self):
        return int(os.path.getmtime(self.datafile) + .5)

    def score(self):
        self._score = collections.Counter()
        for match, games in self._games.items():
            results = collections.Counter([g[1] for g in games])
            w, l, j = results['+'], results['-'], results['=']
            s = 2*l + 3*j + bool(w)*(3*w+1)
            self._score[match[0]] += s

    def from_csv(self):
        self._timestamp = self._get_timestamp()
        with open(self.datafile, 'r') as fp:
            reader = csv.reader(fp)
            self.flush()
            for row in reader:
                me = int(row[0])
                player = {'name': row[1]}
                self._players[me] = player
                for game in row[2:]:
                    opp, color, sign = self.parse_match(game)
                    self._games[(me, opp)].append((color, sign))
        self._validate()
        self.score()

    def _validate(self):
        color = {'W': 'B', 'B': 'W'}
        result = {'+': '-', '-': '+', '=': '='}
        for match, games in self._games.items():
            if len(games) > 2:
                raise Error('More than 2 games between {}'.format(match))
            for game in games:
                mirror = color[game[0]], result[game[1]]
                try:
                    assert mirror in self._games[match[::-1]]
                except (AssertionError, KeyError):
                    raise Error('Game record error found {}'.format(match))