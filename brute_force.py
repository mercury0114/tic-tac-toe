import utils
import numpy as np
from neural_network import ConstructDenseNetwork

def MinMax(board, last_row, last_col, turn, ply_count, answer):
    position_str = str(utils.ToVector(board))

    result = utils.GameResult(board, last_row, last_col, 3, ply_count)
    if result is not None:
        answer[position_str] = result
        return result * turn

    moves = utils.AvailableMoves(board)
    if not moves:
        answer[position_str] = 0
        return 0

    if position_str in answer:
        return answer[position_str] * turn
    
    score = -1
    for row, col in moves:
        board[row][col] = turn
        move_score = -MinMax(board, row, col, -turn, ply_count + 1, answer)
        score = max(score, move_score)
        board[row][col] = 0
        
    answer[position_str] = score * turn
    return score

def Solve3By3():
    board = [[0,0,0],[0,0,0],[0,0,0]]
    answer = {}
    MinMax(board, -1, -1, -1, 0, answer)
    X = []
    y = []
    for position_str, score in answer.items():
        X.append(eval(position_str))
        y.append(score)
    return X, y

def TrainOptimal3By3Network():
    X, y = Solve3By3()
    network = ConstructDenseNetwork(3, 3)
    network.fit(np.array(X), np.array(y),
                validation_split = 0.2, batch_size=10, epochs=200)
    network.save("data/optimal_3_by_3_network")
    return network
