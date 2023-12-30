import random

from flask import Flask, session, redirect
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
        self.move_history = {"owca": [], "wilk": []}
        self.wolf = Wolf(350, 50)
        self.sheep = [Sheep(50 * i, 350) for i in range(4)]

    def get_wolf(self):
        return self.wolf

    def get_sheep(self):
        return self.sheep

    def set_player_role(self, role):
        print(f"Setting player role to: {role}")
        if role == 'owca':
            self.player.set_player_role(role)
            self.computer_player.set_player_role('wilk')
            self.current_player = self.player
        elif role == 'wilk':
            self.player.set_player_role('owca')
            self.computer_player.set_player_role(role)
            self.current_player = self.computer_player
        else:
            raise ValueError(f"Nieznana rola: {role}")

        print(f"Player role set to: {self.current_player.get_role()}")

    def switch_player(self):
        self.current_player = (
            self.player if self.current_player == self.computer_player else self.computer_player
        )

    def play_turn(self, user_move=None):
        print("DEBUG: Play Turn - Start")
        result = "Aktualny stan gry: "

        if user_move:
            # Gracz wykonał ruch
            if self.last_move is not None:
                return "Możesz wykonać tylko jeden ruch w swojej turze."

            if self.player_role not in self.move_history:
                self.move_history[self.player_role] = []

            result += f"\n{self.current_player.get_role()} wykonuje ruch: {user_move}"

            if self.current_player is not None:
                self.move_history[self.player_role].append({"player": self.player_role, "move": user_move})

            self.last_move = user_move

            if self.is_game_over():
                result += self.is_game_over()[1]  # Dodaj informację o zakończeniu gry
                return result
        else:
            # Gracz nie wykonał ruchu, przekieruj z powrotem do gry
            print("DEBUG: Brak ruchu gracza.")
            return redirect('/game')

        # Sprawdź, czy użytkownik wykonał ruch
        is_game_over, computer_result = self.is_game_over()
        if not is_game_over:
            if self.last_move is not None:
                if isinstance(self.current_player, ComputerPlayer):
                    computer_move = self.get_computer_move()
                    print(f"DEBUG: Computer move: {computer_move}")
                    result += f"\n{self.current_player.get_role()} wykonuje ruch: {computer_move}"
                    self.move_history[self.current_player.get_role()].append(
                        {"player": self.current_player.get_role(), "move": computer_move}
                    )
                    self.last_move = computer_move
                    is_game_over, computer_result = self.is_game_over()
                    self.switch_player()  # Przełącz gracza po wykonaniu ruchu
                    print(f"DEBUG: Current player after computer move: {self.current_player.get_role()}")

        print(f"DEBUG: Play Turn - End. Result={result}")
        return result

    def get_move_history(self):
        # Ustaw domyślną rolę, jeśli player_role nie jest ustawiona
        print(f"Komputer widzi grę jako {self.role}")
        player_role = self.current_player.get_player_role() if self.current_player.get_player_role() is not None else 'owca'
        return self.move_history.get(player_role, [])

    def get_computer_move(self):
        print("DEBUG: Get Computer Move - Start")
        print(f"Komputer widzi grę jako {self.current_player.role}")

        if isinstance(self.current_player, ComputerPlayer):
            wolf_position = self.get_wolf().get_position()
            sheep_positions = [sheep.get_position() for sheep in self.get_sheep()]

            possible_moves = self.current_player.get_possible_moves(wolf_position, sheep_positions)

            if possible_moves:
                # Wybierz losowy dozwolony ruch
                chosen_move = random.choice(possible_moves)
                print(f"DEBUG: Computer possible moves: {possible_moves}")
                print(f"DEBUG: Computer chosen move: {chosen_move}")
                print("DEBUG: Get Computer Move - End")
                return chosen_move
            else:
                print("Brak dostępnych ruchów dla komputera")
                return "Brak dostępnych ruchów"
        else:
            print("Aktualny gracz nie jest komputerem, nie można uzyskać ruchu komputera.")
            return "Aktualny gracz nie jest komputerem, nie można uzyskać ruchu komputera"

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

    # def init_flask_routes(self):
