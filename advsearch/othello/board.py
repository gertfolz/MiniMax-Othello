def from_file(path_to_file):
    """
    Generates a board from the string representation
    contained in the file
    :param path_to_file:
    :return: Board object
    """
    return from_string(open(path_to_file).read())


def from_string(string):
    """
    Generates a board from the string representation
    :param string:
    :return:
    """
    b = Board()
    # resets piece_count and set it during board construction
    b.piece_count = {b.BLACK: 0, b.WHITE: 0, b.EMPTY: 0}
    for lineno, line in enumerate(string.split('\n')):
        line.strip()  # cuts the \n

        for colno, col in enumerate(line):
            b.tiles[lineno][colno] = col
            b.piece_count[col] += 1

    return b


class Board(object):
    """
    Board implementation strongly inspired by: http://dhconnelly.com/paip-python/docs/paip/othello.html
    The internal representation is an 8x8 matrix of characters. Each character represents a tile
    and can be either 'B' for a black piece, 'W' for a white piece or '.' for an empty place, where
    a piece can be played. For example, the initial board is the following:
    ........
    ........
    ........
    ...WB...
    ...BW...
    ........
    ........
    ........

    Coordinate system is such that x grows from left to right and y from top to bottom:
      01234567 --> x axis
    0 ........
    1 ........
    2 ........
    3 ...WB...
    4 ...BW...
    5 ........
    6 ........
    7 ........
    |
    |
    v
    y axis
    """

    BLACK = 'B'
    WHITE = 'W'
    EMPTY = '.'

    # direction of neighbor tiles (add to current tile coordinates to obtain neighbor)
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)

    # list with all directions
    DIRECTIONS = [UP, DOWN, LEFT, RIGHT, UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT]

    def __init__(self):
        """
        Initializes the 8x8 board with all tiles empty, except the center
        that are initialized according to othello's initial board
        :return:
        """
        self.tiles = [[self.EMPTY] * 8 for i in range(8)]

        self.tiles[3][3], self.tiles[3][4] = self.WHITE, self.BLACK
        self.tiles[4][3], self.tiles[4][4] = self.BLACK, self.WHITE

        # cache legal moves in attempt to reduce function calls
        self._legal_moves = {self.BLACK: None, self.WHITE: None}

        self.piece_count = {self.BLACK: 2, self.WHITE: 2, self.EMPTY: 60}

        # stores the flipped tiles at each move
        self.flipped = set()

    def is_within_bounds(self, move):
        """
        Returns whether the move refers to a valid board position
        :param move: (int, int)
        :return: bool
        """
        return 0 <= move[0] < 8 and 0 <= move[1] < 8

    def is_legal(self, move, color):
        """
        Returns whether the move is legal for the given color
        :param move: (int,int) tile position to place the disk
        :param color: color of the player making the move
        :return: bool
        """
        # move is queried row,col but stored col,row in legal_moves
        return (move[1], move[0]) in self.legal_moves(color)

    def is_terminal_state(self):
        """
        Returns whether the current state is terminal (game finished) or not
        :return:
        """
        no_moves_black = len(self.legal_moves(self.BLACK)) == 0
        no_moves_white = len(self.legal_moves(self.WHITE)) == 0

        return no_moves_black and no_moves_white

    def find_bracket(self, move, color, direction):
        """
        Traverses the board in given direction trying to
        find a tile of the given color that surrounds opponent tiles, returns
        :param move: (int, int)
        :param color: color of player making the move
        :param direction: one of eight directions of tile neighborhood
        :return: (int,int)
        """
        # performing inline boundary check to avoid calls for is_within_bounds
        # this saves some time
        dx, dy = direction
        tx, ty = move
        tx += dx
        ty += dy

        opp = self.BLACK if color == self.WHITE else self.WHITE  # inline opponent calc.

        if not (0 <= tx <= 7 and 0 <= ty <= 7) or self.tiles[tx][ty] != opp:
            return False

        while self.tiles[tx][ty] == opp:  # putting is_within_bounds here yields more calls
            tx += dx
            ty += dy
            if not (0 <= tx <= 7 and 0 <= ty <= 7):  # self.is_within_bounds((tx, ty)):
                return False

        if self.tiles[tx][ty] == self.EMPTY:
            return False
        return tx, ty

    def find_where_to_play_from_owned(self, owned, color, direction):
        """
        Traverses the board in given direction trying to
        find an empty tile that surrounds opponent tiles, returns it.
        This is the dual of find_bracket, which goes from empty to
        the piece of the desired color
        :param owned: (int, int), col, row coordination of owned tile
        :param color: color of owned tile
        :param direction: one of eight directions of tile neighborhood
        :return: (int,int) or False if not found
        """
        # performing inline boundary check to avoid calls for is_within_bounds
        # this saves some time
        dx, dy = direction
        tx, ty = owned
        tx += dx
        ty += dy
        opp = self.BLACK if color == self.WHITE else self.WHITE  # inline opponent calc.

        if not (0 <= tx <= 7 and 0 <= ty <= 7) or self.tiles[tx][ty] != opp:  # color:
            return False

        while self.tiles[tx][ty] == opp:
            tx += dx
            ty += dy
            if not (0 <= tx <= 7 and 0 <= ty <= 7):
                return False

        if self.tiles[tx][ty] != self.EMPTY:
            return False
        return tx, ty

    def process_move(self, position, color):
        """
        Executes the placement of a tile of a given color
        in a given position
        :param position:
        :param color:
        :return: bool
        """

        # as the board is represented row-column, swaps coords to col-row
        position = position[1], position[0]

        if color not in [self.WHITE, self.BLACK]:
            raise ValueError("Move must be made by BLACK or WHITE player")

        if self.is_legal(position, color):
            # places the piece and update piece counts
            px, py = position
            self.tiles[px][py] = color
            self.piece_count[color] += 1
            self.piece_count[self.EMPTY] -= 1

            for direc in self.DIRECTIONS:
                self.flip_tiles(position, color, direc)

            # resets legal moves
            self._legal_moves[self.BLACK], self._legal_moves[self.WHITE] = None, None
            return True

        return False  # guards against illegal moves

    def flip_tiles(self, origin, color, direction):
        """
        Traverses the board in the given direction,
        transforming the color of appropriate tiles
        :param origin: where the traversal will begin
        :param color:
        :param direction:
        :return:
        """
        destination = self.find_bracket(origin, color, direction)  # move, player, board, direction)
        if not destination:
            return

        ox, oy = origin
        dx, dy = direction

        nx, ny = ox + dx, oy + dy  # n stands for 'next'

        opp = self.opponent(color)
        self.flipped = set()
        while (nx, ny) != destination:
            # flips the tile and updates piece counts
            self.flipped.add((nx, ny))
            self.tiles[nx][ny] = color
            self.piece_count[color] += 1
            self.piece_count[opp] -= 1
            nx, ny = nx + dx, ny + dy

    def legal_moves(self, color):
        """
        Returns a list of legal moves for the given color
        :param color:
        :return:
        """
        if self._legal_moves[color] is None:
            # construct the list of legal moves only once
            self._legal_moves[color] = list()

            if self.piece_count[color] > self.piece_count[self.EMPTY]:
                self.find_legal_moves_dense(color)
            else:
                self.find_legal_moves_sparse(color)

        return self._legal_moves[color]

    def find_legal_moves_dense(self, color):
        """
        Finds the legal moves for a given color in a dense board.
        A dense board has less empty tiles than pieces of the given color.
        :param color:
        """
        # test if every empty tile on the board is a legal move
        tiles = [(x, y) for x in range(8) for y in range(8) if self.tiles[x][y] == self.EMPTY]

        for x, y in tiles:
            if self.tiles[x][y] == self.EMPTY:  # and any(map(hasbracket, self.DIRECTIONS)):
                # performs the 'inline' any:
                for direc in self.DIRECTIONS:
                    if self.find_bracket((x, y), color, direc):
                        # flips x,y because of the way tiles are stored and the x,y coords in real world
                        self._legal_moves[color].append((y, x))
                        break

    def find_legal_moves_sparse(self, color):
        """
        Finds the legal moves for a given color in a sparse board.
        A sparse board has more empty tiles than pieces of the given color
        :param color:
        :return:
        """
        # test if every empty tile on the board is a legal move
        tiles = [(x, y) for x in range(8) for y in range(8) if self.tiles[x][y] == color]

        for x, y in tiles:
            if self.tiles[x][y] == color:
                for direc in self.DIRECTIONS:
                    move = self.find_where_to_play_from_owned((x, y), color, direc)
                    if move:
                        # flips x,y because of the way tiles are stored and the x,y coords in real world
                        self._legal_moves[color].append((move[1], move[0]))

    def has_legal_move(self, color):
        """
        Returns whether the given color has any legal move
        :param color:
        :return:bool
        """
        # test if every empty tile on the board is a legal move
        tiles = [(x, y) for x in range(8) for y in range(8) if self.tiles[x][y] == self.EMPTY]

        for x, y in tiles:
            # self._legal_moves[color] = [(y, x) for x, y in tiles if self.is_legal((x, y), color)]

            hasbracket = lambda direction: self.find_bracket((x, y), color, direction)

            if self.tiles[x][y] == self.EMPTY and any(map(hasbracket, self.DIRECTIONS)):
                return True
        return False

    def opponent(self, color):
        """
        Returns the opponent of the received color
        :param color:
        :return:
        """
        if color == self.EMPTY:
            raise ValueError('Empty has no opponent.')

        if color == self.WHITE:
            return self.BLACK
        else:
            return self.WHITE

    def print_board(self):
        """
        Prints the string representation of the board
        :return:
        """

        print(self.decorated_str())

    def decorated_str(self, pretty=False, highlight=None):
        """
        Returns the string representation of the board
        decorated with coordinates for board positions
        :param highlight: tuple with position (row, col) to highlight
        :return: str
        TODO look at https://pypi.org/project/colorama/ and/or https://docs.python.org/3/howto/curses.html
        """
        if pretty:
            string = 'x   0   1   2   3   4   5   6   7 \n'
            for i, row in enumerate(self.tiles):
                string += '  -' + '----' * 8 + '\n'
                string += '%d | %s |\n' % (i, ' | '.join(row))
            string += '  -' + '----' * 8 + '\n'
        else:
            string = 'x 0 1 2 3 4 5 6 7\n'
            for i, row in enumerate(self.tiles):
                if highlight is None:
                    string += f'{i} {" ".join(row)} \n'
                else:
                    string += f'{i}'
                    for j, piece in enumerate(row):
                        if (i, j) == highlight or (i, j) in self.flipped:
                            string += f'*{piece}'
                            if j == 7:
                                string += '*'  # adds sign to the right of boundary piece
                        elif (i, j-1) == highlight or (i, j-1) in self.flipped:  # shows sign at the piece to the right of the highlighted one
                            string += f'*{piece}'
                        else:
                            string += f' {piece}'
                    string += '\n'

        return string

    def __str__(self):
        """
        Returns the string representation of the board
        :return: str
        """
        string = ''
        for i, row in enumerate(self.tiles):
            string += '%s\n' % ''.join(row)

        return string
