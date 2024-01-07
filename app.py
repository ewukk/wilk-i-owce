import random
from flask import Flask, render_template, request, session, redirect, json, jsonify
from Players.ComputerPlayer import ComputerPlayer
from game import create_player, create_game_instance, Game, is_position_within_board
import json

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
                    handle_computer_move()

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


@app.route('/handle_computer_move', methods=['POST'])
def handle_computer_move():
    try:
        # Pobierz pozycję wilka i owiec oraz rolę komputera
        wolf_position = game_instance.get_wolf().get_position()
        sheeps = game_instance.get_sheep()
        sheep_positions = [sheep.get_position() for sheep in sheeps]
        computer_role = session.get('computer_role')

        # Przekaż te informacje do funkcji obsługującej ruch komputera
        handle_computer_move_logic(wolf_position, sheep_positions, computer_role)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def handle_computer_move_logic(wolf_position, sheep_positions, computer_role):
    try:
        sheeps = game_instance.get_sheep()

        # Przekaż wszystkie potrzebne informacje
        computer_move = get_computer_move(wolf_position, sheep_positions)
        new_position = computer_move

        # Zaktualizuj current_position na nową pozycję
        if computer_role == "wilk":
            game_instance.get_wolf().set_position(new_position)
        else:
            chosen_sheep = sheeps[computer_move.get('sheepIndex')]
            chosen_sheep.set_position(new_position)

        session['current_turn'] = 'player'

        return jsonify(success=True, current_position=new_position)
    except Exception as e:
        return jsonify(success=False, error=str(e))


def handle_game_move():
    try:
        data = json.loads(request.get_data())
        move = data.get('pieceId')

        if move == 'USER_MOVE':
            handle_player_move(move)
        elif move == 'COMPUTER_MOVE':
            handle_computer_move()

        return jsonify(success=True, move=move)
    except Exception as e:
        return jsonify(success=False, error=str(e))


def handle_player_move(user_move):
    try:
        print("DEBUG: Handling player move")

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


def get_computer_move(wolf_position, sheep_positions):
    global move_mapping
    print("DEBUG: Pobierz Ruch Komputera - Start")

    computer_role = session.get('computer_role')

    # Sprawdź rolę komputera
    if computer_role == "wilk":
        move_mapping = {
            "DIAGONAL_UP_LEFT": "DIAGONAL_UP_LEFT",
            "DIAGONAL_UP_RIGHT": "DIAGONAL_UP_RIGHT",
            "DIAGONAL_DOWN_LEFT": "DIAGONAL_DOWN_LEFT",
            "DIAGONAL_DOWN_RIGHT": "DIAGONAL_DOWN_RIGHT",
        }
        current_position = game_instance.get_wolf().get_position()
        # Wybierz jeden ruch
        chosen_move = random.choice(list(move_mapping.values()))
        new_position = calculate_new_position(current_position, chosen_move, computer_role)

        print(f"DEBUG: Wybrany ruch komputera: {chosen_move}")
        print(f"DEBUG: Nowa pozycja pionka: {new_position}")
        print("DEBUG: Pobierz Ruch Komputera - Koniec")

        return new_position

    elif computer_role == "owca":
        move_mapping = {
            "DIAGONAL_UP_LEFT": "DIAGONAL_UP_LEFT",
            "DIAGONAL_UP_RIGHT": "DIAGONAL_UP_RIGHT",
        }
        # Wybierz losową owcę
        chosen_sheep = random.choice(game_instance.get_sheep())
        sheepIndex = chosen_sheep.get_index()
        current_position = chosen_sheep.get_position()
        print(f"DEBUG: Wybrana owca: {sheepIndex}")

        # Wybierz jeden ruch
        chosen_move = random.choice(list(move_mapping.values()))
        print(f"DEBUG: Wybrany ruch komputera: {chosen_move}")

        # Oblicz ruch na podstawie pozycji wybranej owcy
        new_position = calculate_new_position(current_position, chosen_move, computer_role)
        print(f"DEBUG: Nowa pozycja pionka: {new_position}")

        print("DEBUG: Pobierz Ruch Komputera - Koniec")

        return new_position


def calculate_new_position(current_position, move, role):
    # Metoda do obliczania nowej pozycji na podstawie aktualnej pozycji, ruchu i roli
    row, col = current_position
    print(f"DEBUG: Obliczanie nowej pozycji. Aktualna pozycja: {current_position}")

    if role == 'wilk':
        # Logika dla ruchu wilka
        if move == 'DIAGONAL_UP_LEFT':
            new_position = row - 1, col - 1
        elif move == 'DIAGONAL_UP_RIGHT':
            new_position = row - 1, col + 1
        elif move == 'DIAGONAL_DOWN_LEFT':
            new_position = row + 1, col - 1
        elif move == 'DIAGONAL_DOWN_RIGHT':
            new_position = row + 1, col + 1
        else:
            new_position = row, col
    elif role == 'owca':
        # Logika dla ruchu owcy
        if move == 'DIAGONAL_UP_LEFT':
            new_position = row - 1, col - 1
        elif move == 'DIAGONAL_UP_RIGHT':
            new_position = row - 1, col + 1
        else:
            new_position = row, col
    else:
        # Logika dla innej roli (możesz dostosować do własnych potrzeb)
        new_position = row, col

    # Sprawdź, czy nowa pozycja wykracza poza szachownicę
    if is_position_within_board(new_position):
        return new_position
    else:
        print(f"Nowa pozycja {new_position} wykracza poza szachownicę. Wybieranie nowej pozycji.")

        return calculate_new_position(current_position, "RANDOM_MOVE", role)



if __name__ == '__main__':
    app.run()
