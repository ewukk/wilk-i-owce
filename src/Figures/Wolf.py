class Wolf:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, direction_x, direction_y):
        """
        Metoda do poruszania się wilka.
        :param direction_x: Kierunek ruchu w osi x (-1, 0, 1).
        :param direction_y: Kierunek ruchu w osi y (-1, 0, 1).
        """
        self.x += direction_x
        self.y += direction_y

    def get_position(self):
        return self.x, self.y

    def set_position(self, x, y):
        self.x = x
        self.y = y
