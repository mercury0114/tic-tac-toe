from copy import deepcopy
from utils import AvailableMoves, BestMove, CandidateMoves
from utils import Flatten, PlyCount, GameWon
from utils import OPPONENT_TURN, EMPTY
from math import log, sqrt
from random import choice, shuffle
from time import time
import numpy as np

def Select(board, turn, counts, scores):
    # Variable names logN, w, n are taken from the wikipedia article about the MCTS
    logN = log(counts[str(board)])
    ucb_and_moves = []
    for row, col in CandidateMoves(board):
        board[row][col] = turn
        w = scores[str(board)]
        n = counts[str(board)]
        ucb_and_moves.append((w * turn / n + 2 * sqrt(logN / n), row, col))
        board[row][col] = EMPTY
    _, best_row, best_col = max(ucb_and_moves)
    return best_row, best_col

def UpdateStatistics(game, counts, scores, score):
    for position in game:
        position_str = str(position)
        counts.setdefault(position_str, 0)
        counts[position_str] += 1
        scores.setdefault(position_str, 0)
        scores[position_str] += score

class MonteCarloOpponent:
    def __init__(self, rows_count, cols_count, k, simulation_count):
        self.rows_count, self.cols_count = rows_count, cols_count
        self.k, self.simulation_count = k, simulation_count

    def FinishGame(self, starting_position, last_row, last_col,
                           ply_count, turn):
        board = deepcopy(starting_position)
        moves = AvailableMoves(board)
        shuffle(moves)
        while not GameWon(board, last_row, last_col, self.k) and \
                ply_count < self.rows_count * self.cols_count:
            last_row, last_col = moves[-1]
            board[last_row][last_col] = turn
            turn = -turn
            ply_count += 1
            moves.remove((last_row, last_col))
        return GameWon(board, last_row, last_col, self.k)

    def Expand(self, game, last_row, last_col, ply_count, turn, \
                   counts, scores):
        score = GameWon(game[-1], last_row, last_col, self.k)
        if (score or ply_count == self.rows_count * self.cols_count):
            UpdateStatistics(game, counts, scores, score)
            return
        for row, col in CandidateMoves(game[-1]):
            board = deepcopy(game[-1])
            board[row][col] = turn
            score = self.FinishGame(board, row, col, ply_count + 1, -turn)
            game.append(board)
            UpdateStatistics(game, counts, scores, score)
            game.pop()

    def GetCountsAndScores(self, board, original_turn):
        counts, scores = {}, {}
        expanded = set()
        ply_count = PlyCount(board)
        for simulation_nr in range(self.simulation_count):
            turn = original_turn
            row, col = -1, -1
            extra_plies = 0
            history = [deepcopy(board)]
            while not GameWon(history[-1], row, col, self.k) and \
                    ply_count + extra_plies < self.rows_count * self.cols_count and \
                    str(history[-1]) in expanded:
                row, col = Select(history[-1], turn, counts, scores)
                next_board = deepcopy(history[-1])
                next_board[row][col] = turn
                history.append(next_board)
                extra_plies += 1
                turn = -turn
            self.Expand(history, row, col, ply_count + extra_plies, turn, counts, scores)
            expanded.add(str(history[-1]))
        return counts, scores
        
    def find_move(self, board, window):
        counts, scores = self.GetCountsAndScores(board, OPPONENT_TURN)       
        best = []
        for row, col in CandidateMoves(board):
            board[row][col] = OPPONENT_TURN
            best.append((counts[str(board)], row, col))
            board[row][col] = EMPTY
        print(best)
        _, best_row, best_col = max(best)    
        return best_row, best_col

def Example():
    opponent = MonteCarloOpponent(3, 3, 3)
    board = [[0,0,0],[0,0,0],[0,0,0]]
    return opponent.GetCountsAndScores(board, -1)
