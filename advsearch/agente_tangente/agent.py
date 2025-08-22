from cmath import inf
import random
from ..othello import board
import sys
import copy

MAX_DEPTH = 2 # MiniMax depth

def make_move(the_board, color):
    """
    Returns an Othello move
    :param the_board: a board.Board object with the current game state
    :param color: a character indicating the color to make the move ('B' or 'W')
    :return: (int, int) tuple with x, y indexes of the move
    """

    bestValue = -inf
    alpha = -inf
    beta = inf
    bestMove = ()

    legal_moves = the_board.legal_moves(color)

    if len(legal_moves) == 0:
        return (-1, -1)

    for move in legal_moves:
        b = copy.deepcopy(the_board)
        b.process_move(move, color)

        value = miniMax(b, alpha, beta, 0, False, color)
        if(bestValue < value):
            bestValue = value
            bestMove = move

    return bestMove

if __name__ == '__main__':
    b = board.Board()
    move = make_move(b, 'W')
    print(f'A random move for black in the initial state: {move}')
    print('Resulting state:')
    b.process_move(move, 'W')
    b.print_board()


def miniMax(the_board, alpha, beta, depth, isMax, color):

    if color == 'B':
        opp = 'W'
    else:
        opp = 'B'

    if(isMax):
        legal_moves = the_board.legal_moves(color)
        if(depth == MAX_DEPTH or (len(legal_moves) == 0)):
            return evaluate_node(the_board, color)

        for move in legal_moves:
            b = copy.deepcopy(the_board)
            b.process_move(move, color)
            value = miniMax(b, alpha, beta, depth + 1, False, color)
            alpha = max(alpha, value)

            if(beta <= alpha): # Beta pruning 
                break

        return alpha

    else:
        legal_moves = the_board.legal_moves(opp)
        
        if(depth == MAX_DEPTH or (len(legal_moves) == 0)):
            return evaluate_node(the_board, color)

        for move in legal_moves:
            b = copy.deepcopy(the_board)
            b.process_move(move, opp)
            value = miniMax(b, alpha, beta, depth + 1, True, color)
            beta = min(beta, value)

            if(beta <= alpha): # Alpha pruning
                break

        return beta
        
def evaluate_node(the_board, color):

    cornersState = [the_board.tiles[0][0], the_board.tiles[7][0], the_board.tiles[0][7], the_board.tiles[7][7]] # Encontra os valores dos cantos na odem NW, NE, SW, SE

    A_score = 5
    B_score = 3
    C_score = 10
    X_score = 15
    corner_score = 20

    A_tiles = [[the_board.tiles[2][0], the_board.tiles[0][2]], [the_board.tiles[5][0], the_board.tiles[7][2]], [the_board.tiles[2][7], the_board.tiles[0][5]], [the_board.tiles[5][7], the_board.tiles[7][5]]]
    B_tiles = [[the_board.tiles[3][0], the_board.tiles[0][3]], [the_board.tiles[4][0], the_board.tiles[7][3]], [the_board.tiles[3][7], the_board.tiles[0][4]], [the_board.tiles[4][7], the_board.tiles[7][4]]]
    C_tiles = [[the_board.tiles[1][0], the_board.tiles[0][1]], [the_board.tiles[6][0], the_board.tiles[7][1]], [the_board.tiles[1][7], the_board.tiles[0][6]], [the_board.tiles[6][7], the_board.tiles[7][6]]]
    X_tiles = [[the_board.tiles[1][1]], [the_board.tiles[6][1]], [the_board.tiles[1][6]], [the_board.tiles[6][6]]]

    if color == 'B':
        opp = 'W'
    else:
        opp = 'B'


    if (len(the_board.legal_moves(color)) + len(the_board.legal_moves(opp)) == 0 and the_board.piece_count.get(color) > the_board.piece_count.get(opp)):
        return inf
    if (the_board.piece_count.get(opp) == 0): 
        return inf
    if (the_board.piece_count.get(color) == 0): 
        return -inf

    score = len(the_board.legal_moves(color)) - len(the_board.legal_moves(opp)) 
    score += (cornersState.count(color) - cornersState.count(opp)) * corner_score 

    specialTileScore = [0, 0, 0, 0]

    for area in range(0, 4):
        specialTileScore[area] = -(A_tiles[area].count(color) * A_score + B_tiles[area].count(color) * B_score + C_tiles[area].count(color) * C_score + X_tiles[area].count(color) * X_score)
        if cornersState[area] == color:
            specialTileScore[area] = -specialTileScore[area] / 3        

    score += sum(specialTileScore)

    return score
                                    
    
def isCorner(tuple):
    if (((tuple[0] == 0) and (tuple[1]  in [0, 7])) or ((tuple[0] == 7) and (tuple[1]  in [0, 7]))):    
        return True
    else:
        return False

