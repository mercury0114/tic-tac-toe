from itertools import product
import numpy as np

MY_TURN = -1
OPPONENT_TURN = 1
EMPTY = 0

def InitialBoard(rows_count, cols_count):
    return [[0 for _ in range(rows_count)] for _ in range(cols_count)]

def ToVector(board):
    arr = np.array(board)
    return np.ndarray.flatten(np.array(board)).tolist()

def PlyCount(board):
    count = 0
    for row in range(len(board)):
        for col in range(len(board[0])):
            count += board[row][col] * board[row][col]
    return count

def InRange(board, row, col):
    return row >= 0 and row < len(board) and col >= 0 and col < len(board[0])

def ConsecutiveCount(board, row, col):
    directions = [[0, 1], [1, 1], [1, 0], [1, -1]]
    max_count = 1
    for direction in directions:
        forward_count = 0
        next_row = row + direction[0]
        next_col = col + direction[1]
        while InRange(board, next_row, next_col) and \
                board[next_row][next_col] == board[row][col]:
            forward_count += 1
            next_row += direction[0]
            next_col += direction[1]
        backward_count = 0
        next_row = row - direction[0]
        next_col = col - direction[1]
        while InRange(board, next_row, next_col) and \
                board[next_row][next_col] == board[row][col]:
            backward_count += 1
            next_row -= direction[0]
            next_col -= direction[1]
        max_count = max(max_count, 1 + forward_count + backward_count)
    return max_count

def AvailableMoves(board):
    return [(row,col) for row,col in product(range(len(board)), range(len(board[0]))) \
                if board[row][col] == EMPTY]

def AdjacentCount(board, row, col):
    count = 0
    directions = [[-1,-1], [-1, 0], [-1, 1], [0, -1], [0,1], [1, -1], [1, 0], [1, 1]]
    for direction in directions:
        r = row + direction[0]
        c = col + direction[1]
        if (r >= 0 and r < len(board) and c >= 0 and c < len(board[0])
            and board[r][c] != EMPTY):
            count += 1
    return count

def CandidateMoves(board, turn, k):
    moves = []
    for row, col in AvailableMoves(board):
        if AdjacentCount(board, row, col):
            board[row][col] = turn
            count = ConsecutiveCount(board, row, col)
            board[row][col] = EMPTY
            if count == k:
                return [(row, col)]
            moves.append((row, col))
    if not moves:
        moves.append((len(board) // 2, len(board[0]) // 2))
    return moves
                
def GameResult(board, last_row, last_col, k, ply_count):
    if last_row == -1:
        return None
    score = (ConsecutiveCount(board, last_row, last_col) == k) * board[last_row][last_col]
    if score:
        return score
    if ply_count < len(board) * len(board[0]):
        return None
    return 0

def ConvertToTrainingData(counts, scores):
    X, y = [], []
    for position_str in counts:
        X.append(eval(position_str))
        y.append(scores[position_str] / counts[position_str])
    return np.array(X), np.array(y)
