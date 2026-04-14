import pygame as pg
from os.path import join
from pygame import Vector2 as vetor
from enum import Enum
from pathlib import Path

class TipoMov(Enum):
    NORMAL = 0
    CAPTURA = 1


class Peca:
    BASE_DIR    = Path(__file__).resolve().parent
    IMG_DIR     = BASE_DIR.parent / "img"

    def __init__(
        self,
        cor: str,
        posicao: vetor
    ) -> None:
        """
        Inicializa uma peça.

        Args:
            cor (str): Cor da peça ('w' para branco ou 'b' para preto).
            tipo (str): Tipo da peça ('p' para peão, 'r' para torre, 'n' para cavalo, 'b' para bispo, 'q' para dama, 'k' para rei).
            TAMANHO_PECA (int): Tamanho da peça.
            posicao (vetor): Posição da peça.
        """
        if cor.lower() not in ('b', 'w'):
            raise ValueError("Cor tem que estar em: ('b', 'w')")
        
        self.cor: str       = cor.lower()
        self.posicao: vetor = posicao.copy() # Posição do sprite


    def __str__(self) -> str:
        """Retorna uma representação de string da peça."""
        return f'Cor: {self.cor}'
    

    def __repr__(self) -> str:
        """Retorna uma representação de depuração da peça."""
        return f"{self.cor})"
    

    def inicializar_sprite(self, largura: int, altura: int, nome_sprite: str) -> None:
        caminho_sprite = self.IMG_DIR / nome_sprite
        self.sprite = pg.transform.scale(pg.image.load(caminho_sprite), (largura, altura))
        self.rect = self.sprite.get_rect(topleft=self.posicao)


    def desenhar_sprite(self, tela: pg.Surface) -> None:
        """
        Desenha o sprite da peça na tela.
        
        Args:
            tela (pg.Surface): Superfície na qual é desenhado o sprite.
        """
        if self.sprite is not None:
            tela.blit(self.sprite, self.rect)


    @staticmethod
    def lc_valido(linha: int, coluna: int) -> bool:
        """
        Verifica se a linha e coluna são válidas.

        Returns:
            bool: True se a linha e coluna forem validas, False caso contrário.
        """
        return 0 <= linha < 8 and 0 <= coluna < 8
