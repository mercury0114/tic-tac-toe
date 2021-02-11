from tkinter import Tk, Button, LEFT
import threading
import time
import numpy
import utils

MY_TURN = -1
OPPONENT_TURN = 1
EMPTY = 0
COLOURS = { MY_TURN : "black", OPPONENT_TURN : "red" }
TITLES = { MY_TURN : "Your move", OPPONENT_TURN : "Please wait" }

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
        self.last_row, self.last_col = -1, -1
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
                b = Button(self.window, height=1, width=2,
                        command = lambda row=row, col=col:
                            self.try_make_move(row, col))
                b.grid(row = row, column = col)
                self.buttons.append(b)

    def start(self):
        opponent_thread = threading.Thread(target = self.opponent_respond, args=())
        opponent_thread.daemon = True
        opponent_thread.start()
        self.window.mainloop()

    # returns -1 if I won, 0 if game continues, 1 if opponent won
    def game_won(self):
    	return (utils.ConsecutiveCount(self.board, self.last_row, self.last_col) == self.k) * \
            self.board[self.last_row][self.last_col]

    def full_board(self):
        return utils.PlyCount(self.board) == self.rows_count * self.cols_count

    def opponent_respond(self):
        while True:
            if (self.current_turn == MY_TURN or self.full_board() or self.game_won()):
                time.sleep(0.5)
                continue
            start_time = time.time()
            opponents_row, opponents_col = self.opponent.find_move(self.board, self.window)
            print("seconds for move: ", time.time() - start_time)
            self.try_make_move(opponents_row, opponents_col)
            print()

    # doesn't change the board state if the move is illegal or the game has ended
    def try_make_move(self, row, col):
        # updating board
        if not self.game_won() and self.board[row][col] == EMPTY:
            self.board[row][col] = self.current_turn
            self.buttons[row * self.rows_count + col].configure(bg=COLOURS[self.current_turn])
            self.last_row, self.last_col = row, col
            self.current_turn = -self.current_turn

        # updating display message
        game_won = self.game_won()
        if game_won == MY_TURN:
            self.window.title("Congratulations, you won!")
            return
        if game_won == OPPONENT_TURN:
            self.window.title("You lost...")
            return
        if self.full_board():
            self.window.title("Draw, not bad")
            return
        self.window.title(TITLES[self.current_turn])

