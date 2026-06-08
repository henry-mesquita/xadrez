from constantes import *
from logic.move import *
from pecas.peca import Peca, Coord


class Rei(Peca):
    """
    Peça mais importante do xadrez, move-se uma casa em qualquer direção.

    Seu objetivo é proteger o rei oposto do xeque para vencer a partida.
    """
    def __init__(
        self,
        cor: Cor,
        posicao: Coord,
        valor: float
    ) -> None:
        super().__init__(cor, posicao)
        self.tipo: TipoPeca = TipoPeca.REI
        self.valor: float = valor


    def gerar_pseudo_movimentos(
        self,
        lc: Pos
    ) -> list[Pos]:
        """
        Gera os movimentos pseudo legais para o rei (k).

        Args:
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[Pos] = []

        offsets_rei = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1)
        ]

        for offset_l, offset_c in offsets_rei:
            l, c = lc
            casa_destino = (l + offset_l, c + offset_c)
            if lc_valido(casa_destino[0], casa_destino[1]):
                mov.append(casa_destino)

        return mov
