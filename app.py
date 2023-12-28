from flask import Flask, render_template, request, session, redirect

from Figures.Sheep import Sheep
from Figures.Wolf import Wolf
from game import Game
from Players.ComputerPlayer import ComputerPlayer
from Players.Player import Player

app = Flask(__name__)
app.secret_key = 'secret_key'
player = Player()
computer_player = ComputerPlayer()
game_instance = Game(player, computer_player, player_role=None)


@app.route('/')
def hello():
    return render_template('hello.html')


@app.route('/choose_figure', methods=['GET', 'POST'])
def choose_figure():
    global game_instance
    if request.method == 'POST':
        session['player_role'] = request.form['figure']
        session['computer_role'] = "owca" if session['player_role'] == "wilk" else "wilk"
        game_instance.set_player_role(session.get('player_role', 'owca'))  # Ustaw rolę w instancji Game
        return redirect('/game')
    return render_template('choose_figure.html', player_role=session.get('player_role'))


@app.route('/game', methods=['GET', 'POST'])
def game():
    global game_instance
    result = ""

    if request.method == 'POST':
        user_move = request.form['move']
        result = game_instance.play_turn(user_move)
        session['last_move'] = user_move

        if game_instance.is_game_over():
            pass

    computer_move = game_instance.get_computer_move()
    result += game_instance.play_turn(computer_move)

    sheeps = game_instance.get_sheep()
    wolf = game_instance.get_wolf()
    sheep_positions = [sheep.get_position() for sheep in sheeps]
    initialSheepPositions = [sheep.get_position() for sheep in sheeps]

    return render_template('game.html', sheeps=sheeps, wolf=wolf, result=result, sheep_positions=sheep_positions, initialSheepPositions=initialSheepPositions)


if __name__ == '__main__':
    app.run()
