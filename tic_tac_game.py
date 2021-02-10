from tkinter import Tk, Button, LEFT
import opponent
import threading
import time
import numpy

MY_TURN = -1
OPPONENT_TURN = 1
EMPTY = 0
COLOURS = { MY_TURN : "black", OPPONENT_TURN : "red" }
TITLES = { MY_TURN : "Your move", OPPONENT_TURN : "Please wait" }

# returns -1 if I won, 1 if I lost, 0 if the game continues or is a draw
def GameEnded(board, k):
    directions = [[0, 1], [1, 1], [1, 0], [1, -1]]
    for row in range(len(board)):
        for col in range(len(board[0])):
            for direction in directions:
                count = 0
                score = 0
                next_row, next_col = row, col
                while (count < k and next_row < len(board) and
                    next_col >= 0 and next_col < len(board[0])):
                        score += board[next_row][next_col]
                        count += 1
                        next_row += direction[0]
                        next_col += direction[1]
                        if abs(score) == k:
                            return numpy.sign(score)
    return 0

def FullBoard(board):
    for row in range(len(board)):
        for col in range(len(board[0])):
            if (board[row][col] == EMPTY):
                return False
    return True

class Game:
    def __init__(self, rows_count, cols_count, k, opponent):
        # setting board dimension
        self.rows_count, self.cols_count, self.k = rows_count, cols_count, k
        self.board = [[EMPTY for _ in range(self.rows_count)]
            for _ in range(self.cols_count)]
        
        self.current_turn = MY_TURN
        self.opponent = opponent

        # Displaying board
        self.window = Tk()
        self.window.title("You start")
        self.buttons = []
        for row in range(rows_count):
            for col in range(cols_count):
                b = Button(self.window, height=1, width=1,
                        command = lambda row=row, col=col:
                            self.try_fill(row, col))
                b.grid(row = row, column = col)
                self.buttons.append(b)

    def start(self):
        opponent_thread = threading.Thread(target = self.respond, args=())
        opponent_thread.daemon = True
        opponent_thread.start()
        self.window.mainloop()

    def respond(self):
        while True:
            if (self.current_turn == MY_TURN):
                time.sleep(0.5)
                continue
            if not FullBoard(self.board) and not GameEnded(self.board, self.k):
                opponents_row, opponents_col = self.opponent.make_move(self.board, self.window)
                self.try_fill(opponents_row, opponents_col)

    def try_fill(self, row, col):
        if (not GameEnded(self.board, self.k) and self.board[row][col] == EMPTY):
            self.board[row][col] = self.current_turn
            self.buttons[row * self.rows_count + col].configure(bg=COLOURS[self.current_turn])
            self.current_turn = -self.current_turn
        game_ended = GameEnded(self.board, self.k)
        full_board = FullBoard(self.board)
        if (game_ended == MY_TURN):
            self.window.title("Congratulations, you won!")
            return
        if (game_ended == OPPONENT_TURN):
            self.window.title("You lost...")
            return
        if (full_board):
            self.window.title("Draw, not bad")
            return
        self.window.title(TITLES[self.current_turn])

