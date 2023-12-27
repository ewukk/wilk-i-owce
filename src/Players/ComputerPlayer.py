import random
from Players.Player import Player


def make_move():
    # Ta metoda zawiera algorytm, który decyduje, jaki ruch wykonuje komputer
    # Poniżej znajduje się przykładowy algorytm dla komputera, który porusza się losowo

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    return random.choice(directions)


class ComputerPlayer(Player):
    def __init__(self):
        super().__init__()

    def make_move(self):
        return make_move()