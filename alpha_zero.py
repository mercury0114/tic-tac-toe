from neural_network import ConstructDenseNetwork, ScoreMoves
from monte_carlo import MonteCarloOpponent
from utils import CandidateMoves, Flatten, GameEnded, InitialBoard, ConvertToTrainingData
from utils import PlyCount
from utils import EMPTY, MY_TURN, OPPONENT_TURN
from math import log, sqrt
from numpy import argmax, float64
from random import choices
from copy import deepcopy
from time import time

TRAIN_ITERATIONS_COUNT = 20
EPISODES_COUNT = 60
SIMULATION_COUNT = 300

def PlayOneGame(players, rows_count, cols_count, k):
    board = InitialBoard(rows_count, cols_count)
    ply_count = 0
    last_row, last_col = -1, -1
    turn = MY_TURN
    
    result = None
    while result is None:
        last_row, last_col = players[turn].find_move(board)
        board[last_row][last_col] = turn
        turn = -turn
        ply_count += 1
        result = GameEnded(board, last_row, last_col, k, ply_count)
    return result

def EvaluatesBetter(new_evaluator, current_evaluator, rows_count, cols_count, k):
    print("Checking who evaluates positions better")
    score = 0
    new_player = MonteCarloOpponent(rows_count, cols_count, k, new_evaluator, SIMULATION_COUNT)
    best_player = MonteCarloOpponent(rows_count, cols_count, k, current_evaluator, SIMULATION_COUNT)
    
    players = {MY_TURN : new_player, OPPONENT_TURN : best_player}
    for game_nr in range(EPISODES_COUNT // 2):
        print("white game nr: {},  score so far: {}".format(game_nr, score))
        score += MY_TURN * PlayOneGame(players, rows_count, cols_count, k)
    new_player.clear_tables()
    best_player.clear_tables()
    players = {MY_TURN : best_player, OPPONENT_TURN : new_player}
    for game_nr in range(EPISODES_COUNT // 2):
        print("black game nr: {}, score so far: {}".format(game_nr, score))
        score += OPPONENT_TURN * PlayOneGame(players, rows_count, cols_count, k)
    print("Final score: ", score)
    return score / EPISODES_COUNT >= 0.06


class NeuralNetworkEvaluator:
    def __init__(self, network):
        self.network = network

    def evaluate(self, board, last_row, last_col, ply_count):
        return self.network.predict([Flatten(board)])

def ExecuteEpisode(mcts):
    X = []
    board = InitialBoard(mcts.rows_count, mcts.cols_count)
    turn = MY_TURN
    ply_count = 0
    result = None
    while result is None:
        X.append(Flatten(board))
        row, col = mcts.find_move(board)
        board[row][col] = turn
        turn = -turn
        ply_count += 1
        result = GameEnded(board, row, col, mcts.k, ply_count)
    print("Result after {} plies: {}".format(ply_count, result))
    return X, result

def UpdateTrainingDataFromEpisodes(mcts, counts, rewards):
    for episode in range(EPISODES_COUNT):
        print("Episode: ", episode)
        start_time = time()
        new_X, reward = ExecuteEpisode(mcts)
        for x in new_X:
                str_x = str(x)
                counts.setdefault(str_x, 0)
                counts[str_x] += 1
                rewards.setdefault(str_x, 0)
                rewards[str_x] += reward
        print("Episode time: ", time() - start_time)
    return ConvertToTrainingData(counts, rewards)

def TrainNetwork(rows_count, cols_count, k):
    current_evaluator = NeuralNetworkEvaluator(ConstructDenseNetwork(rows_count, cols_count))
    counts, rewards = {}, {}
    for train_iteration in range(TRAIN_ITERATIONS_COUNT):
        print("Train iteration: ", train_iteration)
        monte_carlo = MonteCarloOpponent(rows_count, cols_count, k, \
                current_evaluator, SIMULATION_COUNT)
        X, y = UpdateTrainingDataFromEpisodes(monte_carlo, counts, rewards)
        new_evaluator = NeuralNetworkEvaluator(ConstructDenseNetwork(rows_count, cols_count))
        new_evaluator.network.fit(X, y, epochs=200, validation_split=0.2)
        if EvaluatesBetter(new_evaluator, current_evaluator, rows_count, cols_count, k):
            print("Evaluates better")
            current_evaluator.network = new_evaluator.network
    current_evaluator.network.save("data/final_network")
    return current_evaluator.network
        
