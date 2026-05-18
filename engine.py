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


    def __init__(self) -> None:
        """
        Inicializa a engine com o tabuleiro vazio e carrega a posição inicial.
        """
        self.matriz: np.ndarray = np.full((8, 8), None, dtype=object)
        self.movimentos_possiveis:  list[tuple[tuple[int, int], TipoMov]]   = []
        self.pseudo_movimentos:     list[tuple[tuple[int, int], TipoMov]]   = []

        self.carregar_posicao_fen(fen=FEN_INICIAL)
        self.turno = 'w' # w = branco | b = preto


    def executar_movimento(self, mov: Movimento) -> bool:
        """
        Tenta executar um movimento na matriz. 

        Args:
            mov (Movimento): Objeto contendo as coordenadas de origem e destino.

        Returns:
            bool: True se o movimento foi bem sucedido, False caso contrário.
        """
        destinos_validos = [m[0] for m in self.movimentos_possiveis]
        
        if mov.destino not in destinos_validos:
            return False

        peca = self.matriz[mov.origem[0], mov.origem[1]]
        
        self.matriz[mov.destino[0], mov.destino[1]] = peca
        self.matriz[mov.origem[0], mov.origem[1]] = None
        
        peca.posicao = mov.destino
        
        self.movimentos_possiveis = []
        self.pseudo_movimentos = []
        
        return True


    def mudar_turno(self) -> None:
        """
        Alterna o turno atual entre branco ('w') e preto ('b').
        """
        self.turno = 'b' if self.turno == 'w' else 'w'


    def carregar_posicao_fen(self, fen: str) -> None:
        """
        Carrega uma posição no padrão FEN para a matriz do tabuleiro.

        Args:
            fen (str): String no formato FEN.
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

                    self.matriz[i, j] = self.criar_peca(tipo=tipo, cor=cor, pos=[i, j])
                    j += 1

            if j != 8:
                raise ValueError("FEN inválida: rank não fecha em 8 colunas.")


    def criar_peca(self, tipo: str, cor: str, pos: list[int]) -> Peca:
        """
        Instancia uma peça baseada no tipo e cor fornecidos.

        Args:
            tipo (str): Caractere representando o tipo da peça.
            cor (str): 'w' para branco, 'b' para preto.
            pos (list[int]): Coordenadas [linha, coluna].

        Returns:
            Peca: Instância da classe da peça correspondente.
        """
        return self.MAPA_PECAS[tipo](
            cor=cor,
            posicao=pos
        )


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


    def gerar_mov_peca(self, p: Peca) -> None:
        """
        Gera e classifica os movimentos possíveis para a peça selecionada.

        Args:
            p (Peca): A peça selecionada para análise de movimentos.
        """
        origem = self.achar_lc_peca(peca=p)
        if origem is None:
            self.movimentos_possiveis = []
            self.pseudo_movimentos = []

        self.pseudo_movimentos = p.gerar_pseudo_movimentos(lc=origem)
        self.movimentos_possiveis = self._classificar_movimentos(peca=p, origem=origem, movimentos=self.pseudo_movimentos)


    def _classificar_movimentos(
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
            tipo = self._validar_movimento(peca=peca, origem=origem, destino_lc=casa)
            if tipo is not None:
                movs.append((casa, tipo))
        return movs


    def _validar_movimento(
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
            if not self._caminho_livre(origem=origem, destino=destino_lc):
                return None

        if destino is not None:
            if destino.cor == peca.cor:
                return None
            return TipoMov.CAPTURA

        return TipoMov.NORMAL


    def _caminho_livre(self, origem: tuple[int, int], destino: tuple[int, int]) -> bool:
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
            if self.matriz[atual[0], atual[1]] is not None:
                return False
            atual = (atual[0] + passo_l, atual[1] + passo_c)
        return True


    def achar_lc_rei(self, cor: str) -> tuple[int, int] | None:
        """
        Localiza a posição do rei de uma determinada cor na matriz.

        Args:
            cor (str): 'w' para branco, 'b' para preto.

        Returns:
            tuple[int, int] | None: Posição (L, C) do rei.
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
        """
        Verifica se o rei da cor informada está sob ataque.

        Args:
            cor (str): Cor do rei a ser verificado.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        cor = cor.lower()
        if cor not in ('b', 'w'):
            raise ValueError('Cor precisa ser "w" ou "b"')
        
        lc_rei = self.achar_lc_rei(cor=cor)
        if lc_rei is None:
            return False

        horizontais =   self._verificar_horizontais(lc_rei=lc_rei, cor=cor)
        diagonais   =   self._verificar_diagonais(lc_rei=lc_rei, cor=cor)
        cavalo      =   self._verificar_cavalo(lc_rei=lc_rei, cor=cor)
        rei         =   self._verificar_rei(lc_rei=lc_rei, cor=cor)
        peao        =   self._verificar_peao(lc_rei=lc_rei, cor=cor)

        return horizontais or diagonais or cavalo or rei or peao
    

    def _verificar_horizontais(self, lc_rei: tuple[int, int], cor: str) -> bool:
        direcoes_horizontais = ((0, 1), (0, -1), (1, 0), (-1, 0))
        for direcao in direcoes_horizontais:
            l, c = lc_rei
            while True:
                l += direcao[0]
                c += direcao[1]
                if not self.lc_valido(linha=l, coluna=c):
                    break
                destino = self.matriz[l, c]
                if destino is None:
                    continue
                if destino.cor != cor and isinstance(destino, (Torre, Dama)):
                    return True
                break
        return False
    

    def _verificar_diagonais(self, lc_rei: tuple[int, int], cor: str) -> bool:
        direcoes_diagonais = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        for direcao in direcoes_diagonais:
            l, c = lc_rei
            while True:
                l += direcao[0]
                c += direcao[1]
                if not self.lc_valido(linha=l, coluna=c): break
                destino = self.matriz[l, c]
                if destino is None: continue
                if destino.cor != cor and isinstance(destino, (Bispo, Dama)):
                    return True
                break
        return False


    def _verificar_cavalo(self, lc_rei: tuple[int, int], cor: str) -> bool:
        offsets_cavalo = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1), (2, 1), (1, -2), (1, 2)]
        for offset in offsets_cavalo:
            l, c = lc_rei[0] + offset[0], lc_rei[1] + offset[1]
            if self.lc_valido(linha=l, coluna=c):
                destino = self.matriz[l, c]
                if destino and isinstance(destino, Cavalo) and destino.cor != cor:
                    return True
        return False


    def _verificar_rei(self, lc_rei: tuple[int, int], cor: str) -> bool:
        offsets_rei = [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1), (0, -1), (0, 1)]
        for offset in offsets_rei:
            l, c = lc_rei[0] + offset[0], lc_rei[1] + offset[1]
            if self.lc_valido(linha=l, coluna=c):
                destino = self.matriz[l, c]
                if destino and isinstance(destino, Rei) and destino.cor != cor:
                    return True
        return False


    def _verificar_peao(self, lc_rei: tuple[int, int], cor: str) -> bool:
        direcao = -1 if cor == 'w' else 1
        offsets_peao = [(direcao, -1), (direcao, 1)]
        for offset in offsets_peao:
            l, c = lc_rei[0] + offset[0], lc_rei[1] + offset[1]
            if self.lc_valido(linha=l, coluna=c):
                destino = self.matriz[l, c]
                if destino and isinstance(destino, Peao) and destino.cor != cor:
                    return True
        return False


    @staticmethod
    def lc_valido(linha: int, coluna: int) -> bool:
        """
        Verifica se a coordenada informada está dentro dos limites do tabuleiro.

        Returns:
            bool: True se válida, False caso contrário.
        """
        return 0 <= linha < 8 and 0 <= coluna < 8
