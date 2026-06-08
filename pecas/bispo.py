from constantes import *
from pecas.peca import Peca, Coord
from logic.move import *


class Bispo(Peca):
    """
    Peça de xadrez que se move diagonalmente.

    Pode mover-se qualquer número de casas na diagonal enquanto o caminho
    estiver desobstruído.
    """
    def __init__(
        self,
        cor: Cor,
        posicao: Coord,
        valor: float
    ) -> None:
        super().__init__(cor, posicao)
        self.tipo: TipoPeca = TipoPeca.BISPO
        self.valor: float = valor


    def gerar_pseudo_movimentos(
        self,
        lc: tuple[int, int]
    ) -> list[tuple[int, int]]:
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

                if not lc_valido(l, c):
                    break
                mov.append((l, c))

        return mov
