import tic_tac_game
import numpy
import utils

WIN_SCORE = 10000
DEPTH = 6
BREADTH = 12

def AdjacentCount(board, row, col):
    count = 0
    directions = [[-1,-1], [-1, 0], [-1, 1], [0, -1], [0,1], [1, -1], [1, 0], [1, 1]]
    for direction in directions:
        r = row + direction[0]
        c = col + direction[1]
        if (r >= 0 and r < len(board) and c >= 0 and c < len(board[0])
            and board[r][c] != utils.EMPTY):
            count += 1
    return count
        

class AlphaBetaOpponent:
    def __init__(self, k):
        self.k = k
        self.visited_positions = {}

    def evaluate(self, board):
        return tic_tac_game.GameEnded(board, self.k) * WIN_SCORE

    def candidate_moves(self, board, turn):
        moves = []
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] == utils.EMPTY:
                    adjacent_count = AdjacentCount(board, row, col)
                    if adjacent_count:
                        board[row][col] = turn
                        consecutive_count = utils.ConsecutiveCount(board, row, col)
                        board[row][col] = -turn
                        block_count = utils.ConsecutiveCount(board, row, col)
                        board[row][col] = utils.EMPTY
                        score = WIN_SCORE if consecutive_count == self.k else \
                            block_count ** 3 + consecutive_count ** 2 + adjacent_count
                        moves.append((score, row, col))
        moves.sort(reverse=True)            
        return [(row,col) for (_, row, col) in moves][:BREADTH]

    def alpha_beta(self, board, alpha, beta, depth, turn, last_row, last_col):
        consecutive_count = utils.ConsecutiveCount(board, last_row, last_col)
        # Checking whether the game has ended
        if consecutive_count == self.k:
            return -WIN_SCORE
        if self.ply_count + depth == len(board) * len(board[0]):
            return 0
        
        # Stop search here, returning heuristic position evaluation
        if depth == DEPTH:
            return -consecutive_count
        
        for row, col in self.candidate_moves(board, turn):
            board[row][col] = turn
            alpha = max(alpha, -self.alpha_beta(board, -beta, -alpha, depth+1, -turn, row, col))
            board[row][col] = utils.EMPTY
            if alpha >= beta:
                return beta
        return alpha

    def find_move(self, board, window):
        self.visited_positions.clear()
        self.ply_count = utils.PlyCount(board)
        
        best_score = -WIN_SCORE
        best_row, best_col = -1, -1
        candidate_moves = self.candidate_moves(board, utils.OPPONENT_TURN)
        moves_checked = 0
        for row, col in candidate_moves:
            window.title("Please wait, {}/{} checked".format(moves_checked, len(candidate_moves)))
            
            board[row][col] = utils.OPPONENT_TURN
            new_score = -self.alpha_beta(board, -WIN_SCORE, WIN_SCORE,
                1, utils.MY_TURN, row, col)
            board[row][col] = utils.EMPTY
            
            print("Score for ", row, col, "is", new_score)
            if new_score > best_score or best_row == -1:
                print("New best score: ", new_score)
                best_score = new_score
                best_row = row
                best_col = col
            if new_score == WIN_SCORE:
                return row, col    

            moves_checked += 1    
        return best_row, best_col
