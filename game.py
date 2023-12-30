from flask import Flask, session
from Players.Player import Player, SheepPlayer, WolfPlayer
from Players.ComputerPlayer import ComputerPlayer
from Figures.Sheep import Sheep
from Figures.Wolf import Wolf


def create_game_instance():
    player = Player()
    computer_player = ComputerPlayer()
    return Game(player, computer_player)


def create_player(role):
    if role is None or role == 'owca':
        return SheepPlayer()
    elif role == 'wilk':
        return WolfPlayer()
    else:
        raise ValueError(f"Nieznana rola: {role}")


class Game:
    def __init__(self, player, computer_player):
        # self.app = app  # Ta linia może być problemem, ale zostaw ją na razie
        self.player = player
        self.computer_player = computer_player
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
        self.player_role = role
        self.player = create_player(role)

    def switch_player(self):
        self.current_player = (
            self.player if self.current_player == self.computer_player else self.computer_player
        )

    def play_turn(self, user_move=None):
        # Get the move from the current player
        move = user_move

        if any(self.move_history["owca"]) or any(self.move_history["wilk"]):
            return "Możesz wykonać tylko jeden ruch w swojej turze."

        result = "Aktualny stan gry: "

        # Ustaw ruch gracza
        if isinstance(self.current_player, ComputerPlayer):
            move = self.current_player.get_computer_move(
                self.wolf.get_position(), [sheep.get_position() for sheep in self.sheep]
            )
            result += f"\n{self.current_player.role} wykonuje ruch: {move}"
        else:
            self.current_player.set_move(move)
            # Wykonaj ruch gracza
            move_result = self.current_player.make_move()
            result += f"\n{self.current_player.role} wykonuje ruch: {move_result}"

        # Sprawdź, czy player_role jest ustawiona
        if self.player_role is not None:
            self.move_history[self.player_role].append({"player": self.player_role, "move": move})
            session['last_move'] = move
        else:
            print("Błąd: player_role nie jest ustawiona")

        # Przełącz na kolejnego gracza
        self.switch_player()

        return result

    def get_move_history(self):
        # Ustaw domyślną rolę, jeśli player_role nie jest ustawiona
        player_role = self.current_player.role if self.current_player.role is not None else 'owca'
        return self.move_history.get(player_role, [])

    def get_computer_move(self):
        if isinstance(self.current_player, ComputerPlayer):
            computer_move = self.current_player.get_computer_move(
                self.wolf.get_position(), [sheep.get_position() for sheep in self.sheep]
            )
            return f"\nKomputer wykonuje ruch: {computer_move}"
        else:
            return "\nAktualny gracz nie jest komputerem, nie można uzyskać ruchu komputera."

    def is_game_over(self):
        result = "Aktualny stan gry: "

        if self.is_wolf_winner():
            result += "\nWilk wygrywa!"
        elif self.is_sheep_winner():
            result += "\nOwce wygrywają!"
        elif self.is_blocked():
            result += "\nOwce zablokowały wilka. Koniec gry!"

        return result

    def is_wolf_winner(self):
        x, y = self.wolf.get_position()
        return y == 0  # Wilk wygrywa, gdy dotrze na drugą stronę szachownicy

    def is_sheep_winner(self):
        return all(sheep.get_position()[1] == 0 for sheep in self.sheep)

    def is_blocked(self):
        x, y = self.wolf.get_position()
        return all(
            sheep.get_position() == (x - 1, y) or sheep.get_position() == (x + 1, y)
            for sheep in self.sheep)

    # def init_flask_routes(self):


