from flask import Flask, session
from Players.Player import Player, SheepPlayer, WolfPlayer
from Players.ComputerPlayer import ComputerPlayer
from Figures.Sheep import Sheep
from Figures.Wolf import Wolf

app = Flask(__name__)


class Game:
    def __init__(self, player, computer_player):
        self.app = app
        self.player = player
        self.computer_player = computer_player
        self.players = [self.player, self.computer_player]
        self.init_flask_routes()

        self.player = self.create_player(session.get('player_role', 'owca'))
        self.wolf = Wolf(350, 50)
        self.sheep = [Sheep(50 * i, 350) for i in range(8)]

    def create_player(self, role):
        if role == 'owca':
            return SheepPlayer()
        elif role == 'wilk':
            return WolfPlayer()
        else:
            raise ValueError(f"Nieznana rola: {role}")

    def init_flask_routes(self):
        @self.app.route('/play_turn')
        def play_turn():
            result = self.play_turn()
            return result

    def play_turn(self):
        result = "Aktualny stan gry: "  # Początkowa wartość wyniku gry

        for player in self.players:
            move = player.make_move()
            result += f"\n{player.name} wykonuje ruch: {move}"

        if self.is_wolf_winner():
            result += "\nWilk wygrywa!"
        elif self.is_sheep_winner():
            result += "\nOwce wygrywają!"
        elif self.is_blocked():
            result += "\nOwce zablokowały wilka. Koniec gry!"
        else:
            self.app.after(1000, self.play_turn)

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
    app_instance = Game(player, computer_player)
    app_instance.app.run(debug=True)
