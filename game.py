class Game:
    def __init__(self, board):
        self.board = board
        self.height = len(board)
        self.width = len(board[0])
        self.player_x = 0
        self.player_y = 0

        self.find_player()

    def find_player(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == "P":
                    self.player_x = x
                    self.player_y = y
                    return

    def draw(self):
        for row in self.board:
            print("".join(row))

    def move(self, dx, dy):
        nx = self.player_x + dx
        ny = self.player_y + dy

        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return

        if self.board[ny][nx] == "X":
            return

        self.board[self.player_y][self.player_x] = "."
        self.player_x = nx
        self.player_y = ny
        self.board[ny][nx] = "P"
