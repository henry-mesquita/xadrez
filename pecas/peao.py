from constantes import *
from pecas.peca import Peca


class Peao(Peca):
    def __init__(
        self,
        cor: str,
        posicao: list[int, int]
    ) -> None:
        super().__init__(cor, posicao)
        self.tipo = 'p'


    def gerar_pseudo_movimentos(self, lc: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Gera os movimentos pseudo legais caso o tipo da peça seja o peão (p).

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[tuple[int, int]] = []

        if self.cor == 'w': # se cor for branco
            
            offsets_peao = [
                (-1, 0)
            ]

            offsets_captura_peao = [
                (-1, -1),
                (-1, 1)
            ]

            if lc[0] == 6:
                offsets_peao.append((-2, 0))
        else: # se cor for preto
            offsets_peao = [
                (1, 0)
            ]

            offsets_captura_peao = [
                (1, -1),
                (1, 1)
            ]

            if lc[0] == 1:
                offsets_peao.append((2, 0))

        
        for offset in offsets_peao:
            casa_destino = (lc[0] + offset[0], lc[1] + offset[1])
            if self.lc_valido(casa_destino[0], casa_destino[1]):
                mov.append(casa_destino)
        
        for offset_captura in offsets_captura_peao:
            casa_destino = (lc[0] + offset_captura[0], lc[1] + offset_captura[1])
            if self.lc_valido(casa_destino[0], casa_destino[1]):
                mov.append(casa_destino)

        return mov
