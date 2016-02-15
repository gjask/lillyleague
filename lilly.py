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
    return render_template('table.html',
                           players=league.players(),
                           games=league.games(),
                           score=league.score(),
                           order=league.order()
                           )


if __name__ == '__main__':
    app.run()
