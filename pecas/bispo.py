from constantes import *
from logic.move import *
from pecas.peca import Peca, Coord


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
        """
        Inicializa a peça de bispo.

        Args:
            cor (Cor): Cor da peça.
            posicao (Coord): Posição inicial da peça.
        """
        super().__init__(cor, posicao)
        self.tipo: TipoPeca = TipoPeca.BISPO
        self.valor: float = valor


    def gerar_pseudo_movimentos(
        self,
        lc: Pos
    ) -> list[Pos]:
        """
        Gera os movimentos pseudo legais do bispo.

        Args:
            lc (Pos): Linha e coluna da peça.

        Returns:
            list[Pos]: Lista de movimentos possíveis.
        """
        mov: list[Pos] = []

        direcoes = ((-1, -1), (-1, 1), (1, -1), (1, 1))

        for dl, dc in direcoes:
            l, c = lc
            while True:
                l += dl
                c += dc

                if not lc_valido(l, c):
                    break
                mov.append((l, c))

        return mov
