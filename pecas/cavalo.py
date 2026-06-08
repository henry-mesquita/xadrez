from constantes import *
from pecas.peca import Peca
from logic.move import *


class Cavalo(Peca):
    """
    Peça de xadrez que se move em padrão L (2+1 ou 1+2 casas).

    Realiza saltos e não é bloqueado por outras peças no caminho.
    """
    def __init__(
        self,
        cor: str,
        posicao: tuple[int, int]
    ) -> None:
        super().__init__(cor, posicao)
        self.tipo: TipoPeca = TipoPeca.CAVALO
        self.pontuacao: int = 3


    def gerar_pseudo_movimentos(
        self,
        lc: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Gera os movimentos pseudo legais do cavalo.

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[tuple[int, int]] = []

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

        for offset in offsets_cavalo:
            casa_destino = (lc[0] + offset[0], lc[1] + offset[1])
            if self.lc_valido(casa_destino[0], casa_destino[1]):
                mov.append(casa_destino)

        return mov
