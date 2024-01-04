import random

from flask import Flask, render_template, request, session, redirect, json, jsonify
from Players.ComputerPlayer import ComputerPlayer
from game import create_player, create_game_instance, Game
import logging

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


# Funkcja do generowania początkowych pozycji pionków
def generate_initial_positions():
    # Początkowe pozycje wilka i owiec
    wolf_position = {"id": "wolf", "row": 0, "col": 0}
    sheep_positions = [{"id": f"sheep{i}", "row": 7, "col": 2 * i} for i in range(4)]

    # Zwróć listę początkowych pozycji pionków
    return [wolf_position] + sheep_positions


# Przykładowe dane
data = {
    "pieces": generate_initial_positions()
}


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
    session['current_turn'] = 'player'

    # Sprawdź role użytkowników
    player_role = session.get('player_role')
    computer_role = session.get('computer_role')
    print(f"DEBUG: Player Role: {player_role}")
    print(f"DEBUG: Computer Role: {computer_role}")

    is_game_over, game_result = game_instance.is_game_over()

    if not is_game_over:
        if request.method == 'POST':
            if game_instance.is_player_turn():
                # Logika dla tury gracza
                print("DEBUG: Tura gracza")
                user_move = request.json.get('move')
                print(f"DEBUG: Otrzymano ruch gracza: {user_move}")
                handle_game_move()

                # Po ruchu gracza sprawdź, czy gra się zakończyła
                is_game_over, game_result = game_instance.is_game_over()

                if not is_game_over:
                    # Jeśli gra się nie zakończyła, to przełącz na turę komputera
                    session['current_turn'] = 'computer'
                    if 'computer_role' not in session:
                        session['computer_role'] = "owca" if player_role == "wilk" else "wilk"
                    wolf_position = game_instance.get_wolf()
                    sheeps = game_instance.get_sheep()
                    sheep_positions = [sheep.get_position() for sheep in sheeps]

                    # Pobierz ruch komputera
                    computer_move = handle_computer_move(wolf_position, sheep_positions, session['computer_role'])
                    moveSheepWithComputerMove(computer_move)
                    moveWolfWithComputerMove(computer_move)

    sheeps = game_instance.get_sheep()
    wolf = game_instance.get_wolf()
    sheep_positions = [sheep.get_position() for sheep in sheeps]
    initialSheepPositions = [sheep.get_position() for sheep in sheeps]

    if request.method == 'GET':
        # Jeśli to żądanie GET, zwróć stronę HTML
        return render_template('game.html', sheeps=sheeps, wolf=wolf, result=result,
                               computer_result=computer_result, sheep_positions=sheep_positions,
                               initialSheepPositions=initialSheepPositions,
                               move_history=game_instance.move_history,
                               is_game_over=is_game_over, current_turn=session.get('current_turn'))
    elif request.method == 'POST' and request.is_json:
        # Jeśli to żądanie POST i zawiera dane w formie JSON, zwróć dane jako JSON
        return jsonify(data)
    else:
        # Jeśli to inne żądanie POST, zwróć odpowiednią odpowiedź (np. 400 Bad Request)
        return jsonify({"error": "Invalid request"}), 400


def handle_game_move():
    try:
        data = json.loads(request.get_data())
        move = data.get('pieceId')

        if move == 'USER_MOVE':
            handle_player_move(move)
        elif move == 'COMPUTER_MOVE':
            wolf_position = game_instance.get_wolf().get_position()
            sheep_positions = [sheep.get_position() for sheep in game_instance.get_sheep()]
            handle_computer_move(wolf_position, sheep_positions)

        return jsonify(success=True, move=move)
    except Exception as e:
        return jsonify(success=False, error=str(e))


def handle_player_move(user_move):
    try:
        print("DEBUG: Handling player move")
        wolf_position = game_instance.get_wolf().get_position()
        sheep_positions = [sheep.get_position() for sheep in game_instance.get_sheep()]

        game_instance.update_positions_based_on_player_move(user_move)
        is_game_over, _ = game_instance.is_game_over()

        if not is_game_over:
            game_instance.switch_player()
            print(f"DEBUG: Current turn after player move: {game_instance.current_player.get_role()}")

        else:
            print("Invalid move. Piece out of bounds.")
            return jsonify(success=False, error="Invalid move. Piece out of bounds.")

        return jsonify(success=True, move=user_move)

    except Exception as e:
        print(f"Error handling player move: {str(e)}")
        return jsonify(success=False, error=str(e))


def handle_computer_move(wolf_position, sheep_positions, computer_role):
    try:
        print("DEBUG: Handling computer move")

        computer_move = game_instance.get_computer_move()
        result = game_instance.play_turn(computer_move)

        is_game_over, _ = game_instance.is_game_over()
        if not is_game_over:
            game_instance.switch_player()
            print(f"DEBUG: Current turn after computer move: {game_instance.current_player.get_role()}")

        return jsonify(success=True, result=result)

    except Exception as e:
        print(f"Error handling computer move: {str(e)}")
        return jsonify(success=False, error=str(e))


# Funkcja sprawdzająca, czy pozycja pionka jest w zakresie planszy
def is_position_valid(position):
    return 0 <= position["row"] < 8 and 0 <= position["col"] < 8


def get_computer_move(self):
    global move_mapping
    print("DEBUG: Pobierz Ruch Komputera - Start")
    print(f"Komputer widzi grę jako {self.computer_player.get_role()}")
    computer_role = self.computer_player.get_role()
    wolf_position = self.wolf.get_position()
    sheep_positions = [sheep.get_position() for sheep in self.get_sheep()]

    # Sprawdź rolę komputera
    if computer_role == "wilk":
        possible_moves = self.calculate_new_position(wolf_position, sheep_positions)
        # Dostosuj format ruchu do oczekiwanego formatu w grze
        move_mapping = {
            "DIAGONAL_UP_LEFT": "DIAGONAL_UP_LEFT",
            "DIAGONAL_UP_RIGHT": "DIAGONAL_UP_RIGHT",
            "DIAGONAL_DOWN_LEFT": "DIAGONAL_DOWN_LEFT",
            "DIAGONAL_DOWN_RIGHT": "DIAGONAL_DOWN_RIGHT",
        }
    elif computer_role == "owca":
        # Wybierz losową owcę
        chosen_sheep = random.choice(self.get_sheep())
        # Oblicz ruch na podstawie pozycji wybranej owcy
        chosen_move = self.calculate_new_position(self.wolf.get_position(), chosen_sheep.get_position())
        possible_moves = [chosen_move]
        # Dostosuj format ruchu do oczekiwanego formatu w grze
        move_mapping = {
            "DIAGONAL_UP_LEFT": "DIAGONAL_UP_LEFT",
            "DIAGONAL_UP_RIGHT": "DIAGONAL_UP_RIGHT",
        }

    # Wybierz jeden ruch z move_mapping, nawet jeśli brak dostępnych ruchów
    chosen_move = random.choice(list(move_mapping.values()))

    print(f"DEBUG: Wybrany ruch komputera: {chosen_move}")
    print("DEBUG: Pobierz Ruch Komputera - Koniec")

    # Zwróć ruch komputera jako JSON
    return jsonify({"chosen_move": chosen_move})


if __name__ == '__main__':
    app.run()
