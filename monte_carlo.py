from copy import deepcopy
from utils import AvailableMoves, CandidateMoves
from utils import Flatten, PlyCount, GameEnded
from utils import MY_TURN, OPPONENT_TURN, EMPTY
from math import log, sqrt
from random import choice, choices, shuffle
from time import time
from numpy import argmax

class MonteCarloOpponent:
    def __init__(self, rows_count, cols_count, k, evaluator, simulation_count):
        self.rows_count, self.cols_count, self.k = rows_count, cols_count, k
        self.evaluator, self.simulation_count = evaluator, simulation_count
        self.Q, self.N = {}, {}

    def clear_tables(self):
        self.Q.clear()
        self.N.clear()

    def select_move_with_largest_ucb_score(self, board, turn):
        N = self.N[str(board)]
        ucb_and_moves = []
        for row, col in CandidateMoves(board):
            board[row][col] = turn
            board_str = str(board)
            board[row][col] = EMPTY
            q = turn if board_str not in self.Q else self.Q[board_str]
            n = 1 if board_str not in self.N else self.N[board_str]
            ucb_and_moves.append((q * turn + 2 * sqrt(log(N) / n), row, col))
        _, best_row, best_col = max(ucb_and_moves)
        return best_row, best_col

    def run_simulation(self, board, last_row, last_col, turn, ply_count):
        score = GameEnded(board, last_row, last_col, self.k, ply_count)
        if score is not None:
            return score
        
        initial_board_str = str(board)
        if initial_board_str not in self.Q:
            self.Q[initial_board_str] = self.evaluator.evaluate(board, last_row, last_col, ply_count)
            self.N[initial_board_str] = 1 
            return self.Q[initial_board_str]

        best_row, best_col = self.select_move_with_largest_ucb_score(board, turn)     
        board[best_row][best_col] = turn
        q = self.run_simulation(board, best_row, best_col, -turn, ply_count + 1)
        self.Q[initial_board_str] = (self.N[initial_board_str] * self.Q[initial_board_str] + q) \
                                     / (self.N[initial_board_str] + 1)
        self.N[initial_board_str] += 1
        return q

    def find_move(self, board, window = None):
        ply_count = PlyCount(board)
        turn = MY_TURN if ply_count % 2 == 0 else OPPONENT_TURN
        
        # Optimisation not to do a search if there is only one good move
        moves = CandidateMoves(board, turn, self.k)
        if len(moves) == 1:
            return moves[0]

        for iteration in range(self.simulation_count):
            self.run_simulation(deepcopy(board), -1, -1, turn, ply_count)
            if window:
                window.title("Please wait, {}/{} checked".format(iteration+1, self.simulation_count))
       
        weights = []
        for row, col in moves:
            board[row][col] = turn
            board_str = str(board)
            board[row][col] = EMPTY
            N = 1 if board_str not in self.N else self.N[board_str]
            weights.append(N)
        row, col = choices(moves, weights=weights)[0]
        return row, col
