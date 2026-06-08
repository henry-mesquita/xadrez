from constantes import *
from pecas.peca import Peca, Coord
from logic.move import *


class Torre(Peca):
    """
    Peça de xadrez que se move horizontalmente ou verticalmente.

    Pode mover-se qualquer número de casas enquanto o caminho
    estiver desobstruído.
    """
    def __init__(
        self,
        cor: Cor,
        posicao: Coord,
        valor: float
    ) -> None:
        super().__init__(cor, posicao)
        self.tipo: TipoPeca = TipoPeca.TORRE
        self.valor: float = valor


    def gerar_pseudo_movimentos(
        self,
        lc: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Gera os movimentos pseudo legais da torre.

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[tuple[int, int]] = []

        direcoes = ((0, 1), (0, -1), (1, 0), (-1, 0))

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
