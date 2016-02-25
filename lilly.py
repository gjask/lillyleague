from flask import Flask, render_template
from league import League
import os


path = os.path.dirname(__file__)
data = os.path.join(path, 'league001.csv')
league = League(data)
app = Flask(__name__)


@app.template_filter('date')
def date_format(ts, fmt='%d.%m.%Y'):
    return ts.strftime(fmt)


@app.route('/')
def league_table():
    league.refresh()
    return render_template('table.html', league=league)


if __name__ == '__main__':
    app.run(debug=True)
