import random
from Players.Player import Player


class ComputerPlayer(Player):
    def __init__(self):
        super().__init__()

    def set_role(self, role):
        self.role = role

    def set_player_role(self, role):
        if role == 'owca':
            self.role = 'wilk'
        elif role == 'wilk':
            self.role = 'owca'
        else:
            raise ValueError(f"Nieznana rola: {role}")

    def get_wolf_position(self):
        return self.get_wolf().get_position()

    def get_sheep_positions(self):
        return [sheep.get_position() for sheep in self.get_sheep()]

    def make_move(self):
        wolf_position = self.get_wolf_position()
        sheep_positions = self.get_sheep_positions()
        possible_moves = self.get_possible_moves(wolf_position, sheep_positions)
        if possible_moves:
            # Wybierz losowy dozwolony ruch
            return random.choice(possible_moves)
        else:
            return "Brak dostępnych ruchów"

    def get_computer_move(self, wolf_position, sheep_positions):
        print(f"Komputer widzi grę jako {self.role}")
        possible_moves = self.get_possible_moves(wolf_position, sheep_positions)
        if possible_moves:
            # Wybierz losowy dozwolony ruch
            chosen_move = random.choice(possible_moves)
            print(f"Komputer wybiera ruch: {chosen_move}")
            return chosen_move
        else:
            print("Brak dostępnych ruchów dla komputera")
            return "Brak dostępnych ruchów"

    def get_possible_moves(self, wolf_position, sheep_positions):
        possible_moves = []

        if self.role == "wilk":
            possible_moves.extend(["DIAGONAL_UP_LEFT", "DIAGONAL_UP_RIGHT", "DIAGONAL_DOWN_LEFT", "DIAGONAL_DOWN_RIGHT"])
            # Dodaj ruch losowy
            possible_moves.append("RANDOM")

        elif self.role == "owca":
            possible_moves.extend(["DIAGONAL_UP_LEFT", "DIAGONAL_UP_RIGHT"])
            # Dodaj ruch losowy
            possible_moves.append("RANDOM")

        return possible_moves
