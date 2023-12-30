from flask import Flask, render_template, request, session, redirect, json, jsonify

from Players.ComputerPlayer import ComputerPlayer
from Players.Player import Player
from game import create_player, create_game_instance, Game

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = 600
app.config['JSON_AS_ASCII'] = False


def create_game_instance(session):
    player_role = session.get('player_role')
    player = create_player(player_role)
    computer_player = ComputerPlayer()
    return Game(player, computer_player, session)


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
        session['last_move'] = user_move

        if game_instance.is_game_over():
            pass

    # Sprawdź, czy użytkownik wykonał ruch, a następnie wykonaj ruch komputera
    print("DEBUG: Before checking if game is over")
    is_game_over, computer_result = game_instance.is_game_over()
    if not is_game_over:
        if session.get('last_move') is not None:
            computer_move = game_instance.get_computer_move()
            print(f"DEBUG: Computer move: {computer_move}")
            computer_result = game_instance.play_turn(computer_move)
            result += computer_result
            session.modified = True  # Dodaj tę linię, aby zaznaczyć, że sesja została zmieniona
            print(f"DEBUG: After Computer Move: {result}")

        # Sprawdź ponownie, czy gra jest teraz zakończona po ruchu komputera
        is_game_over, _ = game_instance.is_game_over()

    sheeps = game_instance.get_sheep()
    wolf = game_instance.get_wolf()
    sheep_positions = [sheep.get_position() for sheep in sheeps]
    initialSheepPositions = [sheep.get_position() for sheep in sheeps]

    print(f"DEBUG: Result={result}, Computer Result={computer_result}")

    return render_template('game.html', sheeps=sheeps, wolf=wolf, result=result,
                           computer_result=computer_result, sheep_positions=sheep_positions,
                           initialSheepPositions=initialSheepPositions, move_history=game_instance.move_history,
                           is_game_over=is_game_over)


@app.route('/game', methods=['POST'])
def handle_game_move():
    try:
        data = request.get_json()  # Użyj get_json zamiast json
        user_move = data.get('move')
        piece_id = user_move.get('pieceId')
        position = user_move.get('position')

        # Wywołaj metodę play_turn z klasy Game, przekazując dane o ruchu
        game_instance.play_turn(position)

        return jsonify(success=True)  # Odpowiedz w formie JSON
    except Exception as e:
        return jsonify(success=False, error=str(e))



if __name__ == '__main__':
    app.run()
