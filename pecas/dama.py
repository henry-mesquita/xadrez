from constantes import *
from logic.move import *
from pecas.peca import Peca, Coord


class Dama(Peca):
    """
    Peça de xadrez mais poderosa, combina movimentos de torre e bispo.

    Pode mover-se qualquer número de casas na horizontal, vertical ou diagonal.
    """
    def __init__(
        self,
        cor: Cor,
        posicao: Coord,
        valor: float
    ) -> None:
        """
        Inicializa a peça de dama.

        Args:
            cor (Cor): Cor da peça.
            posicao (Coord): Posição inicial da peça.
        """
        super().__init__(cor, posicao)
        self.tipo: TipoPeca = TipoPeca.DAMA
        self.valor: float = valor


    def gerar_pseudo_movimentos(
        self,
        lc: Pos
    ) -> list[Pos]:
        """
        Gera os movimentos pseudo legais da dama.

        Args:
            lc (Pos): Linha e coluna da peça.

        Returns:
            list[Pos]: Lista de movimentos possíveis.
        """
        mov: list[Pos] = []

        direcoes = ((0, 1), (0, -1), (1, 0), (-1, 0)) # horizontais

        for direcao in direcoes:
            l = lc[0]
            c = lc[1]
            while True:
                l += direcao[0]
                c += direcao[1]

                if not lc_valido(l, c):
                    break
                mov.append((l, c))

        direcoes = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # diagonais

        for direcao in direcoes:
            l = lc[0]
            c = lc[1]
            while True:
                l += direcao[0]
                c += direcao[1]

                if not lc_valido(l, c):
                    break
                mov.append((l, c))

        return mov
