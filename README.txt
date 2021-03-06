# To start a default 15 x 15, 5 in a row game:
python3 main.py

# To start a game with custom parameters, e.g: ROWS_COUNT = 3, COLS_COUNT = 3, K = 3
python3 main.py 3 3 3

# If you modify the random_game_evaluator.c code and want to use the updates, recompile the code:
./recompile_c_code.sh

# For windows, to create a directory containing a portable program with .exe file, type:
pyinstaller -w main.py

# To create just a single exe file, type
pyinstaller --onefile -w main.py
