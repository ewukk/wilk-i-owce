class Wolf:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def get_position(self):
        return self.row, self.col

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self):
        return f"Wolf({self.row}, {self.col})"

