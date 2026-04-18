import pygame as pg
from pygame import Vector2 as vetor
from enum import Enum

class TipoMov(Enum):
    NORMAL = 0
    CAPTURA = 1


class Peca:
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


    @staticmethod
    def lc_valido(linha: int, coluna: int) -> bool:
        """
        Verifica se a linha e coluna são válidas.

        Returns:
            bool: True se a linha e coluna forem validas, False caso contrário.
        """
        return 0 <= linha < 8 and 0 <= coluna < 8
