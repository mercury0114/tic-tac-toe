import tic_tac_game
import numpy

WIN_SCORE = 10000

def InRange(board, row, col):
    return row >= 0 and row < len(board) and col >= 0 and col < len(board[0])

def AdjacentCount(board, row, col):
    count = 0
    directions = [[-1,-1], [-1, 0], [-1, 1], [0, -1], [0,1], [1, -1], [1, 0], [1, 1]]
    for direction in directions:
        r = row + direction[0]
        c = col + direction[1]
        if (r >= 0 and r < len(board) and c >= 0 and c < len(board[0])
            and board[r][c] != tic_tac_game.EMPTY):
            count += 1
    return count

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
        

class Opponent:
    def __init__(self, k):
        self.k = k

    def evaluate(self, board):
        return tic_tac_game.GameEnded(board, self.k) * WIN_SCORE

    def candidate_moves(self, board, turn):
        moves = []
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] == tic_tac_game.EMPTY:
                    adjacent_count = AdjacentCount(board, row, col)
                    if adjacent_count:
                        board[row][col] = turn
                        consecutive_count = ConsecutiveCount(board, row, col)
                        board[row][col] = -turn
                        block_count = ConsecutiveCount(board, row, col)
                        board[row][col] = tic_tac_game.EMPTY
                        score = WIN_SCORE if consecutive_count == self.k else \
                            consecutive_count + block_count * block_count + adjacent_count
                        moves.append((score, row, col))
        moves.sort(reverse=True)            
        return [(row,col) for (_, row, col) in moves][0:min(len(moves), 20)]

    def alpha_beta(self, board, alpha, beta, depth, turn):
        if tic_tac_game.GameEnded(board, self.k) or depth == 0:
            return self.evaluate(board) * turn
        if tic_tac_game.FullBoard(board):
            return 0
        for row, col in self.candidate_moves(board, turn):
            board[row][col] = turn
            alpha = max(alpha, -self.alpha_beta(board, -beta, -alpha, depth-1, -turn))
            board[row][col] = tic_tac_game.EMPTY
            if alpha >= beta:
                return beta
        return alpha

    def make_move(self, board, window):
        best_score = -WIN_SCORE
        best_row, best_col = -1, -1
        candidate_moves = self.candidate_moves(board, tic_tac_game.OPPONENT_TURN)
        count = 0
        for row, col in candidate_moves:
            window.title("Please wait, {}/{} complete".format(count, len(candidate_moves)))
            count += 1
            print("Dealing with ", row, col)
            if (best_row == -1):
                best_row, best_col = row, col
            board[row][col] = tic_tac_game.OPPONENT_TURN
            new_score = -self.alpha_beta(board, -WIN_SCORE, WIN_SCORE,
                3, tic_tac_game.MY_TURN)
            board[row][col] = tic_tac_game.EMPTY
            if (new_score == WIN_SCORE):
                return row, col
            if new_score > best_score:
                print("New best score: ", new_score)
                best_score = new_score
                best_row = row
                best_col = col
        print()
        return best_row, best_col
