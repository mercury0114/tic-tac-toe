from neural_network import ConstructDenseNetwork, ScoreMoves
from utils import CandidateMoves, Flatten, GameEnded, InitialBoard, ConvertToTrainingData
from utils import PlyCount
from utils import EMPTY, MY_TURN, OPPONENT_TURN
from math import log, sqrt
from numpy import argmax, float64
from random import choices
from copy import deepcopy

TRAIN_ITERATIONS_COUNT = 80
EPISODES_COUNT = 100
SIMULATION_COUNT = 1000

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

def PlaysBetter(new_network, best_network, rows_count, cols_count, k):
    score = 0
    new_player = MonteCarloTreeSearch(rows_count, cols_count, k, new_network)
    best_player = MonteCarloTreeSearch(rows_count, cols_count, k, best_network)
    
    players = {MY_TURN : new_player, OPPONENT_TURN : best_player}
    for game_nr in range(100):
        score += MY_TURN * PlayOneGame(players, rows_count, cols_count, k)
        print(score)
    new_player.clear_tables()
    best_player.clear_tables()
    players = {MY_TURN : best_player, OPPONENT_TURN : new_player}
    for game_nr in range(100):
        score += OPPONENT_TURN * PlayOneGame(players, rows_count, cols_count, k)
        print(score)
    return score >= 10

class MonteCarloTreeSearch:
    def __init__(self, rows_count, cols_count, k, network):
        self.rows_count, self.cols_count = rows_count, cols_count
        self.k = k
        self.network = network
        self.Q, self.N = {}, {}

    def clear_tables(self):
        self.Q.clear()
        self.N.clear()

    def search(self, board, last_row, last_col, turn, ply_count):
        score = GameEnded(board, last_row, last_col, self.k, ply_count)
        if score is not None:
            return score
        
        initial_board_str = str(board)
        if initial_board_str not in self.Q:
            self.Q[initial_board_str] = self.network.predict([Flatten(board)])
            self.N[initial_board_str] = 1 
            return self.Q[initial_board_str]

        logN = log(self.N[initial_board_str])
        scores = []
        moves = CandidateMoves(board, turn, self.k)
        for row, col in moves:
            board[row][col] = turn
            board_str = str(board)
            board[row][col] = EMPTY
            q = 0 if (not board_str in self.Q) else self.Q[board_str]
            n = 1 if (not board_str in self.N) else self.N[board_str]
            scores.append(q * turn + 2 * sqrt(logN / (n)))

        best_row, best_col = moves[argmax(scores)]     
        board[best_row][best_col] = turn
        v = self.search(board, best_row, best_col, -turn, ply_count + 1)
        self.Q[initial_board_str] = (self.N[initial_board_str] * self.Q[initial_board_str] \
                                         + v) / (self.N[initial_board_str] + 1)
        self.N[initial_board_str] += 1
        return v

    def find_move(self, board, window = None):
        ply_count = PlyCount(board)
        turn = MY_TURN if ply_count % 2 == 0 else OPPONENT_TURN
        last_row, last_col = -1, -1
        for iteration in range(SIMULATION_COUNT):
            if window:
                window.title("Please wait, {}/{} checked".format(iteration,
                                                                 len(SIMULATION_COUNT)))
            self.search(deepcopy(board), last_row, last_col, turn, ply_count)
        moves, weights = self.getMovesAndWeights(board, turn)
        row, col = choices(moves, weights=weights)[0]
        return row, col

    def getMovesAndWeights(self, board, turn):
        pi = []
        moves = CandidateMoves(board, turn, self.k)
        for row, col in moves:
            board[row][col] = turn
            board_str = str(board)
            board[row][col] = EMPTY
            if board_str in self.N:
                pi.append(self.N[board_str])
            else:
                pi.append(0)
        return moves, pi

def ExecuteEpisode(mcts):
    X = []
    board = InitialBoard(mcts.rows_count, mcts.cols_count)
    turn = MY_TURN
    ply_count = 0
    result = None
    while result is None:
        X.append(Flatten(board))
        row, col = mcts.find_move(board)
        print("New move: ", row, col)
        board[row][col] = turn
        turn = -turn
        ply_count += 1
        result = GameEnded(board, row, col, mcts.k, ply_count)
    return X, result

def UpdateTrainingData(mcts, counts, rewards):
    for episode in range(EPISODES_COUNT):
        print("Episode: ", episode)
        new_X, reward = ExecuteEpisode(mcts)
        for x in new_X:
                counts.setdefault(str(x), 0)
                counts[x] += 1
                rewards.setdefault(str(x), 0)
                rewards[x] += reward
    return ConvertToTrainingData(counts, rewards)

def TrainNetwork(rows_count, cols_count, k):
    best_network = ConstructDenseNetwork(rows_count, cols_count)
    counts, rewards = {}, {}
    for train_iteration in range(TRAIN_ITERATIONS_COUNT):
        print("Train iteration: ", train_iteration)
        mcts = MonteCarloTreeSearch(rows_count, cols_count, k, best_network)
        X, y = UpdateTrainingData(mcts, counts, rewards)
        new_network = ConstructDenseNetwork(rows_count, cols_count)
        new_newtork.fit(X, y, epochs=200, validation_split=0.2)
        if PlaysBetter(new_network, network):
            print("Plays better")
            network = new_network
    network.save("data/final_network")
    return network
        
