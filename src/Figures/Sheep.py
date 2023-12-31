class Sheep:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, direction):
        """
        Metoda do poruszania się owcy.
        :param direction: Kierunek ruchu (1 do przodu, -1 do tyłu).
        """
        if direction == 1:
            self.y += 1
        elif direction == -1:
            self.y -= 1

    def get_position(self):
        return self.x, self.y

    def set_position(self, x, y):
        self.x = x
        self.y = y
