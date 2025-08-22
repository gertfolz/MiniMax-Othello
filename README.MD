# Othello Kit
A kit for running Othello matches and implementing the alpha-beta pruning algorithm.

## Requirements
The server was tested on a GNU/Linux machine with the python 3.7 interpreter.

Other versions of the python interpreter or operating system may work, but have not been tested.

## Instructions

To start an Othello match, type in the terminal:

`python server.py [-h] [-d delay] [-p pace]  [-o output-file] [-l log-history] advsearch.player1 advsearch.player2`

Where 'player(1 or 2)' are the directories within `advsearch` where the players' modules are implemented (inside the agent file).

The arguments in square brackets are optional, their meaning is described below:
```text
-h, --help            Help message
-d delay, --delay delay
                    Time allocated for players to make the move (default=5s)
-p pace, --pace pace
                    Minimum time the server waits to process the move (to be able to see very
                    fast matches without getting lost in the terminal)
-l log-history, --log-history log-history
                    File for the game log (default=history.txt)
-o output-file, --output-file output-file
                    Output file with game details (includes history)
```

The 'random' player is located in the `advsearch/randomplayer` directory. To play a match with it,
just replace player1 or 2 with randomplayer. As an example, start
a random vs. random match to see the server running:

`python server.py advsearch.randomplayer advsearch.randomplayer -d 1 -p 0.3`

The delay can be 1 second because the random player is very fast (and very incompetent). The pace is 0.3 seconds to follow the progress of the match (you can speed it up or slow it down as needed).

## How it works

Starting with the first player, who will play with the black pieces, the server calls the `make_move(board, color)` function of your `agent.py`. The function receives `board`, an object of the `Board` class and `color`, a character indicating the color with which the move should be made ('B' for black or 'W' for white). See `othello/board.py`.


The server then waits for the delay and receives the tuple (x,y) with the column and row with the player's move. The server processes the move, displays the new state in the terminal and passes the turn to the opponent, repeating this cycle until the end of the game.

At the end of the game, the server displays the score of each player and creates a history.txt file
with all the moves attempted by the players (including the illegal ones).

In an object of the `Board` class, the `tiles` attribute contains the representation of the board as a matrix of characters (or list of strings ;). `W` represents a white piece, `B` a black piece and `.` (dot) represents a free space. In the following example, we have the representation of the initial state of Othello.

```text
[
“........”,
“........”,
“........”,
“...WB...”,
“...BW...”,
“........”,
“........”,
“........”,
]
```

The x-axis grows from left to right and the y-axis grows from top to bottom. The following example shows the coordinate system for the initial state.

```text
  01234567 --> x-axis
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
y-axis
```

IMPORTANT: be careful with the coordinate system vs. matrix indexing. Your make_move function must return the x, y coordinates (column, row) while the matrix representation addresses the row first and then the column.

## Agent Strategy

This project includes an agent named `agente_tangente` that uses the minimax algorithm with alpha-beta pruning.

### Evaluation Function
The evaluation function is based on common Othello strategies. In the early game, it prioritizes moves with few captures near the center of the board. This maximizes the number of possible moves for the agent while minimizing the opponent's options. The goal is to force the opponent into capturing undesirable squares (known as C-squares and X-squares, which are adjacent to the corners), preventing them from capturing a corner.

As the game progresses and the center of the board fills up, the function's priority shifts to capturing corners and edges near already-captured corners.

### Stopping Strategy
The minimax algorithm uses a fixed search depth of 2. While not the most optimal solution, this depth was sufficient to achieve a 100% win rate against the random player.

### Development Notes
Several attempts were made to implement a more "intelligent" stopping strategy, such as:
*   Making the search depth dependent on the number of possible moves from a node.
*   Expanding only promising nodes and ignoring those with a lower score.

In all tested cases, these more intelligent solutions were either slower than the fixed depth of 2 or resulted in victories that were much closer to a draw. Therefore, the simpler solution was kept.

## Testing
To test the basic functionality of your agent, you can run the `test_agent.py` script. Make sure you have a `your_agent` directory with an `agent.py` file inside.

`python test_agent.py`

You can add more test cases to this file to test your agent more thoroughly.


## Notes
* The server checks the legality of the moves before making them.
* Illegal moves result in disqualification.
* The 'random' player just draws a move from the valid ones in the received state.
* In case of problems with the server, report via email.

## TODO
- [ ] Add a Django interface to the board.
