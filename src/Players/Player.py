class Player:
    def __init__(self):
        self.role = None
        self.position = None

    def make_move(self):
        if self.position is not None:
            return f"Aktualna pozycja gracza {self.role}: {self.position}"
        else:
            return f"{self.role} nie ma jeszcze ustawionej pozycji."

    def set_move(self, new_position=None):
        if new_position is not None:
            self.position = new_position


class SheepPlayer(Player):
    def get_wolf_position(self):
        return self.get_wolf().get_position()

    def get_sheep_positions(self):
        return [sheep.get_position() for sheep in self.get_sheep()]


class WolfPlayer(Player):
    def get_wolf_position(self):
        return self.get_wolf().get_position()

    def get_sheep_positions(self):
        return [sheep.get_position() for sheep in self.get_sheep()]
