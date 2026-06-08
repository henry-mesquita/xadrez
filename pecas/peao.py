from constantes import *
from logic.move import *
from pecas.peca import Peca, Coord


class Peao(Peca):
    """
    Peça de xadrez que avança uma casa (ou duas no primeiro movimento).

    Captura diagonalmente. Possui movimento e captura diferenciados.
    """
    def __init__(
        self,
        cor: Cor,
        posicao: Coord,
        valor: float
    ) -> None:
        """
        Inicializa a peça de peão.

        Args:
            cor (Cor): Cor da peça.
            posicao (Coord): Posição inicial da peça.
        """
        super().__init__(cor, posicao)
        self.tipo: TipoPeca = TipoPeca.PEAO
        self.valor: float = valor


    def gerar_pseudo_movimentos(
        self,
        lc: Pos
    ) -> list[Pos]:
        """
        Gera os movimentos pseudo legais caso o tipo da peça seja o peão (p).

        Args:
            lc (Pos): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[Pos] = []

        if self.cor == Cor.BRANCO:
            offsets_peao = [
                (-1, 0)
            ]

            offsets_captura_peao = [
                (-1, -1),
                (-1, 1)
            ]

            if lc[0] == 6:
                offsets_peao.append((-2, 0))
        else:
            offsets_peao = [
                (1, 0)
            ]

            offsets_captura_peao = [
                (1, -1),
                (1, 1)
            ]

            if lc[0] == 1:
                offsets_peao.append((2, 0))

        
        for offset_l, offset_c in offsets_peao:
            l, c = lc
            casa_destino = (l + offset_l, c + offset_c)
            if lc_valido(casa_destino[0], casa_destino[1]):
                mov.append(casa_destino)

        for offset_l, offset_c in offsets_captura_peao:
            l, c = lc
            casa_destino = (l + offset_l, c + offset_c)
            if lc_valido(casa_destino[0], casa_destino[1]):
                mov.append(casa_destino)

        return mov
