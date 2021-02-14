import numpy as np
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential, load_model
from keras.callbacks import EarlyStopping
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
        moves = utils.AvailableMoves(board)
        # Making a next move
        if np.random.binomial(1, p=0.1):
            # Next move will be random
            last_row, last_col = random.choice(moves)
        else:
	    # Next move will be one of the best moves, so need to evaluate all of them
            X = []
            for row, col in moves:
                board[row][col] = turn
                X.append(Flatten(board))
                board[row][col] = utils.EMPTY
            scores = network.predict(X).astype(np.float64)
            scores = (scores + 1) ** 7
            scores /= sum(scores)
            scores = Flatten(scores)
            
            index = np.random.choice(range(len(scores)), p = scores)
            last_row, last_col = moves[index]
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
    best_val_loss = 1000
    for network_update_iteration in range(10):
        print("iteration: ", network_update_iteration)
        scores = {}
        counts = {}
        for game_nr in range(30):
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
        earlyStopper = EarlyStopping(monitor='val_loss', patience=25, verbose=1)    
        fit_results = network.fit(np.array(X), np.array(y),
                    validation_split=0.3, batch_size = 10, epochs=100,
                    callbacks=[earlyStopper])
        if fit_results.history['val_loss'][-1] < best_val_loss:
            best_val_loss = fit_results.history['val_loss'][-1]
            print("Saving a network with the best_val_loss = {}".format(best_val_loss))
            network.save("data/intermediate_best_network")
    network.save("data/final_network")
    return network
    
class NeuralNetworkOpponent:
    def __init__(self, rows_count, cols_count, model_file):
        self.rows_count = rows_count
        self.cols_count = cols_count
        self.network = load_model(model_file)

    def find_move(self, board, window):
        scores = []
        for row,col in utils.AvailableMoves(board):
            board[row][col] = utils.OPPONENT_TURN
            score = self.network.predict([Flatten(board)])[0][0]
            scores.append((score, row, col))
            board[row][col] = utils.EMPTY
        scores.sort(reverse=True)
        _, best_row, best_col = scores[0]
        print(best_row, best_col)
        return best_row, best_col
