import tic_tac_game
import opponent
import sys

def PrintUsageAndExit():
    print("python3 main.py [ROWS_COUNT] [COLS_COUNT] [K]")
    print("or to use default k=5:")
    print("python3 main.py [ROWS_COUNT] [COLS_COUNT]")
    sys.exit()

ROWS_COUNT = 15
COLS_COUNT = 15
K = 5
if len(sys.argv) == 2:
    PrintUsageAndExit()
if len(sys.argv) >= 3:
    ROWS_COUNT = int(sys.argv[1])
    COLS_COUNT = int(sys.argv[2])
if (len(sys.argv) == 4):
    K = int(sys.argv[3])
if (len(sys.argv) > 4):
    PrintUsageAndExit()

opponent = opponent.Opponent(K)
game = tic_tac_game.Game(ROWS_COUNT, COLS_COUNT, K, opponent)
game.start()
