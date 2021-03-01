#import alpha_beta_opponent
import tic_tac_game
import sys
#from neural_network import NeuralNetworkOpponent
from monte_carlo import MonteCarloOpponent

def PrintUsageAndExit():
    print("python3 main.py [ROWS_COUNT] [COLS_COUNT] [K]")
    print("or to use default k=5:")
    print("python3 main.py [ROWS_COUNT] [COLS_COUNT]")
    sys.exit()

ROWS_COUNT = 15
COLS_COUNT = 15
K = 5

# Parsing command line arguments
if len(sys.argv) == 2:
    PrintUsageAndExit()
if len(sys.argv) >= 3:
    ROWS_COUNT = int(sys.argv[1])
    COLS_COUNT = int(sys.argv[2])
if (len(sys.argv) == 4):
    K = int(sys.argv[3])
if (len(sys.argv) > 4):
    PrintUsageAndExit()

# Starting the game
#opponent = alpha_beta_opponent.AlphaBetaOpponent(K)
#opponent = NeuralNetworkOpponent(ROWS_COUNT, COLS_COUNT, "data/final_network")
#opponent = NeuralNetworkOpponent(ROWS_COUNT, COLS_COUNT, "data/optimal_3_by_3_network")
opponent = MonteCarloOpponent(ROWS_COUNT, COLS_COUNT, K, 1000)
game = tic_tac_game.Game(ROWS_COUNT, COLS_COUNT, K, opponent)
game.start()
