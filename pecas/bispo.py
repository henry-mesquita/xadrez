from constantes import *
from pecas.peca import Peca


class Bispo(Peca):
    def __init__(
        self,
        cor: str,
        posicao: list[int, int]
    ) -> None:
        super().__init__(cor, posicao)
        self.tipo = 'b'


    def gerar_pseudo_movimentos(self, lc: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Gera os movimentos pseudo legais do bispo.

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[tuple[int, int]] = []

        direcoes = ((-1, -1), (-1, 1), (1, -1), (1, 1))

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
