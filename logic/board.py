import numpy as np

class Board:
    def __init__(self):
        self.matriz = np.zeros((8, 8), dtype=object)


    @staticmethod
    def lc_valido(linha: int, coluna: int) -> bool:
        """
        Verifica se a coordenada informada está dentro dos limites do tabuleiro.

        Returns:
            bool: True se válida, False caso contrário.
        """
        return 0 <= linha < 8 and 0 <= coluna < 8 
