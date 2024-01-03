import random
from Players.Player import Player


def is_position_within_board(position, BOARD_SIZE=8, TILE_SIZE=50):
    max_coordinate = BOARD_SIZE * TILE_SIZE
    return 0 <= position[0] < max_coordinate and 0 <= position[1] < max_coordinate


class ComputerPlayer(Player):
    def __init__(self):
        super().__init__()

    def get_role(self):
        return self.role

    def set_player_role(self, role):
        self.role = role

    def get_possible_moves(self, wolf_position, sheep_positions):
        possible_moves = []

        if self.role == "wilk":
            # Dostępne ruchy dla wilka (na ukos, nie opuszczając planszy)
            moves = [
                ("DIAGONAL_UP_LEFT", lambda pos: (pos[0] - 1, pos[1] - 1)),
                ("DIAGONAL_UP_RIGHT", lambda pos: (pos[0] - 1, pos[1] + 1)),
                ("DIAGONAL_DOWN_LEFT", lambda pos: (pos[0] + 1, pos[1] - 1)),
                ("DIAGONAL_DOWN_RIGHT", lambda pos: (pos[0] + 1, pos[1] + 1))
            ]

            for move_name, move_func in moves:
                new_position = move_func(wolf_position)
                if is_position_within_board(new_position):
                    possible_moves.append(move_name)

            # Dodaj ruch losowy
            possible_moves.append("RANDOM")
