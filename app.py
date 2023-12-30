from flask import Flask, render_template, request, session, redirect, json
from game import Game, create_player, create_game_instance

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = 600
game_instance = create_game_instance()


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/')
def hello():
    return render_template('hello.html')


@app.route('/choose_figure', methods=['GET', 'POST'])
def choose_figure():
    if request.method == 'POST':
        selected_role = request.form['figure']
        session['player_role'] = selected_role
        session['computer_role'] = "owca" if selected_role == "wilk" else "wilk"
        session.modified = True
        return redirect('/game?player_role=' + selected_role)
    return render_template('choose_figure.html', player_role=session.get('player_role'))


@app.route('/game', methods=['GET', 'POST'])
def game():
    result = ""

    # Sprawdź, czy rola gracza jest już ustawiona
    if 'player_role' not in session:
        player_role = request.args.get('player_role')
        if player_role:
            session['player_role'] = player_role
        else:
            return redirect('/choose_figure')

    # Przypisz rolę gracza z sesji
    game_instance.set_player_role(session['player_role'])

    if request.method == 'POST':
        user_move = request.form['move']
        if user_move:
            user_move = json.loads(user_move)

            # Sprawdź, czy użytkownik wykonał już ruch w tej turze
            if session.get('last_move') is not None:
                return redirect('/game')

            result = game_instance.play_turn(user_move)
            session['last_move'] = user_move

            if game_instance.is_game_over():
                pass

    # Sprawdź, czy użytkownik wykonał ruch, a następnie wykonaj ruch komputera
    if session.get('last_move') is not None:
            computer_move = game_instance.get_computer_move()
            result += game_instance.play_turn(computer_move)
            session.pop('last_move')  # Zresetuj ostatni ruch użytkownika

    sheeps = game_instance.get_sheep()
    wolf = game_instance.get_wolf()
    sheep_positions = [sheep.get_position() for sheep in sheeps]
    initialSheepPositions = [sheep.get_position() for sheep in sheeps]

    return render_template('game.html', sheeps=sheeps, wolf=wolf, result=result, sheep_positions=sheep_positions,
                           initialSheepPositions=initialSheepPositions, move_history=game_instance.move_history)


if __name__ == '__main__':
    app.run()
