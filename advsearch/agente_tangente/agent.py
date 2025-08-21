from cmath import inf
import random
from ..othello import board
import sys
import copy

MAX_DEPTH = 2 # Constante que determina até onde o minimax vai (testes são necessários pra achar um valor ótimo que não ultrapasse os 5s impostos pelo professor)


# Voce pode criar funcoes auxiliares neste arquivo
# e tambem modulos auxiliares neste pacote.
#
# Nao esqueca de renomear 'your_agent' com o nome
# do seu agente.

def make_move(the_board, color):
    """
    Returns an Othello move
    :param the_board: a board.Board object with the current game state
    :param color: a character indicating the color to make the move ('B' or 'W')
    :return: (int, int) tuple with x, y indexes of the move (remember: 0 is the first row/column)
    """
    # o codigo abaixo apenas retorna um movimento aleatorio valido para
    # a primeira jogada com as pretas.
    # Remova-o e coloque a sua implementacao da poda alpha-beta

    # Inicializa os valores das váriaveis que serão usadas no minimax e o melhor movimento como uma tupla vazia
    bestValue = -inf
    alpha = -inf
    beta = inf
    bestMove = ()
    # Armazena os movimentos válidos na lista legal_moves, que serão comparados os seus valores de retorno com a função minimax
    legal_moves = the_board.legal_moves(color)
    # Print auxiliar para debug
    print(len(legal_moves))
    if len(legal_moves) == 0:
        return (-1, -1)

    for move in legal_moves:
        # Cria uma váriavel auxiliar do tabuleiro pra mexer as peças nela sem mexer no tabuleiro original,
        # podendo assim comparar os valores 
        b = copy.deepcopy(the_board)
        b.process_move(move, color)
        # Para cada movimento válido possivel, fará a rotina do minimax e salva a melhor jogada encontrada até o momento comparando os seus valores
        value = miniMax(b, alpha, beta, 0, False, color)
        if(bestValue < value):
            bestValue = value
            bestMove = move
    # Print para debug
    #the_board.print_board()
    #print(bestMove)
    return bestMove

if __name__ == '__main__':
    b = board.Board()
    move = make_move(b, 'W')
    print(f'A random move for black in the initial state: {move}')
    print('Resulting state:')
    b.process_move(move, 'W')
    b.print_board()


def miniMax(the_board, alpha, beta, depth, isMax, color):
    """
    Algoritmo padrão do minimax, ainda são necessários alguns testes pra checar se o comportamento tá certinho.

    """

    # Definição da variável oposta pra rotinas auxiliares
    if color == 'B':
        opp = 'W'
    else:
        opp = 'B'

    # Se a próxima jogada é do jogador Max  
    if(isMax):
        legal_moves = the_board.legal_moves(color)
        # Checa se ainda existem jogadas válidas para o jogador e se não alcançou a profundidade máxima do grafo
        if(depth == MAX_DEPTH or (len(legal_moves) == 0)):
            # Se não satisfaz alguma das condições do nó, avalia ele e retorna seu valor
            return evaluate_node(the_board, color)
        # Print dos valores alpha beta e quantos movimentos ainda têm pra debug
        #print(alpha,beta, len(legal_moves))
        # Itera todos possíveis movimentos com o mesmo procedimento anterior
        for move in legal_moves:
            b = copy.deepcopy(the_board)
            b.process_move(move, color)
            #print(legal_moves[i])
            # Chama a função do minimax recursivamente, aumentando a profundidade, e passando a rodada pro Min
            # A cor sempre permanece a mesma que é pra saber qual é o jogador original (mas não sei se essa logica eh necessária tbh)
            value = miniMax(b, alpha, beta, depth + 1, False, color)
            # Atualiza o valor de alpha com o maior encontrado
            alpha = max(alpha, value)
            # Se beta for maior, poda a arvore
            if(beta <= alpha):
                break
        return alpha

    # Análoga à função do Max, mas muda os valores pra beta e busca pelo menor valor
    else:
        legal_moves = the_board.legal_moves(opp)
        if(depth == MAX_DEPTH or (len(legal_moves) == 0)):
            return evaluate_node(the_board, color)
        #print(alpha,beta, len(legal_moves))
        for move in legal_moves:
            b = copy.deepcopy(the_board)
            #print(legal_moves[i])
            b.process_move(move, opp)
            value = miniMax(b, alpha, beta, depth + 1, True, color)
            beta = min(beta, value)
            # Poda da árvore
            if(beta <= alpha):
                break
        return beta
        
def evaluate_node(the_board, color):
    """
    Função auxiliar do minimax que avalia a pontuação de cada nó de acordo com quantas peças da cor do jogador max tem
    """

    cornersState = [the_board.tiles[0][0], the_board.tiles[7][0], the_board.tiles[0][7], the_board.tiles[7][7]] # Encontra os valores dos cantos na odem NW, NE, SW, SE

    A_score = 5
    B_score = 3
    C_score = 10
    X_score = 15
    corner_score = 20

    # Alguns quadrados só são vantajosos de controlar se os cantos já estiverem controlados, senão eles devem ser evitados
    A_tiles = [[the_board.tiles[2][0], the_board.tiles[0][2]], [the_board.tiles[5][0], the_board.tiles[7][2]], [the_board.tiles[2][7], the_board.tiles[0][5]], [the_board.tiles[5][7], the_board.tiles[7][5]]]
    B_tiles = [[the_board.tiles[3][0], the_board.tiles[0][3]], [the_board.tiles[4][0], the_board.tiles[7][3]], [the_board.tiles[3][7], the_board.tiles[0][4]], [the_board.tiles[4][7], the_board.tiles[7][4]]]
    C_tiles = [[the_board.tiles[1][0], the_board.tiles[0][1]], [the_board.tiles[6][0], the_board.tiles[7][1]], [the_board.tiles[1][7], the_board.tiles[0][6]], [the_board.tiles[6][7], the_board.tiles[7][6]]]
    X_tiles = [[the_board.tiles[1][1]], [the_board.tiles[6][1]], [the_board.tiles[1][6]], [the_board.tiles[6][6]]]

    if color == 'B':
        opp = 'W'
    else:
        opp = 'B'


    if (len(the_board.legal_moves(color)) + len(the_board.legal_moves(opp)) == 0 and the_board.piece_count.get(color) > the_board.piece_count.get(opp)): # checa se o jogador ganhará por domínio de peças
        return inf
    if (the_board.piece_count.get(opp) == 0): # checa se o oponente perderá por falta de peças
        return inf
    if (the_board.piece_count.get(color) == 0): # checa se o jogador perderá por falta de peças
        return -inf

    score = len(the_board.legal_moves(color)) - len(the_board.legal_moves(opp))  # Ter mais jogadas possíveis que o outro jogador é sempre vantajoso
    score += (cornersState.count(color) - cornersState.count(opp)) * corner_score   # Controlar os cantos é muito vantajoso

    specialTileScore = [0, 0, 0, 0]

    for area in range(0, 4):
        specialTileScore[area] = -(A_tiles[area].count(color) * A_score + B_tiles[area].count(color) * B_score + C_tiles[area].count(color) * C_score + X_tiles[area].count(color) * X_score)
        if cornersState[area] == color:
            specialTileScore[area] = -specialTileScore[area] / 3        # Controlar os quadrados especiais próximos dos cantos já controlados é vantajoso, mas não tão vantajoso quanto proteger outros lados

    score += sum(specialTileScore)

    #the_board.print_board()
    #print(score)

    return score
        


    """else:
        if (the_board.legal_moves('B') + the_board.legal_moves('W') == 0 and the_board.piece_count.get('W') > the_board.piece_count.get('B')):
            return inf                                                      # Checa se é um estado de vitória para W

        score = the_board.piece_count.get('W')"""
    
    #print(score)
    return score                                
    
def isCorner(tuple):
    """
    Outra função pra auxiliar na avaliação de um nó, neste caso, se um movimento colocar uma peça em um dos 4 cantos do tabuleiro, 
    retorna verdadeiro ou falso. Essa função pode ser útil pois uma peça em qualquer esquina não pode ser convertida em jogadas futuras,
    que torna ela uma jogada melhor do que outra em que houvesse o mesmo número de 'flips'.
    """

    # Checa se a tupla de coordenadas recebida pela função (onde a tupla(0) é a coordenada x e a tupla(1) é a coordenada y)
    if (((tuple[0] == 0) and (tuple[1]  in [0, 7])) or ((tuple[0] == 7) and (tuple[1]  in [0, 7]))):    
        return True
    else:
        return False

