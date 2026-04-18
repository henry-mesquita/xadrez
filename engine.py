from constantes import *
import numpy as np
from pecas.peca import Peca, TipoMov
from pecas.bispo import Bispo
from pecas.cavalo import Cavalo
from pecas.dama import Dama
from pecas.peao import Peao
from pecas.rei import Rei
from pecas.torre import Torre


class Engine:
    MAPA_PECAS: dict[str, type[Peca]] = {
        'p': Peao,
        'r': Torre,
        'n': Cavalo,
        'b': Bispo,
        'q': Dama,
        'k': Rei
    }

    def __init__(self):
        self.matriz: np.ndarray = np.full((8, 8), None, dtype=object)
        self.movimentos_possiveis:  list[tuple[tuple[int, int], TipoMov]]   = []
        self.pseudo_movimentos:     list[tuple[tuple[int, int], TipoMov]]   = []

        self.carregar_posicao_fen(fen=FEN_INICIAL)
        self.turno = 'w' # w = branco | b = preto


    def mudar_turno(self) -> None:
        self.turno = 'b' if self.turno == 'w' else 'w'


    def carregar_posicao_fen(self, fen: str) -> None:
        """
        Carrega uma posição no padrão FEN para a matriz do tabuleiro.

        Args:
            fen (str): FEN do tabuleiro.
        """
        placement = fen.strip().split()[0]
        ranks = placement.split('/')

        if len(ranks) != 8:
            raise ValueError("FEN inválida: deve ter 8 ranks no piece placement.")

        for i, rank in enumerate(ranks):
            j = 0
            for ch in rank:
                if ch.isdigit():
                    j += int(ch)
                else:
                    cor = 'w' if ch.isupper() else 'b'
                    tipo = ch.lower()

                    if tipo not in ('p', 'r', 'n', 'b', 'q', 'k'):
                        raise ValueError(f"FEN inválida: peça desconhecida '{ch}'.")

                    if j >= 8:
                        raise ValueError("FEN inválida: rank excede 8 colunas.")

                    self.matriz[i, j] = self.criar_peca(tipo, cor, [i, j])
                    j += 1

            if j != 8:
                raise ValueError("FEN inválida: rank não fecha em 8 colunas.")


    def criar_peca(self, tipo, cor, pos):
        return self.MAPA_PECAS[tipo](
            cor=cor,
            posicao=pos
        )
