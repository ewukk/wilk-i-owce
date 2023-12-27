class Player:
    def __init__(self):
        self.role = None

    def make_move(self):
        # Ta metoda powinna zwrócić ruch gracza
        raise NotImplementedError("make_move method must be implemented in derived classes")


class SheepPlayer(Player):
    def make_move(self):
        direction_x = int(input("Podaj kierunek ruchu owiec w osi x (-1, 0, 1): "))
        return direction_x, 0  # Owce poruszają się tylko w osi x


class WolfPlayer(Player):
    def make_move(self):
        direction_x = int(input("Podaj kierunek ruchu wilka w osi x (-1, 0, 1): "))
        direction_y = int(input("Podaj kierunek ruchu wilka w osi y (-1, 0, 1): "))
        return direction_x, direction_y
