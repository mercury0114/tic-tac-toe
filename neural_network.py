import numpy as np
import tensorflow as tf
from keras.layers import Dense, Flatten, Conv2D, Dropout
from keras.models import Sequential, load_model
from keras.callbacks import EarlyStopping
from monte_carlo import MonteCarloOpponent
from utils import MY_TURN, EMPTY, OPPONENT_TURN
from utils import GameWon, Flatten, AvailableMoves
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

def UpdateTrainingData(all_counts, all_scores, new_counts, new_scores):
    for position_str in new_counts:
        all_counts[position_str] = new_counts[position_str]
        all_scores[position_str] = new_scores[position_str]
    X, y = [], []
    for position_str in all_counts:
        if (all_counts[position_str] > 4):
            X.append(Flatten(eval(position_str)))
            y.append(all_scores[position_str] / all_counts[position_str])
    return np.array(X), np.array(y)

def TrainNetwork(rows_count, cols_count, k):
    network = ConstructDenseNetwork(rows_count, cols_count)
    opponent = MonteCarloOpponent(rows_count, cols_count, k, 1000000)
    initial_board = [[0 for _ in range(cols_count)] for _ in range(rows_count)]
    new_counts, new_scores = opponent.GetCountsAndScores(initial_board, MY_TURN)
    X, y = UpdateTrainingData({}, {}, new_counts, new_scores)
    earlyStopper = EarlyStopping(monitor='val_loss', patience=200, verbose=1)
    fit_results = network.fit(X, y,
                validation_split=0.2, batch_size = 10, epochs=5000,
                callbacks=[earlyStopper])
    network.save("data/final_network")
    return network
    
    
class NeuralNetworkOpponent:
    def __init__(self, rows_count, cols_count, model_file):
        self.rows_count = rows_count
        self.cols_count = cols_count
        self.network = load_model(model_file)

    def find_move(self, board, window):
        scores = []
        for row,col in AvailableMoves(board):
            board[row][col] = OPPONENT_TURN
            score = self.network.predict([Flatten(board)])[0][0]
            scores.append((score, row, col))
            board[row][col] = EMPTY
        scores.sort(reverse=True)
        _, best_row, best_col = scores[0]
        print(best_row, best_col)
        return best_row, best_col
