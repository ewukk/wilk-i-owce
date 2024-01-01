import random

from flask import session
from Players.Player import Player, SheepPlayer, WolfPlayer
from Players.ComputerPlayer import ComputerPlayer
from Figures.Sheep import Sheep
from Figures.Wolf import Wolf


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
        self.sheep = [Sheep(50 * i, 350) for i in range(4)]

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

    def is_computer_turn(self):
        print(f"DEBUG: Checking if it's computer's turn. Current player: {self.current_player.get_role()}")
        return self.current_player == self.computer_player

    def switch_to_player(self):
        self.current_player = self.player

    def switch_to_computer(self):
        self.current_player = self.computer_player

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

    def get_computer_move(self, wolf_position=None, sheep_positions=None, computer_role=None):
        global possible_moves, move_mapping
        print("DEBUG: Get Computer Move - Start")
        print(f"Komputer widzi grę jako {computer_role}")

        if isinstance(self.computer_player, ComputerPlayer):
            if wolf_position is None:
                wolf_position = self.get_wolf().get_position()
            if sheep_positions is None:
                sheep_positions = [sheep.get_position() for sheep in self.get_sheep()]

            # Sprawdź rolę komputera
            if computer_role == "wilk":
                possible_moves = self.computer_player.get_possible_moves(wolf_position, sheep_positions)
                # Dostosuj format ruchu do oczekiwanego formatu w grze
                move_mapping = {
                    "DIAGONAL_UP_LEFT": "UP_LEFT",
                    "DIAGONAL_UP_RIGHT": "UP_RIGHT",
                    "DIAGONAL_DOWN_LEFT": "DOWN_LEFT",
                    "DIAGONAL_DOWN_RIGHT": "DOWN_RIGHT",
                }
            elif computer_role == "owca":
                # Wybierz losową owcę
                chosen_sheep = random.choice(self.get_sheep())
                # Oblicz ruch na podstawie pozycji wybranej owcy
                chosen_move = self.calculate_new_position(wolf_position, chosen_sheep.get_position())
                possible_moves = [chosen_move]
                # Dostosuj format ruchu do oczekiwanego formatu w grze
                move_mapping = {
                    "DIAGONAL_UP_LEFT": "UP_LEFT",
                    "DIAGONAL_UP_RIGHT": "UP_RIGHT",
                }

            # Sprawdź dostępne ruchy
            if possible_moves:
                # Wybierz losowy dozwolony ruch
                chosen_move = random.choice(possible_moves)
                print(f"DEBUG: Computer possible moves: {possible_moves}")
                print(f"DEBUG: Computer chosen move: {chosen_move}")
                print("DEBUG: Get Computer Move - End")
                # Mapuj ruch na oczekiwany format w grze
                chosen_move = move_mapping.get(chosen_move, "RANDOM")
                return chosen_move
            else:
                print("Brak dostępnych ruchów dla komputera")
                return "Brak dostępnych ruchów"
        else:
            print(
                f"Aktualny gracz ({computer_role}) nie jest komputerem, nie można uzyskać ruchu komputera.")
            return "Aktualny gracz nie jest komputerem, nie można uzyskać ruchu komputera"

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

        new_sheep_positions = [self.calculate_new_position(pos, computer_move) for pos in sheep_positions]
        for i in range(len(self.get_sheep())):
            if new_sheep_positions[i] is not None:
                self.get_sheep()[i].set_position(*new_sheep_positions[i])

    def calculate_new_position(self, current_position, move):
        # Metoda do obliczania nowej pozycji na podstawie aktualnej pozycji i ruchu
        x, y = current_position
        if move == 'DIAGONAL_UP_LEFT':
            return x - 1, y - 1
        elif move == 'DIAGONAL_UP_RIGHT':
            return x - 1, y + 1
        elif move == 'DIAGONAL_DOWN_LEFT':
            return x + 1, y - 1
        elif move == 'DIAGONAL_DOWN_RIGHT':
            return x + 1, y + 1
        else:
            return x, y

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
        x, y = self.wolf.get_position()
        wolf_winner = y == 0

        return wolf_winner

    def is_sheep_winner(self):
        sheep_winner = all(sheep.get_position()[1] == 0 for sheep in self.sheep)

        return sheep_winner

    def is_blocked(self):
        x, y = self.wolf.get_position()
        blocked_condition = all(
            sheep.get_position() == (x - 1, y) or sheep.get_position() == (x + 1, y)
            for sheep in self.sheep)

        return blocked_condition
