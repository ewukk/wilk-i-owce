from flask import session, jsonify
from Players.Player import Player, SheepPlayer, WolfPlayer
from Players.ComputerPlayer import ComputerPlayer
from Figures.Sheep import Sheep
from Figures.Wolf import Wolf
import random


def create_game_instance(session):
    player = Player()
    computer_player = ComputerPlayer()
    return Game(player, computer_player, session)


def create_player(role):
    if role is None or role == 'owca':
        return SheepPlayer()
    elif role == 'wilk':
        return WolfPlayer()
    else:
        raise ValueError(f"Nieznana rola: {role}")


def is_position_within_board(position, BOARD_SIZE=8, TILE_SIZE=50):
    max_coordinate = BOARD_SIZE * TILE_SIZE
    return 0 <= position[0] < max_coordinate and 0 <= position[1] < max_coordinate


class Game:
    def __init__(self, player, computer_player, session):
        # self.app = app  # Ta linia może być problemem, ale zostaw ją na razie
        self.player = player
        self.computer_player = computer_player
        self.session = session
        self.players = [self.player, self.computer_player]
        self.current_player = self.player
        self.last_move = None
        self.player_role = None
        self.user_move_completed = False
        self.move_history = {"owca": [], "wilk": []}
        self.wolf = Wolf(350, 50)
        self.sheep = [Sheep(50 * i, 350) for i in range(1, 8, 2)]

    def get_wolf(self):
        return self.wolf

    def get_sheep(self):
        return self.sheep

    def set_player_role(self, role):
        if role == 'owca':
            self.player.set_player_role(role)
            self.computer_player.set_player_role('wilk')
        elif role == 'wilk':
            self.player.set_player_role(role)
            self.computer_player.set_player_role('owca')
        else:
            raise ValueError(f"Nieznana rola: {role}")

    def switch_player(self):
        self.current_player = (
            self.player if self.current_player == self.computer_player else self.computer_player
        )

    def is_player_turn(self):
        print(f"DEBUG: Checking if it's player's turn. Current player: {self.current_player.get_role()}")
        return self.current_player == self.player

    def play_turn(self, user_move=None):
        result = ""
        print("DEBUG: Play Turn - Start")

        if user_move:
            session['current_turn'] = 'player'

            # Gracz wykonał ruch
            if self.last_move is not None or self.user_move_completed:
                return "Możesz wykonać tylko jeden ruch w swojej turze."

            if self.current_player is not None:
                self.move_history[self.player_role].append({"player": self.player_role, "move": user_move})

            self.last_move = user_move
            self.update_positions_based_on_player_move(user_move)
            self.user_move_completed = True

            if self.is_game_over():
                result += self.is_game_over()[1]  # Dodaj informację o zakończeniu gry
                return result

            # Sprawdź, czy użytkownik wykonał ruch
            if not self.user_move_completed:
                # Gracz nie wykonał jeszcze ruchu, zakończ tę turę
                return result
            elif not self.is_player_turn():
                # Jest tura komputera
                session['current_turn'] = 'computer'

                # Aktualizuj rolę komputera tylko wtedy, gdy jest to tura komputera
                if self.current_player == self.computer_player:
                    session['player_role'] = session['computer_role']

                computer_move = self.get_computer_move()
                self.update_positions_based_on_computer_move(computer_move)
                print(f"DEBUG: Computer move: {computer_move}")

                self.move_history[self.current_player.get_role()].append(
                    {"player": self.current_player.get_role(), "move": computer_move}
                )
                self.last_move = computer_move
                self.user_move_completed = False
                self.is_game_over()

        return result

    def update_positions_based_on_player_move(self, user_move):
        # Pobierz aktualne pozycje owiec i wilka
        wolf_position = self.get_wolf().get_position()
        sheep_positions = [sheep.get_position() for sheep in self.get_sheep()]

        # Zaktualizuj pozycje w zależności od ruchu gracza
        new_wolf_position = self.calculate_new_position(wolf_position, user_move)
        if new_wolf_position is not None:
            self.get_wolf().set_position(*new_wolf_position)

        new_sheep_positions = [self.calculate_new_position(pos, user_move) for pos in sheep_positions]
        for i in range(len(self.get_sheep())):
            if new_sheep_positions[i] is not None:
                self.get_sheep()[i].set_position(*new_sheep_positions[i])

    def update_positions_based_on_computer_move(self, computer_move):
        # Pobierz aktualne pozycje owiec i wilka
        wolf_position = self.get_wolf().get_position()
        sheep_positions = [sheep.get_position() for sheep in self.get_sheep()]

        # Zaktualizuj pozycje w zależności od ruchu komputera
        new_wolf_position = self.calculate_new_position(wolf_position, computer_move)
        if new_wolf_position is not None:
            self.get_wolf().set_position(*new_wolf_position)
            print(f"DEBUG: Nowa pozycja wilka po ruchu gracza: {new_wolf_position}")

        new_sheep_positions = [self.calculate_new_position(pos, computer_move) for pos in sheep_positions]
        for i in range(len(self.get_sheep())):
            if new_sheep_positions[i] is not None:
                self.get_sheep()[i].set_position(*new_sheep_positions[i])

    def calculate_new_position(self, current_position, move, sheep_positions=None):
        # Metoda do obliczania nowej pozycji na podstawie aktualnej pozycji i ruchu
        row, col = current_position
        print(f"DEBUG: Obliczanie nowej pozycji. Aktualna pozycja: {current_position}")
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

        # Sprawdź, czy nowa pozycja wykracza poza szachownicę
        if is_position_within_board(new_position):
            return new_position
        else:
            print(f"Nowa pozycja {new_position} wykracza poza szachownicę. Wybieranie nowej pozycji.")

            if self.current_player == self.player and sheep_positions is not None:
                new_sheep_positions = [self.calculate_new_position(pos, move) for pos in sheep_positions]
                for i in range(len(self.get_sheep())):
                    if new_sheep_positions[i] is not None:
                        self.get_sheep()[i].set_position(*new_sheep_positions[i])

            return self.calculate_new_position(current_position, "RANDOM_MOVE")

    def get_move_history(self):
        # Ustaw domyślną rolę, jeśli player_role nie jest ustawiona
        print(f"Komputer widzi grę jako {self.current_player.get_role()}")
        player_role = self.current_player.get_player_role() if self.current_player.get_player_role() is not None else 'owca'

        # Uwzględnij rolę komputera
        if isinstance(self.current_player, ComputerPlayer):
            player_role = self.current_player.get_role()

        return self.move_history.get(player_role, [])

    def is_game_over(self):
        if self.is_wolf_winner():
            print("DEBUG: Wolf wins condition met")
            return True, "Wilk wygrywa!"
        elif self.is_sheep_winner():
            print("DEBUG: Sheep wins condition met")
            return True, "Owce wygrywają!"
        elif self.is_blocked():
            print("DEBUG: Blocked condition met")
            return True, "Owce zablokowały wilka. Koniec gry!"

        return False, "Gra trwa."

    def is_wolf_winner(self):
        row, col = self.wolf.get_position()
        wolf_winner = col == 7

        return wolf_winner

    def is_sheep_winner(self):
        sheep_winner = all(sheep.get_position()[1] == 0 for sheep in self.sheep)

        return sheep_winner

    def is_blocked(self):
        row, col = self.wolf.get_position()
        blocked_condition = all(
            sheep.get_position() == (row - 1, col) or sheep.get_position() == (row + 1, col)
            for sheep in self.sheep)

        return blocked_condition
