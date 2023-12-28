from flask import Flask, session
from Players.Player import Player, SheepPlayer, WolfPlayer
from Players.ComputerPlayer import ComputerPlayer
from Figures.Sheep import Sheep
from Figures.Wolf import Wolf

app = Flask(__name__)


class Game:
    def __init__(self, player, computer_player, player_role):
        self.app = app
        self.player = player
        self.computer_player = computer_player
        self.players = [self.player, self.computer_player]
        self.current_player = self.player
        self.init_flask_routes()
        self.last_move = None

        self.player = self.create_player(player_role)
        self.wolf = Wolf(350, 50)
        self.sheep = [Sheep(50 * i, 350) for i in range(4)]

    def get_wolf(self):
        return self.wolf

    def get_sheep(self):
        return self.sheep

    def set_player_role(self, role):
        self.player_role = role
        self.player = self.create_player(role)

    def create_player(self, role):
        if role is None or role == 'owca':
            return SheepPlayer()
        elif role == 'wilk':
            return WolfPlayer()
        else:
            raise ValueError(f"Nieznana rola: {role}")

    def switch_player(self):
        self.current_player = (
            self.player if self.current_player == self.computer_player else self.computer_player
        )

    def init_flask_routes(self):
        @self.app.route('/game')
        def play_turn():
            result = self.play_turn()
            return result

    def play_turn(self, user_move=None):
        # Get the move from the current player
        move = user_move

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

        # Przechowaj ostatni ruch
        session['last_move'] = move

        # Przełącz na kolejnego gracza
        self.switch_player()

        return result

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


if __name__ == "__main__":
    player = Player()
    computer_player = ComputerPlayer()
    player_role = session.get('player_role', 'owca')
    app_instance = Game(player, computer_player)
    app_instance.app.run(debug=True)
