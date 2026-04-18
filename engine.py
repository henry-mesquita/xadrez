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


    def achar_lc_peca(self, peca) -> tuple[int, int] | None:
        """
        Encontra a linha e coluna da peça na matriz.

        Returns:
            tuple[int, int] | None: Linha e coluna da peça, ou None se a peça não for encontrada.
        """
        for li in range(8):
            for co in range(8):
                if self.matriz[li, co] == peca:
                    return (li, co)


    def gerar_mov_peca(self, p) -> None:
        """
        Gera os movimentos possíveis para a peça selecionada.

        Args:
            p (Peca): Peça selecionada.

        Returns:
            list[tuple[tuple[int, int], TipoMov]]: Lista de movimentos possíveis com tipo.
        """
        origem = self.achar_lc_peca(p)
        if origem is None:
            self.movimentos_possiveis = []
            self.pseudo_movimentos = []

        self.pseudo_movimentos = p.gerar_pseudo_movimentos(lc=origem)
        self.movimentos_possiveis = self._classificar_movimentos(p, origem, self.pseudo_movimentos)


    def _classificar_movimentos(
        self,
        peca,
        origem: tuple[int, int],
        movimentos: list[tuple[int, int]]
    ) -> list[tuple[tuple[int, int], TipoMov]]:
        """
        Classifica movimentos pseudo-legais como normais ou de captura.

        Args:
            peca (Peca): A peça que está se movendo.
            origem (tuple[int, int]): Casa de origem da peça.
            movimentos (list[tuple[int, int]]): Movimentos pseudo-legais gerados pela peça.

        Returns:
            list[tuple[tuple[int, int], TipoMov]]: Movimentos válidos com tipo.
        """
        movs: list[tuple[tuple[int, int], TipoMov]] = []
        for casa in movimentos:
            tipo = self._validar_movimento(peca, origem, casa)
            if tipo is not None:
                movs.append((casa, tipo))
        return movs


    def _validar_movimento(
        self,
        peca,
        origem: tuple[int, int],
        destino_lc: tuple[int, int]
    ) -> TipoMov | None:
        """
        Valida um movimento pseudo-legal e determina o tipo de movimento.

        Args:
            peca (Peca): Peça que está se movendo.
            origem (tuple[int, int]): Casa de origem.
            destino_lc (tuple[int, int]): Casa de destino.

        Returns:
            TipoMov | None: Tipo de movimento válido ou None se inválido.
        """
        destino = self.matriz[destino_lc[0], destino_lc[1]]

        if isinstance(peca, Peao):
            delta = (destino_lc[0] - origem[0], destino_lc[1] - origem[1])
            if peca.cor == 'w':
                forward = (-1, 0)
                double_forward = (-2, 0)
                captures = [(-1, -1), (-1, 1)]
            else:
                forward = (1, 0)
                double_forward = (2, 0)
                captures = [(1, -1), (1, 1)]

            if delta == forward:
                return TipoMov.NORMAL if destino is None else None

            if delta == double_forward:
                meio = (origem[0] + forward[0], origem[1])
                if destino is None and self.matriz[meio[0], meio[1]] is None:
                    return TipoMov.NORMAL
                return None

            if delta in captures:
                if destino is not None and destino.cor != peca.cor:
                    return TipoMov.CAPTURA
                return None

            return None

        if isinstance(peca, (Bispo, Dama, Torre)):
            if not self._caminho_livre(origem, destino_lc):
                return None

        if destino is not None:
            if destino.cor == peca.cor:
                return None
            return TipoMov.CAPTURA

        return TipoMov.NORMAL


    def _caminho_livre(self, origem: tuple[int, int], destino: tuple[int, int]) -> bool:
        """
        Verifica se o caminho entre origem e destino está livre para movimentos deslizantes.

        Args:
            origem (tuple[int, int]): Casa de origem.
            destino (tuple[int, int]): Casa de destino.

        Returns:
            bool: True se não houver peças entre origem e destino.
        """
        delta = (destino[0] - origem[0], destino[1] - origem[1])
        passo_l = 0 if delta[0] == 0 else (1 if delta[0] > 0 else -1)
        passo_c = 0 if delta[1] == 0 else (1 if delta[1] > 0 else -1)

        if passo_l == 0 and passo_c == 0:
            return False

        atual = (origem[0] + passo_l, origem[1] + passo_c)
        while atual != destino:
            if self.matriz[atual[0], atual[1]] is not None:
                return False
            atual = (atual[0] + passo_l, atual[1] + passo_c)
        return True


    def achar_lc_rei(self, cor: str) -> tuple[int, int] | None:
        """
        Encontra a linha e coluna do rei na matriz baseado na cor passada por parâmetro.

        Args:
            cor (str): Cor do rei.

        Returns:
            tuple[int, int] | None: Linha e coluna do rei, ou None se o rei nao for encontrado.
        """
        cor = cor.lower()
        if cor not in ('b', 'w'):
            raise ValueError('Cor precisa ser "w" ou "b"')

        for li in range(8):
            for co in range(8):
                p = self.matriz[li, co]
                if p is not None and isinstance(p, Rei) and p.cor == cor:
                    return (li, co)
        return None


    def verificar_xeque(self, cor: str) -> bool:
        cor = cor.lower()
        if cor not in ('b', 'w'):
            raise ValueError('Cor precisa ser "w" ou "b"')
        
        lc_rei = self.achar_lc_rei(cor)
        if lc_rei is None:
            return False

        # torre e dama (horizontais)
        direcoes_horizontais = ((0, 1), (0, -1), (1, 0), (-1, 0))
        for direcao in direcoes_horizontais:
            l = lc_rei[0]
            c = lc_rei[1]
            while True:
                l += direcao[0]
                c += direcao[1]

                if not self.lc_valido(l, c):
                    break
                
                destino = self.matriz[l, c]

                if destino is None:
                    continue

                if destino.cor != cor and isinstance(destino, (Torre, Dama)):
                    return True
                break

        # bispo e dama (diagonais)
        direcoes_diagonais = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        for direcao in direcoes_diagonais:
            l = lc_rei[0]
            c = lc_rei[1]
            while True:
                l += direcao[0]
                c += direcao[1]

                if not self.lc_valido(l, c):
                    break
                
                destino = self.matriz[l, c]

                if destino is None:
                    continue

                if destino.cor != cor and isinstance(destino, (Bispo, Dama)):
                    return True
                break

        # cavalo
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
            l = lc_rei[0]
            c = lc_rei[1]

            l += offset[0]
            c += offset[1]

            if not self.lc_valido(l, c):
                continue
            
            destino = self.matriz[l, c]

            if destino is None:
                continue

            if isinstance(destino, Cavalo) and destino.cor != cor:
                return True
        
        # rei
        offsets_rei = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (1, -1),
            (1, 0),
            (1, 1),
            (0, -1),
            (0, 1)
        ]
        for offset in offsets_rei:
            l = lc_rei[0]
            c = lc_rei[1]

            l += offset[0]
            c += offset[1]

            if not self.lc_valido(l, c):
                continue
            
            destino = self.matriz[l, c]

            if destino is None:
                continue
            
            if isinstance(destino, Rei) and destino.cor != cor:
                return True
        
        # peão
        if cor == 'w':
            offsets_peao = [
                (-1, -1),
                (-1, 1)
            ]
        elif cor == 'b':
            offsets_peao = [
                (1, -1),
                (1, 1)
            ]
        
        for offset in offsets_peao:
            l = lc_rei[0]
            c = lc_rei[1]

            l += offset[0]
            c += offset[1]

            if not self.lc_valido(l, c):
                continue
            
            destino = self.matriz[l, c]

            if destino is None:
                continue
            
            if isinstance(destino, Peao) and destino.cor != cor:
                return True
        return False


    @staticmethod
    def lc_valido(linha: int, coluna: int) -> bool:
        """
        Verifica se a linha e coluna são válidas.

        Returns:
            bool: True se a linha e coluna forem validas, False caso contrário.
        """
        return 0 <= linha < 8 and 0 <= coluna < 8
