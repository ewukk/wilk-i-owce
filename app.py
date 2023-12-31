from flask import Flask, render_template, request, session, redirect, json, jsonify

from Players.ComputerPlayer import ComputerPlayer
from Players.Player import Player
from game import create_player, create_game_instance, Game
import logging
import time

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = 600
app.config['JSON_AS_ASCII'] = False


def create_game_instance(session):
    player_role = session.get('player_role')
    player = create_player(player_role)
    computer_player = ComputerPlayer()
    game_instance = Game(player, computer_player, session)
    game_instance.set_player_role(player_role)
    return game_instance


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
        session['current_turn'] = 'player'
        session.modified = True
        print(f"DEBUG: Role selected: {selected_role}, Current turn: {session['current_turn']}")
        return redirect('/game?player_role=' + selected_role)
    return render_template('choose_figure.html', player_role=session.get('player_role'))


@app.route('/game', methods=['GET', 'POST'])
def game():
    global game_instance
    result = ""
    computer_result = ""

    # Sprawdź, czy rola gracza jest już ustawiona
    if 'player_role' not in session:
        player_role = request.args.get('player_role')
        if player_role:
            session['player_role'] = player_role
        else:
            return redirect('/choose_figure')

    # Utwórz nową instancję gry dla sesji gracza
    game_instance = create_game_instance(session=session)

    # Sprawdź role użytkowników
    player_role = session.get('player_role')
    computer_role = session.get('computer_role')
    print(f'Player Role: {player_role}, Computer Role: {computer_role}')

    if request.method == 'POST':
        print(f"DEBUG: POST Data: {request.form}")
        user_move = request.json.get('move')

        # Sprawdź, czy użytkownik wykonał już ruch w tej turze
        if session.get('last_move') is not None:
            print(f"DEBUG: Player move already recorded: {session['last_move']}")
            return redirect('/game')

        print(f"DEBUG: User move: {user_move}")
        result = game_instance.play_turn(user_move)

        if not game_instance.is_game_over():
            game_instance.switch_player()
            session['current_turn'] = 'computer' if game_instance.is_computer_turn() else 'player'
            time.sleep(0.5)  # Opóźnienie o 0.5 sekundy (przykładowa wartość)

    # Sprawdź, czy użytkownik wykonał ruch, a następnie wykonaj ruch komputera
    print("DEBUG: Before checking if game is over")
    is_game_over, computer_result = game_instance.is_game_over()
    if not game_instance.is_game_over():
        game_instance.switch_player()
        session['current_turn'] = 'computer' if game_instance.is_computer_turn() else 'player'
        wolf_position = game_instance.get_wolf().get_position()
        sheep_positions = [sheep.get_position() for sheep in game_instance.get_sheep()]
        computer_move = game_instance.get_computer_move(wolf_position, sheep_positions)
        print(f"DEBUG: Computer move: {computer_move}")
        computer_result = game_instance.play_turn(computer_move)
        result += computer_result
        session.modified = True  # Dodaj tę linię, aby zaznaczyć, że sesja została zmieniona
        session['current_turn'] = 'player'
        print(f"DEBUG: After Computer Move: {result}")

        # Sprawdź ponownie, czy gra jest teraz zakończona po ruchu komputera
        is_game_over, _ = game_instance.is_game_over()
        if is_game_over:
            game_instance.user_move_completed = False

    sheeps = game_instance.get_sheep()
    wolf = game_instance.get_wolf()
    sheep_positions = [sheep.get_position() for sheep in sheeps]
    initialSheepPositions = [sheep.get_position() for sheep in sheeps]

    print(f"DEBUG: Result={result}, Computer Result={computer_result}")

    return render_template('game.html', sheeps=sheeps, wolf=wolf, result=result,
                           computer_result=computer_result, sheep_positions=sheep_positions,
                           initialSheepPositions=initialSheepPositions, move_history=game_instance.move_history,
                           is_game_over=is_game_over, current_turn=session.get('current_turn'))


@app.route('/game', methods=['POST'])
def handle_game_move():
    try:
        data = request.get_json()
        user_move = data.get('move')

        if user_move == 'COMPUTER_MOVE':
            # Wywołaj funkcję do obsługi ruchu komputera
            return handle_computer_move()
        else:
            # Kontynuuj obsługę ruchu gracza
            handle_player_move(user_move)

        return jsonify(success=True)  # Odpowiedz w formie JSON
    except Exception as e:
        return jsonify(success=False, error=str(e))


def handle_player_move(user_move):
    try:
        print("DEBUG: Handling player move")
        game_instance.play_turn(user_move)  # Użyj user_move bez rozpakowywania
    except Exception as e:
        raise ValueError(f"Error handling player move: {str(e)}")


def handle_computer_move():
    try:
        computer_move = game_instance.get_computer_move()
        result = game_instance.play_turn(computer_move)
        return jsonify(success=True, result=result)
    except Exception as e:
        return jsonify(success=False, error=str(e))


if __name__ == '__main__':
    app.run()
