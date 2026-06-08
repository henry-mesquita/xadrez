import numpy as np
from pecas.peca import Cor, Peca
from pecas.rei import Rei
from .move import *


class Board:
    def __init__(self):
        self.matriz: np.ndarray = np.zeros((8, 8), dtype=object)


    def achar_lc_peca(self, peca: Peca) -> Pos | None:
        """
        Encontra a linha e coluna de uma instância de peça na matriz.

        Args:
            peca (Peca): Instância da peça a ser localizada.

        Returns:
            Pos | None: (linha, coluna) ou None se não encontrada.
        """
        for l in range(8):
            for c in range(8):
                if self.matriz[l, c] == peca:
                    return (l, c)
        return None


    def achar_lc_rei(self, cor: Cor) -> Pos | None:
        """
        Encontra a linha e coluna de uma instância de peça na matriz.

        Args:
            peca (Peca): Instância da peça a ser localizada.

        Returns:
            Pos | None: (linha, coluna) ou None se não encontrada.
        """
        for l in range(8):
            for c in range(8):
                p = self.matriz[l, c]
                if isinstance(p, Rei):
                    if p.cor == cor:
                        return (l, c)
        return None 


    @staticmethod
    def lc_valido(l: int, c: int) -> bool:
        """
        Verifica se a coordenada informada está dentro dos limites do tabuleiro.

        Returns:
            bool: True se válida, False caso contrário.
        """
        return 0 <= l < 8 and 0 <= c < 8 
