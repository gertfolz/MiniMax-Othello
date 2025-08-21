# IA
Implementação do trabalho prático 2 da cadeira de Inteligência Artificial INF01048 2021/2 - UFRGS

Integrantes:
Gert Willem Folz - 00288550
Nikolas Tesche - 00263055
Luiza Reveilleau Frozi - 00289717

Turma B

Nenhuma biblioteca externa foi usada na solução do trabalho



Função de avaliação:
 A função de avaliação foi desenvolvida com base em pesquisas de estratégias de Othello. É recomendado que no início do jogo, sejam feitas
jogadas com poucas capturas, e sempre perto do centro do tabuleiro, de forma a maximizar a quantidade possível de jogadas, e minimizar as
possíveis jogadas do oponente. O objetivo dessa estratégia de minimizar as posições em que o oponente pode jogar, é fazê-lo capturar quadrados
específicos conhecidos como quadrados-C e quadrados-X, que são os quadrados ao redor dos cantos do tabuleiro, e devem ser evitados ao máximo
para não permitir que o oponente capture um canto.
 A função então tenta no início do jogo maximizar a quantidade de movimentos possíveis, e conforme o centro do tabuleiro é preenchido, passa
a priorizar capturar os cantos e laterais perto de cantos já capturados.

Estratégia de parada:
 O algoritmo minimax utilizado se aproveita da poda alfa-beta como tentativa de reduzir a quantidade de nodos expandidos e visitados. A
estratégia de parads no fim foi escolhida como uma profundidade fixa de valor 2, que apesar de não ser a melhor opção, já forneceu 100%
de vitória contra o jogador random.

Dificuldades:
 Foram feitas diversas tentativas de mudar a estratégia de parada para uma solução mais "inteligente". Como fazer a profundidade a ser explorada
depender do número de jogadas possíveis a partir de um nodo; ou apenas expandir nodos promissores, e ignorar nodos com uma pontuação mais baixa.
Em todos os casos testados, as soluções mais inteligentes eram ou mais devagar que a profundidade fixa de 2, ou resultavam em partidas ainda
vitoriosas, mas muito mais próximas de empates. Então a decisão final foi manter a solução mais simples.

Bibliografia:
https://www.ultraboardgames.com/othello/tips.php
https://www.ultraboardgames.com/othello/strategy.php (O primeiro vídeo apresentado nesse link foi especialmente útil para explicar nomenclaturas)
https://www.youtube.com/watch?v=SvxTrjvPrSY
