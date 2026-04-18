from constantes import *
from pecas.peca import Peca
from pygame import Vector2 as vetor


class Cavalo(Peca):
    CAMINHOS_SPRITES = {
        'w': 'cavalo_branco.png',
        'b': 'cavalo_preto.png'
    }

    def __init__(
        self,
        cor: str,
        posicao: vetor
    ) -> None:
        super().__init__(cor, posicao)


    def gerar_pseudo_movimentos(self, lc: tuple[int, int]) -> list[tuple[int, int]]:
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
