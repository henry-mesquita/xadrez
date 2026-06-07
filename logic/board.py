import numpy as np
from pecas.peca import Cor, Peca
from pecas.rei import Rei

class Board:
    def __init__(self):
        self.matriz = np.zeros((8, 8), dtype=object)


    def achar_lc_peca(self, peca: Peca) -> tuple[int, int] | None:
        """
        Encontra a linha e coluna de uma instância de peça na matriz.

        Args:
            peca (Peca): Instância da peça a ser localizada.

        Returns:
            tuple[int, int] | None: (linha, coluna) ou None se não encontrada.
        """
        for li in range(8):
            for co in range(8):
                if self.matriz[li, co] == peca:
                    return (li, co)
        return None


    def achar_lc_rei(self, cor: Cor) -> tuple[int, int] | None:
        """
        Encontra a linha e coluna de uma instância de peça na matriz.

        Args:
            peca (Peca): Instância da peça a ser localizada.

        Returns:
            tuple[int, int] | None: (linha, coluna) ou None se não encontrada.
        """
        for li in range(8):
            for co in range(8):
                p = self.matriz[li, co]
                if isinstance(p, Rei):
                    if p.cor == cor:
                        return (li, co)
        return None 


    @staticmethod
    def lc_valido(linha: int, coluna: int) -> bool:
        """
        Verifica se a coordenada informada está dentro dos limites do tabuleiro.

        Returns:
            bool: True se válida, False caso contrário.
        """
        return 0 <= linha < 8 and 0 <= coluna < 8 
