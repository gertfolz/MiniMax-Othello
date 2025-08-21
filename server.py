import os
import time
import importlib
import argparse
import xml.etree.ElementTree as ET
import xml.dom.minidom

import advsearch.othello.board as board
import advsearch.timer as timer


class Server(object):
    """
    Othello server, implements a simple file-based playing protocol

    """

    def __init__(self, p1_dir, p2_dir, delay, history, output, pace=0):
        """
        Initializes the Othello game server
        :param p1_dir: directory where the 'agent.py' of the 1st player is located
        :param p2_dir: directory where the 'agent.py' of the 2nd player is located
        :param delay: time limit to make a move
        :param history: file that will contain the match history (plain text)
        :param output: file to save game details (includes history)
        :param pace: time to wait to display a move, if a player returns before timeout
        """
        # normalizes paths to avoid errors with trailing slashes
        p1_dir = os.path.normpath(p1_dir)
        p2_dir = os.path.normpath(p2_dir)

        self.basedir = os.path.abspath('.')

        self.player_dirs = [p1_dir, p2_dir]

        self.player_colors = [board.Board.BLACK, board.Board.WHITE]
        self.color_names = ['black', 'white']
        self.board = board.Board()

        self.history = []  # a list of performed moves (tuple: ((x,y), color)
        self.history_file = open(history, 'w')
        self.output_file = output

        self.delay = delay
        self.pace = pace

        self.result = None

        # start and finish times of match
        self.start = None
        self.finish = None

        # imports 'agent.py' from both players
        self.player_modules = [
            importlib.import_module(f"{p1_dir}.agent"),
            importlib.import_module(f"{p2_dir}.agent"),
        ]

    def __del__(self):
        self.history_file.close()

    def run(self):
        self.start = time.localtime()
        player = 0

        illegal_count = [0, 0]  # counts the number of illegal move attempts

        print(f'---- Current match: {self.player_dirs[0]} (B) x {self.player_dirs[1]} (W) ----')
        print('Initial board:')
        print(self.board.decorated_str())

        while True:  # runs until endgame

            # checks whether players have available moves
            no_moves_current = len(self.board.legal_moves(self.player_colors[player])) == 0
            no_moves_opponent = len(self.board.legal_moves(self.board.opponent(self.player_colors[player]))) == 0

            # calculates scores
            p1_score = sum([1 for char in str(self.board) if char == self.board.BLACK])
            p2_score = sum([1 for char in str(self.board) if char == self.board.WHITE])

            print(f'---- Current match: {self.player_dirs[0]} (B) x {self.player_dirs[1]} (W) ----')

            # disqualify player if he attempts illegal moves 5 times in a row
            if illegal_count[player] >= 5:
                print(f'Player {player+1} ({self.player_dirs[player]}) DISQUALIFIED! Too many illegal move attempts.')
                print('End of game reached!')
                print('Player 1 (B): %d' % p1_score)
                print('Player 2 (W): %d' % p2_score)

                self.result = 1 - player
                self.finish = time.localtime()
                return self.result

            # checks whether both players don't have available moves (end of game)
            if no_moves_current and no_moves_opponent:

                print('End of game reached! Scores:')
                print(f'Player 1 (B - {self.player_dirs[0]}): {p1_score}')
                print(f'Player 2 (W - {self.player_dirs[1]}): {p2_score}')

                if p1_score > p2_score:
                    print(f'Player 1 (B - {self.player_dirs[0]} wins!')
                elif p2_score > p1_score:
                    print(f'Player 2 (W - {self.player_dirs[1]}) wins!')
                else:
                    print('Draw!')

                self.result = 0 if p1_score > p2_score else 1 if p2_score > p1_score else 2
                self.finish = time.localtime()
                return self.result

            # if current player has no moves, toggle player and continue
            if no_moves_current:
                print(f'Player {player+1} ({self.player_dirs[player]}) has no legal moves and will not play this turn.')
                illegal_count[player] = 0
                player = 1 - player
                time.sleep(self.pace)
                continue

            # creates a copy of the board, so that player changes won't affect mine
            board_copy = board.from_string(self.board.__str__())

            # calls current player's make_move function with the specified timeout
            start = time.time()
            function_call = timer.FunctionTimer(self.player_modules[player].make_move, (board_copy, self.player_colors[player]))
            move = function_call.run(self.delay)
            elapsed = time.time() - start

            if move is None:  # detects timeout
                print('Player %d has not made a move and lost its turn. Illegal moves count incremented' % (player + 1))
                illegal_count[player] += 1
                player = 1 - player
                continue

            move_x, move_y = move

            # checks for move validity
            if not isinstance(move_x, int):
                print(f'Warning! move_x is {type(move_x)} but should be integer!')
                move_x = -1
            if not isinstance(move_y, int):
                print(f'Warning! move_y is {type(move_y)} but should be integer!')
                move_y = -1

            # saves move in history
            self.history_file.write('%d,%d,%s\n' % (move_x, move_y, self.player_colors[player]))
            self.history.append(((move_x, move_y), self.player_colors[player]))

            if self.board.process_move((move_x, move_y), self.player_colors[player]):
                illegal_count[player] = 0
                print('Player %d move %d,%d accepted.' % (player + 1, move_x, move_y))

            else:
                illegal_count[player] += 1
                print('Player %d move %d,%d ILLEGAL!' % (player + 1,move_x, move_y))

            # waits the remaining time, if needed
            if self.pace - elapsed > 0:
                time.sleep(self.pace - elapsed)

            print('Current board:')
            print(self.board.decorated_str(highlight=(move_y, move_x)))

            # toggle player for next move
            player = 1 - player

    def write_output(self):
        """
        Writes a xml file with detailed match data
        :return:
        """
        os.chdir(self.basedir)

        root = ET.Element('othello-match')

        colors = [self.board.BLACK, self.board.WHITE, 'None']
        self.player_dirs.append('None')  # trick for writing a draw match

        timing = ET.SubElement(root, 'timing')
        timing.set('start', time.asctime(self.start))
        timing.set('finish', time.asctime(self.finish))

        scores = [self.board.piece_count['B'], self.board.piece_count['W']]

        for idx, p in enumerate(self.player_dirs[:2]):
            elem = ET.SubElement(root, 'player%d' % (idx + 1))
            elem.set('directory', p)
            elem.set('color', colors[idx])

            result = 'win' if scores[idx] > scores[idx - 1] else 'loss' if scores[idx] < scores[idx - 1] else 'draw'
            elem.set('result', result)
            elem.set('score', str(scores[idx]))

        moves = ET.SubElement(root, 'moves')

        for coords, color in self.history:
            move = ET.SubElement(moves, 'move')
            move.set('coord', '%d,%d' % coords)
            move.set('color', color)

        # preety xml thanks to: https://stackoverflow.com/a/1206856/1251716
        ugly_xml = ET.tostring(root).decode('utf-8')
        dom = xml.dom.minidom.parseString(ugly_xml)  # or xml.dom.minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml()
        f = open(self.output_file, 'w')
        f.write(pretty_xml)
        f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Othello server.')
    parser.add_argument('players', metavar='player', type=str, nargs=2,
                        help='Path to player directory')
    parser.add_argument('-d', '--delay', type=float, metavar='delay',
                        default=5.0,
                        help='Time allocated for players to make a move.')

    parser.add_argument('-p', '--pace', type=float,
                        default=0,
                        help='Pace of the match: time to wait to display a move '
                             '(if a player returns a move before the delay/timeout).')

    parser.add_argument('-l', '--log-history', type=str, dest='history',
                        default='history.txt', metavar='log-history',
                        help='File to save game log (history).')

    parser.add_argument('-o', '--output-file', type=str, dest='output',
                        default='results.xml', metavar='output-file',
                        help='File to save game details (includes history)')

    args = parser.parse_args()
    p1, p2 = args.players

    s = Server(p1, p2, args.delay, args.history, args.output, args.pace)
    s.run()
    s.write_output()
