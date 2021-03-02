from copy import deepcopy
from random import shuffle
from utils import Flatten, GameEnded, AvailableMoves
from utils import MY_TURN, OPPONENT_TURN

class ConstantEvaluator:
    def evaluate(self, position, last_row, last_col, ply_count):
        return 0

class RandomGameEvaluator:
    def __init__(self, k):
        self.k = k

    def evaluate(self, position, last_row, last_col, ply_count):
        board = deepcopy(position)
        turn = MY_TURN if ply_count % 2 == 0 else OPPONENT_TURN
        moves = AvailableMoves(board)
        shuffle(moves)
        index = 0
        result = GameEnded(board, last_row, last_col, self.k, ply_count)
        while result is None:
            last_row, last_col = moves[index]
            index += 1
            board[last_row][last_col] = turn
            turn = -turn
            ply_count += 1
            result = GameEnded(board, last_row, last_col, self.k, ply_count)
        return result

class NeuralNetworkEvaluator:
    def __init__(self, network):
        self.network = network

    def evaluate(self, board, last_row, last_col, ply_count):
        return self.network.predict([Flatten(board)])
