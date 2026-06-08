from constantes import *
from logic.move import *
from pecas.peca import Peca, Coord


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
        lc: Pos
    ) -> list[Pos]:
        """
        Gera os movimentos pseudo legais da torre.

        Args:
            lc (Pos): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[Pos] = []

        direcoes = ((0, 1), (0, -1), (1, 0), (-1, 0))

        for dl, dc in direcoes:
            l, c = lc
            while True:
                l += dl
                c += dc

                if not lc_valido(l, c):
                    break
                mov.append((l, c))
        
        return mov
