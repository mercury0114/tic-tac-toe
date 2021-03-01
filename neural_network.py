import numpy as np
import tensorflow as tf
from keras.layers import Dense, Flatten, Conv2D, Dropout
from keras.models import Sequential, load_model
from keras.callbacks import EarlyStopping
from monte_carlo import MonteCarloOpponent
from utils import MY_TURN, EMPTY, OPPONENT_TURN
from utils import GameWon, Flatten, CandidateMoves, PlyCount
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

def CreateTrainingData(counts, scores):
    X, y = [], []
    for position_str in counts:
        if (counts[position_str] > 4):
            X.append(Flatten(eval(position_str)))
            y.append(scores[position_str] / counts[position_str])
    return np.array(X), np.array(y)

def TrainNetwork(rows_count, cols_count, k):
    network = ConstructDenseNetwork(rows_count, cols_count)
    opponent = MonteCarloOpponent(rows_count, cols_count, k, 400000)
    initial_board = [[0 for _ in range(cols_count)] for _ in range(rows_count)]
    counts, scores = opponent.GetCountsAndScores(initial_board, MY_TURN)
    print("Creating training data")
    X, y = CreateTrainingData(counts, scores)
    print("Training a network with sample size", len(X))
    earlyStopper = EarlyStopping(monitor='val_loss', patience=30, verbose=1)
    fit_results = network.fit(X, y,
                validation_split=0.2, batch_size = 10, epochs=200,
                callbacks=[earlyStopper])
    network.save("data/final_network")
    return network

def ScoreMoves(network, board, turn, ply_count, moves):
    X = []
    for row, col in moves:
        board[row][col] = turn
        X.append(Flatten(board))
        board[row][col] = EMPTY
    y = (network.predict(X) + 1) ** 5
    return Flatten(y / sum(y))
    
class NeuralNetworkOpponent:
    def __init__(self, rows_count, cols_count, k, model_file):
        self.rows_count = rows_count
        self.cols_count = cols_count
        self.k = k
        self.network = load_model(model_file)

    def find_move(self, board, window):
        scores = []
        for row,col in CandidateMoves(board):
            board[row][col] = OPPONENT_TURN
            score = GameWon(board, row, col, self.k)
            if (not score and PlyCount(board) < self.rows_count * self.cols_count):
                score = self.network.predict([Flatten(board)])[0][0]
            scores.append((score, row, col))
            board[row][col] = EMPTY
        scores.sort(reverse=True)
        _, best_row, best_col = scores[0]
        print(best_row, best_col)
        return best_row, best_col
