import unicodecsv as csv
import os
import collections
import operator

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
        self.players = None
        self.games = None
        self.score = None
        self.order = None
        self.datafile = datafile
        self.from_csv()
        self._timestamp = 0

    def flush(self):
        self.players = {}
        self.games = collections.defaultdict(list)
        self.score = None
        self.order = None

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

    @staticmethod
    def _eval_match(games):
        results = collections.Counter([g[1] for g in games])
        return results['+'], results['-'], results['=']

    def _eval_score(self):
        self.score = collections.Counter()
        for match, games in self.games.items():
            w, l, j = self._eval_match(games)
            s = 2*l + 3*j + bool(w)*(3*w+1)
            self.score[match[0]] += s

    def _eval_order(self):
        score = self.score.items()
        s = sorted(score, key=operator.itemgetter(1), reverse=True)
        self.order = {}
        d = 0
        for i in range(len(s)):
            if i != 0 and s[i-1][1] == s[i][1]:
                d += 1
            self.order[s[i][0]] = i + 1 - d

    # def _direct_match_cmp(self, a, b):
    #     w, l, j = self._eval_match(self._games[(a, b)])
    #     return w > l
    #
    # def _number_of_wins(self, a, b):
    #     pass

    def from_csv(self):
        self._timestamp = self._get_timestamp()
        with open(self.datafile, 'r') as fp:
            reader = csv.reader(fp)
            self.flush()
            for row in reader:
                me = int(row[0])
                player = {'name': row[1]}
                self.players[me] = player
                for game in row[2:]:
                    opp, color, sign = self.parse_match(game)
                    self.games[(me, opp)].append((color, sign))

        self._validate()
        self._eval_score()
        self._eval_order()

    def _validate(self):
        color = {'W': 'B', 'B': 'W'}
        result = {'+': '-', '-': '+', '=': '='}
        for match, games in self.games.items():
            if len(games) > 2:
                raise Error('More than 2 games between {}'.format(match))
            for game in games:
                mirror = color[game[0]], result[game[1]]
                try:
                    assert mirror in self.games[match[::-1]]
                except (AssertionError, KeyError):
                    raise Error('Game record error found {}'.format(match))
