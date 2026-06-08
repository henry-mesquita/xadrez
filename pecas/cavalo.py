from constantes import *
from logic.move import *
from pecas.peca import Peca, Coord


class Cavalo(Peca):
    """
    Peça de xadrez que se move em padrão L (2+1 ou 1+2 casas).

    Realiza saltos e não é bloqueado por outras peças no caminho.
    """
    def __init__(
        self,
        cor: Cor,
        posicao: Coord,
        valor: float
    ) -> None:
        """
        Inicializa a peça de cavalo.

        Args:
            cor (Cor): Cor da peça.
            posicao (Coord): Posição inicial da peça.
        """
        super().__init__(cor, posicao)
        self.tipo: TipoPeca = TipoPeca.CAVALO
        self.valor: float = valor


    def gerar_pseudo_movimentos(
        self,
        lc: Pos
    ) -> list[Pos]:
        """
        Gera os movimentos pseudo legais do cavalo.

        Args:
            lc (Pos): Linha e coluna da peça.

        Returns:
            list[Pos]: Lista de movimentos possíveis.
        """
        mov: list[Pos] = []

        offsets_cavalo = [
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (2, -1),
            (2, 1),
            (1, -2),
            (1, 2)
        ]

        for offset_l, offset_c in offsets_cavalo:
            l, c = lc
            casa_destino = (l + offset_l, c + offset_c)
            if lc_valido(casa_destino[0], casa_destino[1]):
                mov.append(casa_destino)

        return mov
