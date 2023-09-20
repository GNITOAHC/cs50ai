"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count = [0, 0, 0]  # X, O, EMPTY
    for row in board:
        for cell in row:
            if cell == X:
                count[0] += 1
            elif cell == O:
                count[1] += 1
            else:
                count[2] += 1
    if count[0] > count[1]:
        return O
    else: return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    row = list(action)[0]
    cell = list(action)[1]
    if board[row][cell] != EMPTY:
        raise Exception("Invalid action")
    else:
        new_board = deepcopy(board)
        new_board[row][cell] = player(board)
        return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for player in (X, O):
        # check rows
        for row in board:
            if row.count(player) == 3:
                return player
        # check columns
        for i in range(3):
            if [row[i] for row in board].count(player) == 3:
                return player
        # check diagonals
        if [board[i][i] for i in range(3)].count(player) == 3:
            return player
        if [board[i][2-i] for i in range(3)].count(player) == 3:
            return player
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Someone has won
    if winner(board) != None:
        return True

    # Board is full
    for row in board:
        if EMPTY in row:
            return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Have Winner
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1

    # Tie
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    # Return type: tuple[val, action]
    def max_value(board) -> tuple[int, tuple[int, int]]:
        optimal_action = (0, 0) # Default action

        if terminal(board):
            return utility(board), optimal_action
        else:
            value = -5
            for action in actions(board):
                min_val = min_value(result(board, action))[0] # Get min value of all possible actions
                if min_val > value:
                    value = min_val
                    optimal_action = action
            return value, optimal_action

    # Return type: tuple[val, action]
    def min_value(board) -> tuple[int, tuple[int, int]]:
        optimal_action = (0, 0) # Default action

        if terminal(board):
            return utility(board), optimal_action
        else:
            value = 5
            for action in actions(board):
                max_val = max_value(result(board, action))[0] # Get max value of all possible actions
                if max_val < value:
                    value = max_val
                    optimal_action = action
            return value, optimal_action

    if terminal(board):
        return None

    if player(board) == X:
        return max_value(board)[1] # Return action
    else:
        return min_value(board)[1]
