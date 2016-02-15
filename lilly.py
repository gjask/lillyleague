from flask import Flask, render_template
from league import League
import os


path = os.path.dirname(__file__)
data = os.path.join(path, 'league001.csv')
league = League(data)
app = Flask(__name__)


@app.route('/')
def league_table():
    league.refresh()
    players = league.get_players()
    games = league.get_games()
    score = league.get_score()
    return render_template('table.html',
                           players=players, games=games, score=score)


if __name__ == '__main__':
    app.run()
