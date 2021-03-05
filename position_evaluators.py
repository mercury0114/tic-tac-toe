from copy import deepcopy
from random import shuffle
from utils import ToVector, GameResult, AvailableMoves
from utils import MY_TURN, OPPONENT_TURN

# each evaluator class should implement self.evaluate function
# the function returns the sum of scores and the number of times
# the position was evaluated. Note that for most evaluators,
# the second return parameter will be 1.

class ConstantEvaluator:
    def evaluate(self, position, last_row, last_col, ply_count):
        return 0, 1

class RandomGameEvaluator:
    def __init__(self, k, evaluation_count):
        self.k, self.evaluation_count = k, evaluation_count

    def evaluate_playing_randomly(self, position, last_row, last_col, ply_count):
        board = deepcopy(position)
        turn = MY_TURN if ply_count % 2 == 0 else OPPONENT_TURN
        moves = AvailableMoves(board)
        shuffle(moves)
        index = 0
        result = GameResult(board, last_row, last_col, self.k, ply_count)
        while result is None:
            last_row, last_col = moves[index]
            index += 1
            board[last_row][last_col] = turn
            turn = -turn
            ply_count += 1
            result = GameResult(board, last_row, last_col, self.k, ply_count)
        return result

    def evaluate(self, position, last_row, last_col, ply_count):
        result = 0
        for _ in range(self.evaluation_count):
            result += self.evaluate_playing_randomly(position, last_row, last_col, ply_count)
        return result, self.evaluation_count

class NeuralNetworkEvaluator:
    def __init__(self, network):
        self.network = network

    def evaluate(self, board, last_row, last_col, ply_count):
        return self.network.predict([ToVector(board)]), 1
