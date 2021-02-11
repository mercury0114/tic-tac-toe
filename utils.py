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