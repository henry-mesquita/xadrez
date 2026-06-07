from pecas.peca import Cor, Peca
from pecas.peao import Peao
from pecas.bispo import Bispo
from pecas.dama import Dama
from pecas.torre import Torre
from pecas.cavalo import Cavalo
from pecas.rei import Rei
from .board import Board
from .state import GameState
from .move import TipoMov
import numpy as np


class Judge:
    def __init__(self, board: Board) -> None:
        self.board: Board = board


    def classificar_movimentos(
        self,
        peca: Peca,
        origem: tuple[int, int],
        movimentos: list[tuple[int, int]]
    ) -> list[tuple[tuple[int, int], TipoMov]]:
        """
        Classifica movimentos pseudo-legais como normais ou de captura.

        Args:
            peca (Peca): A peça que está se movendo.
            origem (tuple[int, int]): Casa de origem.
            movimentos (list[tuple[int, int]]): Lista de destinos pseudo-legais.

        Returns:
            list[tuple[tuple[int, int], TipoMov]]: Destinos validados com seu tipo.
        """
        movs: list[tuple[tuple[int, int], TipoMov]] = []
        for casa in movimentos:
            tipo = self._classificar_movimento(
                peca=peca,
                origem=origem,
                destino_lc=casa
            )
            if tipo is not None:
                movs.append((casa, tipo))
        return movs


    def _classificar_movimento(
        self,
        peca: Peca,
        origem: tuple[int, int],
        destino_lc: tuple[int, int]
    ) -> TipoMov | None:
        """
        Valida logicamente se um movimento pode ser realizado.

        Args:
            peca (Peca): Peça em movimento.
            origem (tuple[int, int]): Coordenada de origem.
            destino_lc (tuple[int, int]): Coordenada de destino.

        Returns:
            TipoMov | None: Tipo do movimento se válido, None caso contrário.
        """
        destino = self.board.matriz[destino_lc[0], destino_lc[1]]

        if isinstance(peca, Peao):
            delta = (destino_lc[0] - origem[0], destino_lc[1] - origem[1])
            if peca.cor == Cor.BRANCO:
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
                if destino is None and self.board.matriz[meio[0], meio[1]] is None:
                    return TipoMov.NORMAL
                return None

            if delta in captures:
                if destino is not None and destino.cor != peca.cor:
                    return TipoMov.CAPTURA
                return None

            return None

        if isinstance(peca, (Bispo, Dama, Torre)):
            if not self.caminho_livre(
                origem=origem,
                destino=destino_lc,
                matriz=self.board.matriz
            ):
                return None

        if destino is not None:
            if destino.cor == peca.cor:
                return None
            return TipoMov.CAPTURA

        return TipoMov.NORMAL


    @staticmethod
    def caminho_livre(
        origem: tuple[int, int],
        destino: tuple[int, int],
        matriz: np.ndarray
    ) -> bool:
        """
        Verifica se há obstáculos entre duas casas para peças deslizantes.

        Args:
            origem (tuple[int, int]): Casa inicial.
            destino (tuple[int, int]): Casa final.

        Returns:
            bool: True se o caminho estiver vazio, False caso contrário.
        """
        delta = (destino[0] - origem[0], destino[1] - origem[1])
        passo_l = 0 if delta[0] == 0 else (1 if delta[0] > 0 else -1)
        passo_c = 0 if delta[1] == 0 else (1 if delta[1] > 0 else -1)

        if passo_l == 0 and passo_c == 0:
            return False

        atual = (origem[0] + passo_l, origem[1] + passo_c)
        while atual != destino:
            if matriz[atual[0], atual[1]] is not None:
                return False
            atual = (atual[0] + passo_l, atual[1] + passo_c)
        return True


    def verificar_xeque(self, cor: str, state: GameState) -> bool:
        """
        Verifica se o rei da cor informada está sob ataque.

        Args:
            cor (str): Cor do rei a ser verificado.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        cor = cor.lower()
        if cor not in (Cor.PRETO, Cor.BRANCO):
            raise ValueError('Cor precisa ser "w" ou "b"')
        
        lc_rei = state.board.achar_lc_rei(cor=cor)
        if lc_rei is None:
            return False

        horizontais = self._verificar_horizontais(
            lc_rei=lc_rei,
            cor=cor,
            state=state
        )
        diagonais = self._verificar_diagonais(
            lc_rei=lc_rei,
            cor=cor,
            state=state
        )
        cavalo = self._verificar_cavalo(
            lc_rei=lc_rei,
            cor=cor,
            state=state
        )
        rei = self._verificar_rei(
            lc_rei=lc_rei,
            cor=cor,
            state=state
        )
        peao = self._verificar_peao(
            lc_rei=lc_rei,
            cor=cor,
            state=state
        )

        return horizontais or diagonais or cavalo or rei or peao
    

    @staticmethod
    def _verificar_horizontais(
        lc_rei: tuple[int, int],
        cor: str,
        state: GameState
    ) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças horizontais.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        direcoes_horizontais = (
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0)
        )
        for direcao in direcoes_horizontais:
            l, c = lc_rei
            while True:
                l += direcao[0]
                c += direcao[1]
                if not state.board.lc_valido(linha=l, coluna=c):
                    break
                destino = state.board.matriz[l, c]
                if destino is None:
                    continue
                if destino.cor != cor and isinstance(destino, (Torre, Dama)):
                    return True
                break
        return False


    @staticmethod
    def _verificar_diagonais(
        lc_rei: tuple[int, int],
        cor: str,
        state: GameState
    ) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças diagonais.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        direcoes_diagonais = (
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1)
        )

        for direcao in direcoes_diagonais:
            l, c = lc_rei
            while True:
                l += direcao[0]
                c += direcao[1]
                if not state.board.lc_valido(linha=l, coluna=c): break
                destino = state.board.matriz[l, c]
                if destino is None: continue
                if destino.cor != cor and isinstance(destino, (Bispo, Dama)):
                    return True
                break
        return False


    @staticmethod
    def _verificar_cavalo(
        lc_rei: tuple[int, int],
        cor: str,
        state: GameState
    ) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças de cavalo.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        offsets_cavalo = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (2, -1),
            (2, 1),
            (1, -2),
            (1, 2)
        )
        for offset in offsets_cavalo:
            l, c = lc_rei[0] + offset[0], lc_rei[1] + offset[1]
            if state.board.lc_valido(linha=l, coluna=c):
                destino = state.board.matriz[l, c]
                if destino and isinstance(destino, Cavalo) and destino.cor != cor:
                    return True
        return False


    @staticmethod
    def _verificar_rei(
        lc_rei: tuple[int, int],
        cor: str,
        state: GameState
    ) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças de rei.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        offsets_rei = (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (1, -1),
            (1, 0),
            (1, 1),
            (0, -1),
            (0, 1)
        )
        for offset in offsets_rei:
            l, c = lc_rei[0] + offset[0], lc_rei[1] + offset[1]
            if state.board.lc_valido(linha=l, coluna=c):
                destino = state.board.matriz[l, c]
                if destino and isinstance(destino, Rei) and destino.cor != cor:
                    return True
        return False


    @staticmethod
    def _verificar_peao(
        lc_rei: tuple[int, int],
        cor: str,
        state: GameState
    ) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças de peão.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        direcao = -1 if cor == Cor.BRANCO else 1
        offsets_peao = (
            (direcao, -1),
            (direcao, 1)
        )

        for offset in offsets_peao:
            l, c = lc_rei[0] + offset[0], lc_rei[1] + offset[1]
            if state.board.lc_valido(linha=l, coluna=c):
                destino = state.board.matriz[l, c]
                if destino and isinstance(destino, Peao) and destino.cor != cor:
                    return True
        return False
