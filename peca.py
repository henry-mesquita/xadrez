import pygame as pg
from os.path import join
from pygame import Vector2 as vetor
import numpy as np
from enum import Enum

# POSSO USAR DEEPCOPY PRA CLONAR MATRIZ

class TipoMov(Enum):
    NORMAL = 0
    CAPTURA = 1


class Peca:
    MAPA_IMG = {
        ('w','p'): 'peao_branco.png',
        ('b','p'): 'peao_preto.png',
        ('w','r'): 'torre_branca.png',
        ('b','r'): 'torre_preta.png',
        ('w','n'): 'cavalo_branco.png',
        ('b','n'): 'cavalo_preto.png',
        ('w','b'): 'bispo_branco.png',
        ('b','b'): 'bispo_preto.png',
        ('w','q'): 'dama_branca.png',
        ('b','q'): 'dama_preta.png',
        ('w','k'): 'rei_branco.png',
        ('b','k'): 'rei_preto.png'
    }

    def __init__(
        self,
        cor: str,
        tipo: str,
        TAMANHO_PECA: int,
        posicao: vetor
    ) -> None:
        """
        Inicializa uma peça.

        Args:
            cor (str): Cor da peça ('w' para branco ou 'b' para preto).
            tipo (str): Tipo da peça ('p' para peão, 'r' para torre, 'n' para cavalo, 'b' para bispo, 'q' para dama, 'k' para rei).
            TAMANHO_PECA (int): Tamanho da peça.
            posicao (vetor): Posição da peça.
        """
        if tipo.lower() not in ('p', 'r', 'n', 'b', 'q', 'k'):
            raise ValueError("Tipo tem que estar em: ('p', 'r', 'n', 'b', 'q', 'k')")
        elif cor.lower() not in ('b', 'w'):
            raise ValueError("Cor tem que estar em: ('b', 'w')")
        
        self.cor: str    = cor.lower()
        self.tipo: str   = tipo.lower()

        self.posicao = posicao.copy() # Posição do sprite
        self.inicializar_sprite((TAMANHO_PECA, TAMANHO_PECA))
        self.rect: pg.Rect = self.sprite.get_rect(topleft=self.posicao)
    

    def __str__(self) -> str:
        """Retorna uma representação de string da peça."""
        return f'Tipo: {self.tipo} | Cor: {self.cor}'
    

    def __repr__(self) -> str:
        """Retorna uma representação de depuração da peça."""
        return f"Peca({self.tipo}, {self.cor})"
    

    @staticmethod
    def lc_valido(linha: int, coluna: int) -> bool:
        """
        Verifica se a linha e coluna são válidas.

        Returns:
            bool: True se a linha e coluna forem validas, False caso contrário.
        """
        return 0 <= linha < 8 and 0 <= coluna < 8


    def inicializar_sprite(self, dimensoes_sprite: tuple[int, int]) -> None:
        """
        Inicializa o sprite da peça.
        
        Args:
            dimensoes_sprite (tuple[int, int]): Dimensões do sprite (largura, altura).
        """
        caminho = Peca.MAPA_IMG[(str(self.cor), str(self.tipo))]
        self.imagem_original = pg.image.load(join('img', caminho)).convert_alpha()
        self.sprite = pg.transform.scale(self.imagem_original, dimensoes_sprite)
    

    def desenhar_sprite(self, tela: pg.Surface) -> None:
        """
        Desenha o sprite da peça na tela.
        
        Args:
            tela (pg.Surface): Superfície na qual é desenhado o sprite.
        """
        tela.blit(self.sprite, self.rect)
    

    def gerar_movimentos_possiveis(self, matriz: np.ndarray, lc: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Gera os movimentos possíveis para a peça selecionada de acordo com o tipo dela.

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        match self.tipo:
            case 'b': # bispo
                return self.gerar_mov_bispo(matriz, lc)
            case 'r': # torre
                return self.gerar_mov_torre(matriz, lc)
            case 'q': # dama
                return self.gerar_mov_dama(matriz, lc)
            case 'p': # peão
                return self.gerar_mov_peao(matriz, lc)
            case 'n': # cavalo
                return self.gerar_mov_cavalo(matriz, lc)
            case 'k': # rei
                return self.gerar_mov_rei(matriz, lc)

        return []


    def gerar_mov_bispo(self, matriz: np.ndarray, lc: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Gera os movimentos possíveis caso o tipo da peça seja o bispo (b).

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[tuple[int, int]] = []

        direcoes = ((-1, -1), (-1, 1), (1, -1), (1, 1))

        for direcao in direcoes:
            l = lc[0]
            c = lc[1]
            while True:
                l += direcao[0]
                c += direcao[1]

                if not self.lc_valido(l, c):
                    break
                mov.append((l, c))

        return mov


    def gerar_mov_torre(self, matriz: np.ndarray, lc: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Gera os movimentos possíveis caso o tipo da peça seja a torre (r).

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[tuple[int, int]] = []

        direcoes = ((0, 1), (0, -1), (1, 0), (-1, 0))

        for direcao in direcoes:
            l = lc[0]
            c = lc[1]
            while True:
                l += direcao[0]
                c += direcao[1]

                if not self.lc_valido(l, c):
                    break
                mov.append((l, c))
        
        return mov


    def gerar_mov_dama(self, matriz: np.ndarray, lc: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Gera os movimentos possíveis caso o tipo da peça seja a dama (q).

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        return self.gerar_mov_bispo(matriz, lc) + self.gerar_mov_torre(matriz, lc)


    def gerar_mov_peao(self, matriz: np.ndarray, lc: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Gera os movimentos possíveis caso o tipo da peça seja o peão (p).

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

    
    def gerar_mov_cavalo(self, matriz: np.ndarray, lc: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Gera os movimentos possíveis caso o tipo da peça seja o cavalo (n).

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[tuple[int, int]] = []

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
            casa_destino = (lc[0] + offset[0], lc[1] + offset[1])
            if self.lc_valido(casa_destino[0], casa_destino[1]):
                mov.append(casa_destino)

        return mov


    def gerar_mov_rei(self, matriz: np.ndarray, lc: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Gera os movimentos possíveis caso o tipo da peça seja o rei (k).

        Args:
            matriz (np.ndarray): Matriz do tabuleiro.
            lc (tuple[int, int]): Linha e coluna da peça.

        Returns:
            list: Lista de movimentos possíveis.
        """
        mov: list[tuple[int, int]] = []

        offsets_rei = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1)
        ]

        for offset in offsets_rei:
            casa_destino = (lc[0] + offset[0], lc[1] + offset[1])
            if self.lc_valido(casa_destino[0], casa_destino[1]):
                mov.append(casa_destino)

        return mov
