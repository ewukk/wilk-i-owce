class Sheep:
    def __init__(self, row, col, index):
        self.row = row
        self.col = col
        self.index = index
        self.position = (row, col)

    def get_position(self):
        return self.position

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_index(self):
        return f"sheep{self.index}"

