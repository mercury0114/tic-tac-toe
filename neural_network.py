import numpy as np
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
import utils
import itertools
import random
import copy
import time

def Flatten(board):
    return np.ndarray.flatten(np.array(board)).tolist()

def ConstructNetwork(rows_count, cols_count):
    network = Sequential()
    network.add(Dense(64, activation = "tanh",
                        input_dim = rows_count * cols_count))
    network.add(Dense(64, activation = "tanh"))
    network.add(Dense(1, activation="tanh"))
    network.compile(optimizer='adam', loss='mse', metrics=['mse'])
    return network

def SimulateGamePlay(network, rows_count, cols_count, k):
    board = [[utils.EMPTY for _ in range(rows_count)] for _ in range(cols_count)]
    last_row, last_col = -1, -1
    ply_count = 0
    turn = utils.MY_TURN
    game_history = [Flatten(board)]
    while not utils.GameWon(board, last_row, last_col, k) and ply_count < rows_count * cols_count:
        # Evaluating all moves
        scores = []
        X = []
        moves = []
        for row, col in utils.AvailableMoves(board):
            moves.append((row, col))
            board[row][col] = turn
            X.append(Flatten(board))
            board[row][col] = utils.EMPTY
        y = network.predict(X)
        scores = [(y[i], moves[i][0], moves[i][1]) for i in range(len(moves))]
        scores.sort(reverse=True)

        # Making a next move
        if np.random.binomial(1, p=0.3):
            # Next move will be random
            _, last_row, last_col = random.choice(scores)
        else:
            # Next move will be one of the best moves
            index = min(np.random.geometric(p=0.6), len(scores))-1
            _, last_row, last_col = scores[index]
        board[last_row][last_col] = turn
        turn = -turn
        ply_count += 1
        
        game_history.append(Flatten(board))
    return game_history, utils.GameWon(board, last_row, last_col, k)

def ExamplePredict():
    network = ConstructNetwork(3, 3)
    board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    return network.predict([board])
            
def ExamplePlay():
    k = 3
    network = ConstructNetwork(3, 3)
    game_history, result = SimulateGamePlay(network, 3, 3, k)
    return game_history, [result for _ in game_history]

def TrainNetwork(rows_count, cols_count, k):
    network = ConstructNetwork(rows_count, cols_count)
    for network_update_iteration in range(80):
        print("iteration: ", network_update_iteration)
        scores = {}
        counts = {}
        for game_nr in range(300):
            print("Iteration {}, game_nr: {}".format(network_update_iteration, game_nr))
            game_history, score = SimulateGamePlay(network, rows_count, cols_count, k)
            for position in game_history:
                position_str = str(position)
                scores.setdefault(position_str, 0)
                scores[position_str] += score
                counts.setdefault(position_str, 0)
                counts[position_str] += 1
        X = []
        y = []
        for position_str in scores:
            X.append(eval(position_str))
            y.append(scores[position_str] / counts[position_str])
        checkPoint = ModelCheckpoint("data/intermediate_best_network", verbose=1,
                                     monitor='val_loss', mode='min', save_best_only=True)
        network.fit(np.array(X), np.array(y),
                    validation_split=0.3, batch_size = 10, epochs=300, callbacks=[checkPoint])
    network.save("data/final_network")
    return network
    


    
