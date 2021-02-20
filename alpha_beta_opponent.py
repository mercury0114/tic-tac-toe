import tic_tac_game
import numpy
from utils import AdjacentCount, PlyCount, ConsecutiveCount, EMPTY, MY_TURN, OPPONENT_TURN

WIN_SCORE = 10000
DEPTH = 7
BREADTH = 11        

class AlphaBetaOpponent:
    def __init__(self, k):
        self.k = k

    def evaluate(self, board):
        return tic_tac_game.GameEnded(board, self.k) * WIN_SCORE

    def candidate_moves(self, board, turn):
        moves = []
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] == EMPTY:
                    adjacent_count = AdjacentCount(board, row, col)
                    if adjacent_count:
                        board[row][col] = turn
                        consecutive_count = ConsecutiveCount(board, row, col)
                        board[row][col] = -turn
                        block_count = ConsecutiveCount(board, row, col)
                        board[row][col] = EMPTY
                        score = WIN_SCORE if consecutive_count == self.k else \
                            block_count ** 3 + consecutive_count ** 2 + adjacent_count
                        moves.append((score, row, col))
        moves.sort(reverse=True)            
        return [(row,col) for (_, row, col) in moves][:BREADTH]

    def alpha_beta(self, board, alpha, beta, depth, turn, last_row, last_col):
        consecutive_count = ConsecutiveCount(board, last_row, last_col)
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
            board[row][col] = EMPTY
            if alpha >= beta:
                return beta
        return alpha

    def find_move(self, board, window):
        self.ply_count = PlyCount(board)
        
        best_score = -WIN_SCORE
        best_row, best_col = -1, -1
        candidate_moves = self.candidate_moves(board, OPPONENT_TURN)
        moves_checked = 0
        for row, col in candidate_moves:
            window.title("Please wait, {}/{} checked".format(moves_checked, len(candidate_moves)))
            
            board[row][col] = OPPONENT_TURN
            new_score = -self.alpha_beta(board, -WIN_SCORE, WIN_SCORE,
                1, MY_TURN, row, col)
            board[row][col] = EMPTY
            
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
