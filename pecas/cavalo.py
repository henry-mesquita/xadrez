from constantes import *
from pecas.peca import Peca
from pygame import Vector2 as vetor
from os.path import join
import pygame as pg


class Cavalo(Peca):
    CAMINHOS_SPRITES = {
        'w': 'cavalo_branco.png',
        'b': 'cavalo_preto.png'
    }

    def __init__(
        self,
        cor: str,
        TAMANHO_PECA: int,
        posicao: vetor
    ) -> None:
        super().__init__(cor, posicao)
        self.inicializar_sprite(
            largura=TAMANHO_PECA,
            altura=TAMANHO_PECA,
            nome_sprite=self.CAMINHOS_SPRITES[self.cor]
        )


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
