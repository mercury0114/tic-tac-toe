import numpy as np
import tensorflow as tf
from keras.layers import Dense, Flatten, Conv2D, Dropout
from keras.models import Sequential, load_model
from keras.callbacks import EarlyStopping
import utils
import itertools
import random
import copy
import time

def ConstructMinimalNetwork(rows_count, cols_count):
    network = Sequential()
    network.add(Dense(rows_count * cols_count, activation="relu",
                      input_dim = rows_count * cols_count))
    network.add(Dense(1, activation="tanh"))
    network.compile(optimizer='adam', loss='mse', metrics=['mse'])
    return network

def ConstructDenseNetwork(rows_count, cols_count):
    network = Sequential()
    network.add(Dense(rows_count * cols_count * 8, activation = "relu",
                        input_dim = rows_count * cols_count))
    network.add(Dense(rows_count * cols_count * 4, activation = "relu"))
    network.add(Dropout(0.2))
    network.add(Dense(rows_count * cols_count * 2, activation = "relu"))
    network.add(Dropout(0.1))
    network.add(Dense(rows_count * cols_count, activation = "relu"))
    network.add(Dense(1, activation="tanh"))
    network.compile(optimizer='adam', loss='mse', metrics=['mse'])
    return network

def ConstructConvolutionalNetwork(rows_count, cols_count):
    network = Sequential()
    network.add(Conv2D(32, kernel_size=(3, 3), activation="relu",
                     padding="same", input_shape=(rows_count, cols_count, 3)))
    network.add(Conv2D(32, kernel_size=(3, 3), activation="relu",
                     padding="same"))
    network.add(Conv2D(32, kernel_size=(3, 3), activation="relu",
                       padding="same"))
    network.add(Conv2D(32, kernel_size=(3, 3), activation="relu",
                       padding="same"))
    network.add(Conv2D(32, kernel_size=(3, 3), activation="relu",
                       padding="same"))
    network.add(Flatten())
    network.add(Dense(64, activation="tanh"))
    network.add(Dense(1, activation="tanh"))
    network.compile(optimizer='adam', loss='mse', metrics=['mse'])
    return network

def SimulateSingleGame(network, rows_count, cols_count, k):
    board = [[utils.EMPTY for _ in range(rows_count)] for _ in range(cols_count)]
    last_row, last_col = -1, -1
    ply_count = 0
    turn = utils.MY_TURN
    game_history = [utils.Flatten(board)]
    while not utils.GameWon(board, last_row, last_col, k) and \
          ply_count < rows_count * cols_count:
        moves = utils.AvailableMoves(board)
        # Making a next move
        if np.random.binomial(1, p=0.1):
            # Next move will be random
            last_row, last_col = random.choice(moves)
        else:
	    # Next move will be the best move
            X = []
            for row, col in moves:
                board[row][col] = turn
                X.append(utils.Flatten(board))
                board[row][col] = utils.EMPTY
            scores = network.predict(X) * turn
            last_row, last_col = moves[np.argmax(scores)]
        board[last_row][last_col] = turn
        turn = -turn
        ply_count += 1
        
        game_history.append(utils.Flatten(board))
    return game_history, utils.GameWon(board, last_row, last_col, k)

def SimulateMultipleGames(network, games_count, rows_count, cols_count, k):
    scores = {}
    counts = {}
    for game_nr in range(games_count):
        print(game_nr)
        game_history, score = SimulateSingleGame(network, rows_count, cols_count, k)
        for position in game_history:
            position_str = str(position)
            scores.setdefault(position_str, 0)
            scores[position_str] += score
            counts.setdefault(position_str, 0)
            counts[position_str] += 1
    return scores, counts

def UpdateTrainingData(all_scores, all_counts, new_scores, new_counts):
    for position_str in new_scores:
        all_scores.setdefault(position_str, 0)
        all_scores[position_str] += new_scores[position_str]
        all_counts.setdefault(position_str, 0)
        all_counts[position_str] += new_counts[position_str]
    X, y = [], []
    for position_str in all_scores:
        X.append(eval(position_str))
        y.append(all_scores[position_str] / all_counts[position_str])
    return np.array(X), np.array(y)

def TrainNetwork(rows_count, cols_count, k):
    network = ConstructDenseNetwork(rows_count, cols_count)
    best_val_loss = 1000
    all_scores, all_counts = {}, {}
    for network_update_iteration in range(80):
        print("iteration {}, simulating games, please wait".format(
            network_update_iteration))
        new_scores, new_counts = SimulateMultipleGames(network, 1000, rows_count, cols_count, k)
        X, y = UpdateTrainingData(all_scores, all_counts, new_scores, new_counts)
        earlyStopper = EarlyStopping(monitor='val_loss', patience=50, verbose=1)
        fit_results = network.fit(X, y,
                    validation_split=0.2, batch_size = 10, epochs=500,
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
            score = self.network.predict([utils.Flatten(board)])[0][0]
            scores.append((score, row, col))
            board[row][col] = utils.EMPTY
        scores.sort(reverse=True)
        _, best_row, best_col = scores[0]
        print(best_row, best_col)
        return best_row, best_col
