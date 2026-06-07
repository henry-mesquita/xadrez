from pecas.peca import Cor, Peca
from pecas.peao import Peao
from pecas.bispo import Bispo
from pecas.dama import Dama
from pecas.torre import Torre
from pecas.cavalo import Cavalo
from pecas.rei import Rei
from .board import Board
from .state import GameState
from .move import TipoMov, Movimento
import numpy as np


class Judge:
    ROQUES = {
        (Cor.BRANCO, "curto"): {
            "direito": "roque_curto_branco",
            "origem_rei": (7, 4),
            "destino_rei": (7, 6),
            "origem_torre": (7, 7),
            "destino_torre": (7, 5),
            "casas_seguras": [(7, 5), (7, 6)]
        },

        (Cor.BRANCO, "longo"): {
            "direito": "roque_longo_branco",
            "origem_rei": (7, 4),
            "destino_rei": (7, 2),
            "origem_torre": (7, 0),
            "destino_torre": (7, 3),
            "casas_seguras": [(7, 3), (7, 2)]
        },

        (Cor.PRETO, "curto"): {
            "direito": "roque_curto_preto",
            "origem_rei": (0, 4),
            "destino_rei": (0, 6),
            "origem_torre": (0, 7),
            "destino_torre": (0, 5),
            "casas_seguras": [(0, 5), (0, 6)]
        },

        (Cor.PRETO, "longo"): {
            "direito": "roque_longo_preto",
            "origem_rei": (0, 4),
            "destino_rei": (0, 2),
            "origem_torre": (0, 0),
            "destino_torre": (0, 3),
            "casas_seguras": [(0, 3), (0, 2)]
        }
    }

    def __init__(self, state: Board) -> None:
        self.state: GameState = state


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
        destino = self.state.board.matriz[destino_lc[0], destino_lc[1]]

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
                if destino is None and self.state.board.matriz[meio[0], meio[1]] is None:
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
                matriz=self.state.board.matriz
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


    def adicionar_en_passant(self, mov: list) -> None:
        """
        Adiciona as casas de en passant na lista de movimentos possíveis.

        Args:
            mov (list): Lista de movimentos.

        Returns:
            list: Lista de movimentos com os movimentos de en passant adicionados.
        """
        mov.append(self.state.en_passant)
    

    def adicionar_roques(
        self,
        cor: str,
        mov: list,
        xeque: bool
    ) -> list[tuple[int, int], TipoMov]:
        if self.verificar_roque(cor, "curto", xeque):
            destino = (
                self.ROQUES[(cor, "curto")]["destino_rei"]
            )

            mov.append((destino, TipoMov.ROQUE_CURTO))

        if self.verificar_roque(cor, "longo", xeque):
            destino = (
                self.ROQUES[(cor, "longo")]["destino_rei"]
            )

            mov.append((destino, TipoMov.ROQUE_LONGO))

        return mov


    def verificar_roque(
        self,
        cor: Cor,
        lado: str,
        xeque: bool
    ) -> bool:
        """
        Retorna True se o roque pode ser realizado.

        Args:
            cor (str): Cor do rei.
            lado (str): "curto" ou "longo".

        Returns:
            bool: True se o roque pode ser realizado, False caso contrário.
        """
        dados = self.ROQUES[(cor, lado)]

        direito = getattr(self.state, dados["direito"])

        if not direito:
            return False

        if xeque:
            return False

        if not self.caminho_livre(
            origem=dados["origem_rei"],
            destino=dados["origem_torre"],
            matriz=self.state.board.matriz
        ):
            return False

        for l, c in dados["casas_seguras"]:
            if self.casa_atacada(l, c, cor):
                return False

        return True


    def casa_atacada(self, l: int, c: int, cor_que_seria_atacada: str) -> bool:
        pos = (l, c)
        
        horizontais = self.verificar_horizontais(pos, cor_que_seria_atacada)
        diagonais   = self.verificar_diagonais(pos, cor_que_seria_atacada)
        cavalo      = self.verificar_cavalo(pos, cor_que_seria_atacada)
        rei         = self.verificar_rei(pos, cor_que_seria_atacada)
        peao        = self.verificar_peao(pos, cor_que_seria_atacada)

        return horizontais or diagonais or cavalo or rei or peao


    def verificar_xeque(self, cor: str) -> bool:
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
        
        lc_rei = self.state.board.achar_lc_rei(cor=cor)
        if lc_rei is None:
            return False

        horizontais = self.verificar_horizontais(
            pos=lc_rei,
            cor_defendendo=cor
        )
        diagonais = self.verificar_diagonais(
            pos=lc_rei,
            cor_defendendo=cor
        )
        cavalo = self.verificar_cavalo(
            pos=lc_rei,
            cor_defendendo=cor
        )
        rei = self.verificar_rei(
            pos=lc_rei,
            cor_defendendo=cor
        )
        peao = self.verificar_peao(
            pos=lc_rei,
            cor_defendendo=cor
        )

        return horizontais or diagonais or cavalo or rei or peao


    def verificar_horizontais(
        self,
        pos: tuple[int, int],
        cor_defendendo: str
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
            l, c = pos
            while True:
                l += direcao[0]
                c += direcao[1]
                if not self.state.board.lc_valido(linha=l, coluna=c):
                    break
                destino = self.state.board.matriz[l, c]
                if destino is None:
                    continue
                if destino.cor != cor_defendendo and isinstance(destino, (Torre, Dama)):
                    return True
                break
        return False


    def verificar_diagonais(
        self,
        pos: tuple[int, int],
        cor_defendendo: str
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
            l, c = pos
            while True:
                l += direcao[0]
                c += direcao[1]
                if not self.state.board.lc_valido(linha=l, coluna=c): break
                destino = self.state.board.matriz[l, c]
                if destino is None: continue
                if destino.cor != cor_defendendo and isinstance(destino, (Bispo, Dama)):
                    return True
                break
        return False


    def verificar_cavalo(
        self,
        pos: tuple[int, int],
        cor_defendendo: str
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
            l, c = pos[0] + offset[0], pos[1] + offset[1]
            if self.state.board.lc_valido(linha=l, coluna=c):
                destino = self.state.board.matriz[l, c]
                if destino and isinstance(destino, Cavalo) and destino.cor != cor_defendendo:
                    return True
        return False


    def verificar_rei(
        self,
        pos: tuple[int, int],
        cor_defendendo: str
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
            l, c = pos[0] + offset[0], pos[1] + offset[1]
            if self.state.board.lc_valido(linha=l, coluna=c):
                destino = self.state.board.matriz[l, c]
                if destino and isinstance(destino, Rei) and destino.cor != cor_defendendo:
                    return True
        return False


    def verificar_peao(
        self,
        pos: tuple[int, int],
        cor_defendendo: str
    ) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças de peão.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        direcao = -1 if cor_defendendo == Cor.BRANCO else 1
        offsets_peao = (
            (direcao, -1),
            (direcao, 1)
        )

        for offset in offsets_peao:
            l, c = pos[0] + offset[0], pos[1] + offset[1]
            if self.state.board.lc_valido(linha=l, coluna=c):
                destino = self.state.board.matriz[l, c]
                if destino and isinstance(destino, Peao) and destino.cor != cor_defendendo:
                    return True
        return False
