from constantes import *
from pecas.peca import Peca
from logic.move import *


class Dama(Peca):
    """
    Peça de xadrez mais poderosa, combina movimentos de torre e bispo.

    Pode mover-se qualquer número de casas na horizontal, vertical ou diagonal.
    """
    def __init__(
        self,
        cor: str,
        posicao: list[int, int]
    ) -> None:
        super().__init__(cor, posicao)
        self.tipo: TipoPeca = TipoPeca.DAMA
        self.pontuacao: int = 9


    def gerar_pseudo_movimentos(
        self,
        lc: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Gera os movimentos pseudo legais da dama.

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[tuple[int, int]] = []

        direcoes = ((0, 1), (0, -1), (1, 0), (-1, 0)) # horizontais

        for direcao in direcoes:
            l = lc[0]
            c = lc[1]
            while True:
                l += direcao[0]
                c += direcao[1]

                if not self.lc_valido(l, c):
                    break
                mov.append((l, c))

        direcoes = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # diagonais

        for direcao in direcoes:
            l = lc[0]
            c = lc[1]
            while True:
                l += direcao[0]
                c += direcao[1]

                if not self.lc_valido(l, c):
                    break
                mov.append((l, c))

        return mov
