from flask import Flask, render_template, request, session, redirect

from Figures.Sheep import Sheep
from Figures.Wolf import Wolf
from game import Game
from Players.ComputerPlayer import ComputerPlayer
from Players.Player import Player

app = Flask(__name__)
app.secret_key = 'secret_key'


@app.route('/')
def hello():
    return render_template('hello.html')


@app.route('/choose_figure', methods=['GET', 'POST'])
def choose_figure():
    if request.method == 'POST':
        session['player_role'] = request.form['figure']
        session['computer_role'] = "owca" if session['player_role'] == "wilk" else "wilk"
        return redirect('/game')
    return render_template('choose_figure.html', player_role=session.get('player_role'))


@app.route('/game')
def game():
    sheeps = [Sheep(50 * i, 350) for i in range(8)]
    wolf = Wolf(350, 50)
    return render_template('game.html', sheeps=sheeps, wolf=wolf)


if __name__ == '__main__':
    player = Player()
    computer_player = ComputerPlayer()
    game_instance = Game(player, computer_player)
    app.run()
