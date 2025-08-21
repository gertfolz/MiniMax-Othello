import random
from ..othello import board


def make_move(the_board, color):
    """
    Returns a random move from the list of possible ones
    :param the_board: a board.Board object
    :param color: a character indicating the color to make the move ('B' or 'W')
    :return: (int, int)
    """
    legal_moves = the_board.legal_moves(color)
    return random.choice(legal_moves) if len(legal_moves) > 0 else (-1, -1)


if __name__ == '__main__':
    b = board.Board()
    move = make_move(b, 'B')
    print(f'A random move for black in the initial state: {move}')
    print('Resulting state:')
    b.process_move(move, 'B')
    b.print_board()


