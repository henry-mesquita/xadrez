from .generator import Generator
from pecas.peca import Cor
from pecas.peao import Peao
from pecas.bispo import Bispo
from pecas.dama import Dama
from pecas.torre import Torre
from pecas.cavalo import Cavalo
from pecas.rei import Rei
from .state import GameState


class Judge:
    def __init__(self, generator: Generator) -> None:
        self.generator: Generator = generator


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
