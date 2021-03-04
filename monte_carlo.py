from copy import deepcopy
from utils import CandidateMoves, PlyCount, GameResult
from utils import MY_TURN, OPPONENT_TURN, EMPTY
from math import log, sqrt
from random import choices
from time import time

class MonteCarloOpponent:
    def __init__(self, rows_count, cols_count, k, evaluator, simulation_count):
        self.rows_count, self.cols_count, self.k = rows_count, cols_count, k
        self.evaluator, self.simulation_count = evaluator, simulation_count
        self.Q, self.N = {}, {}

    def clear_tables(self):
        self.Q.clear()
        self.N.clear()

    def select_move_with_largest_ucb_score(self, board, turn):
        logN = log(self.N[str(board)])
        ucb_and_moves = []
        for row, col in CandidateMoves(board, turn, self.k):
            board[row][col] = turn
            board_str = str(board)
            board[row][col] = EMPTY
            q = turn if board_str not in self.Q else self.Q[board_str]
            n = 1 if board_str not in self.N else self.N[board_str]
            ucb_and_moves.append((q * turn / n + 2 * sqrt(logN / n), row, col))
        _, best_row, best_col = max(ucb_and_moves)
        return best_row, best_col

    def run_simulation(self, board, turn, ply_count):
        history = []
        result = None
        row, col = -1, -1
        while result is None and str(board) in self.Q:
            history.append(str(board))
            row, col = self.select_move_with_largest_ucb_score(board, turn)
            board[row][col] = turn
            turn, ply_count = -turn, ply_count + 1
            result = GameResult(board, row, col, self.k, ply_count)
        if result is None:
            result = self.evaluator.evaluate(board, row, col, ply_count)
            board_str = str(board)
            self.N[board_str] = 1
            self.Q[board_str] = result
        for board_str in history:
            self.N[board_str] += 1
            self.Q[board_str] += result

    def find_move(self, board, window = None):
        ply_count = PlyCount(board)
        turn = MY_TURN if ply_count % 2 == 0 else OPPONENT_TURN
        # Optimisation not to do a search if there is only one good move
        moves = CandidateMoves(board, turn, self.k)
        if len(moves) == 1:
            return moves[0]

        # TODO(mariusl): check whether clearing tables helps or hurts
        self.clear_tables()
        for simulation in range(self.simulation_count):
            self.run_simulation(deepcopy(board), turn, ply_count)
            if window:
                window.title("Please wait, {}/{} checked".format(simulation+1, self.simulation_count))

        weights = []
        for row, col in moves:
            board[row][col] = turn
            board_str = str(board)
            board[row][col] = EMPTY
            w = 1 if board_str not in self.N else self.N[board_str] * self.N[board_str]
            weights.append(w)
        row, col = choices(moves, weights=weights)[0]
        return row, col
