import itertools

MY_TURN = -1
OPPONENT_TURN = 1
EMPTY = 0

def PlyCount(board):
    count = 0
    for row in range(len(board)):
        for col in range(len(board[0])):
            count += board[row][col] * board[row][col]
    return count

def InRange(board, row, col):
    return row >= 0 and row < len(board) and col >= 0 and col < len(board[0])

def ConsecutiveCount(board, row, col):
    directions = [[0, 1], [1, 1], [1, 0], [1, -1]]
    max_count = 1
    for direction in directions:
        forward_count = 0
        next_row = row + direction[0]
        next_col = col + direction[1]
        while InRange(board, next_row, next_col) and \
                board[next_row][next_col] == board[row][col]:
            forward_count += 1
            next_row += direction[0]
            next_col += direction[1]
        backward_count = 0
        next_row = row - direction[0]
        next_col = col - direction[1]
        while InRange(board, next_row, next_col) and \
                board[next_row][next_col] == board[row][col]:
            backward_count += 1
            next_row -= direction[0]
            next_col -= direction[1]
        max_count = max(max_count, 1 + forward_count + backward_count)
    return max_count

def AvailableMoves(board):
    moves = []
    for row, col in itertools.product(range(len(board)), range(len(board[0]))):
        if board[row][col] == EMPTY:
            moves.append((row, col))
    return moves

# returns -1 if I won, 0 if game continues, 1 if opponent won
def GameWon(board, last_row, last_col, k):
    if last_row == -1:
        return 0
    return (ConsecutiveCount(board, last_row, last_col) == k) * board[last_row][last_col]
