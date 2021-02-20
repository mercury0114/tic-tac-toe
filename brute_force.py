import utils
import neural_network
import numpy as np

def MinMax(board, last_row, last_col, turn, answer):
    position_str = str(utils.Flatten(board))

    result = utils.GameWon(board, last_row, last_col, 3)
    if result:
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
        move_score = -MinMax(board, row, col, -turn, answer)
        score = max(score, move_score)
        board[row][col] = 0
        
    answer[position_str] = score * turn
    return score

def Solve3By3():
    board = [[0,0,0],[0,0,0],[0,0,0]]
    answer = {}
    MinMax(board, -1, -1, -1, answer)
    X = []
    y = []
    for position_str, score in answer.items():
        X.append(eval(position_str))
        y.append(score)
    return X, y

def TrainOptimal3By3Network():
    X, y = Solve3By3()
    train_size = len(X) // 2
    print("Train size: ", train_size)
    
    network = neural_network.ConstructDenseNetwork(3, 3)
    network.fit(np.array(X[:train_size]), np.array(y[:train_size]),
                validation_split = 0.2, batch_size=10, epochs=200)
    network.save("data/optimal_3_by_3_network")
    return network

network = TrainOptimal3By3Network()
