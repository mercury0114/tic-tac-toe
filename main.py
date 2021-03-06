import sys
from tic_tac_game import Game
from monte_carlo import MonteCarloOpponent
from position_evaluators import ConstantEvaluator
from position_evaluators import OptimisedRandomGameEvaluator 
from position_evaluators import RandomGameEvaluator

def PrintUsageAndExit():
    print("python3 main.py [ROWS_COUNT] [COLS_COUNT] [K]")
    print("or to use default k=5:")
    print("python3 main.py [ROWS_COUNT] [COLS_COUNT]")
    sys.exit()

ROWS_COUNT = 15
COLS_COUNT = 15
K = 5

# Parsing command line arguments
l = len(sys.argv)
if l == 2 or l == 3 or l > 4:
    PrintUsageAndExit()
if l == 4:
    ROWS_COUNT = int(sys.argv[1])
    COLS_COUNT = int(sys.argv[2])
    K = int(sys.argv[3])

# Starting the game
SIMULATION_COUNT = 10000
opponent = MonteCarloOpponent(ROWS_COUNT, COLS_COUNT, K, \
                              OptimisedRandomGameEvaluator(K, 50), SIMULATION_COUNT)
#opponent = MonteCarloOpponent(ROWS_COUNT, COLS_COUNT, K, \
#                             ConstantEvaluator(), SIMULATION_COUNT)
#opponent = MonteCarloOpponent(ROWS_COUNT, COLS_COUNT, K, \
#                              RandomGameEvaluator(K, 50), SIMULATION_COUNT)
game = Game(ROWS_COUNT, COLS_COUNT, K, opponent)
game.start()
