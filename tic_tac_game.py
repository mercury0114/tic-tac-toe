from tkinter import Tk, Button, LEFT
import threading
from time import sleep, time
from utils import MY_TURN, EMPTY, OPPONENT_TURN
from utils import InitialBoard, GameResult, PlyCount

COLOURS = { MY_TURN : "black", EMPTY : "sandy brown", OPPONENT_TURN : "white" }
TITLES = { MY_TURN : "Your move", OPPONENT_TURN : "Please wait" }

class Game:
    def __init__(self, rows_count, cols_count, k, opponent):
        # setting board dimension
        self.rows_count, self.cols_count, self.k = rows_count, cols_count, k
        self.opponent = opponent
        self.last_row, self.last_col = -1, -1
        self.board = InitialBoard(rows_count, cols_count)
        self.current_turn = MY_TURN
        self.ply_count = 0
        self.game_result = None

        # Displaying board
        self.window = Tk()
        self.window.title("You start")
        self.buttons = []
        for row in range(rows_count):
            for col in range(cols_count):
                b = Button(self.window, height=1, width=2,
                        command = lambda row=row, col=col:
                            self.try_make_my_move(row, col))
                b.configure(bg=COLOURS[EMPTY], activebackground=COLOURS[MY_TURN])
                b.grid(row = row, column = col)
                self.buttons.append(b)

    def start(self):
        opponent_thread = threading.Thread(target = self.opponent_respond, args=())
        opponent_thread.daemon = True
        opponent_thread.start()
        self.window.mainloop()

    def opponent_respond(self):
        while True:
            if (self.current_turn == MY_TURN or self.game_result is not None):
                sleep(0.5)
                continue
            start_time = time()
            opponents_row, opponents_col = self.opponent.find_move(self.board, self.window)
            print("Found move in {} seconds".format(time() - start_time))
            self.make_move(opponents_row, opponents_col)

    # doesn't change the board state if the move is illegal or the game has ended
    def try_make_my_move(self, row, col):
        if (self.current_turn == MY_TURN and self.game_result is None and \
                self.board[row][col] == EMPTY):
            self.make_move(row, col)

    def make_move(self, row, col):
        # updating board
        self.board[row][col] = self.current_turn
        self.last_row, self.last_col = row, col
        self.ply_count += 1
        self.buttons[row * self.rows_count + col].configure(bg=COLOURS[self.current_turn])
        self.current_turn = -self.current_turn
        self.game_result = GameResult(self.board, row, col, self.k, self.ply_count)

        # updating display message
        if self.game_result == MY_TURN:
            self.window.title("Congratulations, you won!")
            return
        if self.game_result == OPPONENT_TURN:
            self.window.title("You lost...")
            return
        if self.game_result == EMPTY:
            self.window.title("Draw, not bad")
            return
        self.window.title(TITLES[self.current_turn])

