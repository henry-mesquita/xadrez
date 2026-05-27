from constantes import *
from pecas.peca import Peca, TipoPeca


class Rei(Peca):
    """
    Peça mais importante do xadrez, move-se uma casa em qualquer direção.

    Seu objetivo é proteger o rei oposto do xeque para vencer a partida.
    """
    def __init__(
        self,
        cor: str,
        posicao: list[int, int]
    ) -> None:
        super().__init__(cor, posicao)
        self.tipo: TipoPeca     = TipoPeca.REI
        self.pontuacao: float   = float('inf')


    def gerar_pseudo_movimentos(
        self,
        lc: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Gera os movimentos pseudo legais para o rei (k).

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[tuple[int, int]] = []

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

        for offset in offsets_rei:
            casa_destino = (lc[0] + offset[0], lc[1] + offset[1])
            if self.lc_valido(casa_destino[0], casa_destino[1]):
                mov.append(casa_destino)

        return mov
