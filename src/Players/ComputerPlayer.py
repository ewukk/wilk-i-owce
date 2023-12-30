import random
from Players.Player import Player


class ComputerPlayer(Player):
    def __init__(self):
        super().__init__()

    def set_role(self, role):
        self.role = role

    def make_move(self):
        wolf_position = self.get_wolf_position()  # Dodaj tę metodę w klasie Player
        sheep_positions = self.get_sheep_positions()  # Dodaj tę metodę w klasie Player
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
            for sheep_position in sheep_positions:
                if sheep_position[0] < wolf_position[0]:
                    possible_moves.append("RIGHT")
                elif sheep_position[0] > wolf_position[0]:
                    possible_moves.append("LEFT")

                if sheep_position[1] < wolf_position[1]:
                    possible_moves.append("DOWN")
                elif sheep_position[1] > wolf_position[1]:
                    possible_moves.append("UP")

            # Dodaj ruch losowy
            possible_moves.append("RANDOM")

        elif self.role == "owca":
            for sheep_position in sheep_positions:
                if wolf_position[0] < sheep_position[0]:
                    possible_moves.append("RIGHT")
                elif wolf_position[0] > sheep_position[0]:
                    possible_moves.append("LEFT")

                if wolf_position[1] < sheep_position[1]:
                    possible_moves.append("DOWN")
                elif wolf_position[1] > sheep_position[1]:
                    possible_moves.append("UP")

            # Dodaj ruch losowy
            possible_moves.append("RANDOM")

        return possible_moves
