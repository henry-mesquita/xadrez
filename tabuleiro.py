from constantes import *
import pygame as pg
from peca import Peca, TipoMov
from pygame import Vector2 as vetor
from dataclasses import dataclass
import numpy as np


@dataclass
class Lance: # Não está sendo utilizada ainda
    casa_inicial: tuple[int, int]
    casa_final: tuple[int, int]


class Tabuleiro:
    def __init__(self) -> None:
        """
        Inicializa o tabuleiro.
        """
        self.click: bool = False
        self.peca_selecionada = None    # Peça que o jogador clicou
        self.drag_offset = vetor(0, 0)  # Offset da peça ao clicar
        self.origem_lc: tuple[int, int] | None = None # Casa onde a peça foi clicada (linha, coluna)

        self.matriz: np.ndarray = np.full((8, 8), None, dtype=object) # Matriz do tabuleiro
        self.posicao_topleft_casas: list[vetor] = self.calcular_pos_casas()

        # flag pra não deixar gerar movimentos a cada frame
        self.flag_gerar_movimentos = True
        self.movimentos_possiveis: list[tuple[int, int]] = [] # Movimentos já gerados ao clicar na peça

        self.carregar_posicao_fen(fen=FEN_INICIAL)


    # def carregar_posicao_inicial(self) -> None:
    #     """
    #     Carrega a posição inicial do tabuleiro de forma arcaica.
    #     (Função feita apenas para testar a atribuição na matriz)
    #     """
    #     self.matriz[0][0] = Peca('b', 'r', TAMANHO_PECA, self.posicao_topleft_casas[0])
    #     self.matriz[0][1] = Peca('b', 'n', TAMANHO_PECA, self.posicao_topleft_casas[1])
    #     self.matriz[0][2] = Peca('b', 'b', TAMANHO_PECA, self.posicao_topleft_casas[2])
    #     self.matriz[0][3] = Peca('b', 'q', TAMANHO_PECA, self.posicao_topleft_casas[3])
    #     self.matriz[0][4] = Peca('b', 'k', TAMANHO_PECA, self.posicao_topleft_casas[4])
    #     self.matriz[0][5] = Peca('b', 'b', TAMANHO_PECA, self.posicao_topleft_casas[5])
    #     self.matriz[0][6] = Peca('b', 'n', TAMANHO_PECA, self.posicao_topleft_casas[6])
    #     self.matriz[0][7] = Peca('b', 'r', TAMANHO_PECA, self.posicao_topleft_casas[7])

    #     self.matriz[1][0] = Peca('b', 'p', TAMANHO_PECA, self.posicao_topleft_casas[8])
    #     self.matriz[1][1] = Peca('b', 'p', TAMANHO_PECA, self.posicao_topleft_casas[9])
    #     self.matriz[1][2] = Peca('b', 'p', TAMANHO_PECA, self.posicao_topleft_casas[10])
    #     self.matriz[1][3] = Peca('b', 'p', TAMANHO_PECA, self.posicao_topleft_casas[11])
    #     self.matriz[1][4] = Peca('b', 'p', TAMANHO_PECA, self.posicao_topleft_casas[12])
    #     self.matriz[1][5] = Peca('b', 'p', TAMANHO_PECA, self.posicao_topleft_casas[13])
    #     self.matriz[1][6] = Peca('b', 'p', TAMANHO_PECA, self.posicao_topleft_casas[14])
    #     self.matriz[1][7] = Peca('b', 'p', TAMANHO_PECA, self.posicao_topleft_casas[15])
        
    #     self.matriz[6][0] = Peca('w', 'p', TAMANHO_PECA, self.posicao_topleft_casas[48])
    #     self.matriz[6][1] = Peca('w', 'p', TAMANHO_PECA, self.posicao_topleft_casas[49])
    #     self.matriz[6][2] = Peca('w', 'p', TAMANHO_PECA, self.posicao_topleft_casas[50])
    #     self.matriz[6][3] = Peca('w', 'p', TAMANHO_PECA, self.posicao_topleft_casas[51])
    #     self.matriz[6][4] = Peca('w', 'p', TAMANHO_PECA, self.posicao_topleft_casas[52])
    #     self.matriz[6][5] = Peca('w', 'p', TAMANHO_PECA, self.posicao_topleft_casas[53])
    #     self.matriz[6][6] = Peca('w', 'p', TAMANHO_PECA, self.posicao_topleft_casas[54])
    #     self.matriz[6][7] = Peca('w', 'p', TAMANHO_PECA, self.posicao_topleft_casas[55])

    #     self.matriz[7][0] = Peca('w', 'r', TAMANHO_PECA, self.posicao_topleft_casas[56])
    #     self.matriz[7][1] = Peca('w', 'n', TAMANHO_PECA, self.posicao_topleft_casas[57])
    #     self.matriz[7][2] = Peca('w', 'b', TAMANHO_PECA, self.posicao_topleft_casas[58])
    #     self.matriz[7][3] = Peca('w', 'q', TAMANHO_PECA, self.posicao_topleft_casas[59])
    #     self.matriz[7][4] = Peca('w', 'k', TAMANHO_PECA, self.posicao_topleft_casas[60])
    #     self.matriz[7][5] = Peca('w', 'b', TAMANHO_PECA, self.posicao_topleft_casas[61])
    #     self.matriz[7][6] = Peca('w', 'n', TAMANHO_PECA, self.posicao_topleft_casas[62])
    #     self.matriz[7][7] = Peca('w', 'r', TAMANHO_PECA, self.posicao_topleft_casas[63])


    # @staticmethod
    # def indice_para_lc(idx: int) -> tuple[int, int]:
    #     """
    #     Converte o indice da matriz para linha e coluna.

    #     Returns:
    #         tuple[int, int]: linha e coluna
    #     """
    #     return int(idx // 8, idx % 8)


    # @staticmethod
    # def lc_para_indice(linha: int, coluna: int) -> int:
    #     """
    #     Converte linha e coluna para o indice da matriz.

    #     Returns:
    #         int: Indice da matriz
    #     """
    #     return int(linha * 8 + coluna)


    @staticmethod
    def posicao_para_lc(topleft: tuple[int, int]) -> tuple[int, int]:
        """
        Converte a posição do canto superior esquerdo (topleft) da casa para linha e coluna.

        Returns:
            tuple[int, int]: linha e coluna
        """
        x, y = topleft
        coluna = x // TAM_CASA
        linha = y // TAM_CASA
        return int(linha), int(coluna)


    @staticmethod
    def lc_valido(linha: int, coluna: int) -> bool:
        """
        Verifica se a linha e coluna são válidas.

        Returns:
            bool: True se a linha e coluna forem validas, False caso contrário.
        """
        return 0 <= linha < 8 and 0 <= coluna < 8


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

                    idx = i * 8 + j
                    pos = self.posicao_topleft_casas[idx]

                    self.matriz[i, j] = Peca(
                        cor=cor,
                        tipo=tipo,
                        TAMANHO_PECA=TAMANHO_PECA,
                        posicao=pos
                    )

                    j += 1

            if j != 8:
                raise ValueError("FEN inválida: rank não fecha em 8 colunas.")


    def achar_lc_peca(self, peca: Peca) -> tuple[int, int] | None:
        """
        Encontra a linha e coluna da peça na matriz.

        Returns:
            tuple[int, int] | None: Linha e coluna da peça, ou None se a peça não for encontrada.
        """
        for li in range(8):
            for co in range(8):
                if self.matriz[li, co] == peca:
                    return (li, co)
    

    def gerar_mov_peca(self, p: Peca) -> None | list[tuple[int, int]]:
        """
        Gera os movimentos possíveis para a peça selecionada.

        Args:
            p (Peca): Peça selecionada.

        Returns:
            list[tuple[int, int]]: Lista de movimentos possíveis.
        """
        self.flag_gerar_movimentos = False
        self.movimentos_possiveis = p.gerar_movimentos_possiveis(self.matriz, lc=self.achar_lc_peca(p))
        print(self.movimentos_possiveis)
        return self.movimentos_possiveis


    def handle_drag_n_drop(self, event: pg.Event) -> None:
        """
        Trata os eventos de arrastar e soltar.
        """
        if self._is_left_click(event):
            self._handle_click(event)

        elif self._is_dragging(event):
            self._handle_drag(event)

        elif self._is_release(event):
            self._handle_release()


    def _is_left_click(self, event: pg.Event) -> bool:
        """
        Verifica se o tipo do evento é o botão esquerdo do mouse foi clicado.
        
        args:
            event (pg.Event): Evento do Pygame.
        
        returns:
            bool: True se o botão esquerdo do mouse foi clicado, False caso contrário.
        """
        return event.type == pg.MOUSEBUTTONDOWN and event.button == 1


    def _is_dragging(self, event: pg.Event) -> bool:
        """
        Verifica se o mouse está sendo arrastado.
        
        args:
            event (pg.Event): Evento do Pygame.
        
        returns:
            bool: True se o mouse estiver sendo arrastado, False caso contrário.
        """
        return (
            event.type == pg.MOUSEMOTION and
            self.click and
            self.peca_selecionada is not None
        )


    def _is_release(self, event: pg.Event) -> bool:
        """
        Verifica se o botão esquerdo do mouse foi solto.
        
        args:
            event (pg.Event): Evento do Pygame.
        
        returns:
            bool: True se o botão esquerdo do mouse foi solto, False caso contrário.
        """
        return event.type == pg.MOUSEBUTTONUP and event.button == 1


    def _handle_click(self, event: pg.Event) -> None:
        """
        Trata o clique do mouse.
        
        args:
            event (pg.Event): Evento do Pygame.
        """
        self.click = False
        self.peca_selecionada = None
        self.origem_lc = None

        for li in range(8):
            for co in range(8):
                p = self.matriz[li, co]

                if p is not None and p.rect.collidepoint(event.pos):
                    self._selecionar_peca(p, li, co, event.pos)
                    return


    def _selecionar_peca(self, peca: Peca, li: int, co: int, mouse_pos: tuple[int, int]) -> None:
        """
        Seleciona a peça clicada.
        
        args:
            peca (Peca): Peça selecionada.
            li (int): Linha da peça.
            co (int): Coluna da peça.
            mouse_pos (tuple[int, int]): Posição do mouse.
        """
        self.peca_selecionada = peca
        self.origem_lc = (li, co)
        self.click = True

        self.drag_offset = vetor(mouse_pos) - vetor(peca.rect.topleft)

        if self.flag_gerar_movimentos:
            self.gerar_mov_peca(peca)


    def _handle_drag(self, event: pg.Event) -> None:
        """
        Trata o arrastar da peça.
        
        args:
            event (pg.Event): Evento do Pygame.
        """
        novo_topleft = vetor(event.pos) - self.drag_offset
        self.peca_selecionada.rect.topleft = (
            int(novo_topleft.x),
            int(novo_topleft.y)
        )


    def _handle_release(self) -> None:
        if self.peca_selecionada is not None:
            self.soltar_peca(self.peca_selecionada)

        self._reset_drag_state()


    def _reset_drag_state(self) -> None:
        """
        Reseta o estado do arrastar.
        """
        self.click = False
        self.peca_selecionada = None
        self.origem_lc = None


    def soltar_peca(self, peca: Peca) -> None:
        """
        Solta a peça na casa alvo caso possível.

        Args:
            peca (Peca): Peça a ser solta.
        """
        if self.origem_lc is None:
            origem = vetor(peca.rect.topleft)
            casa_mais_proxima = min(self.posicao_topleft_casas, key=lambda c: c.distance_to(origem))
            idx0 = self.posicao_topleft_casas.index(casa_mais_proxima)
            li0, co0 = idx0 // 8, idx0 % 8
        else:
            li0, co0 = self.origem_lc

        mx, my = pg.mouse.get_pos()
        alvo_li = my // TAM_CASA
        alvo_co = mx // TAM_CASA

        if not self.lc_valido(alvo_li, alvo_co):
            idx0 = li0 * 8 + co0
            pos0 = self.posicao_topleft_casas[idx0]
            peca.rect.topleft = (int(pos0.x), int(pos0.y))
            return

        # captura
        ocupante = self.matriz[alvo_li, alvo_co]
        if ocupante is not None and ocupante is not peca:
            self.matriz[alvo_li][alvo_co] = None

        # atualização casa inicial e casa alvo
        self.matriz[li0, co0] = None
        self.matriz[alvo_li, alvo_co] = peca

        idx = alvo_li * 8 + alvo_co
        pos = self.posicao_topleft_casas[idx]
        peca.rect.topleft = (int(pos.x), int(pos.y))

        self.movimentos_possiveis = []
        self.flag_gerar_movimentos = True


    def calcular_pos_casas(self) -> list[vetor]:
        """
        Calcula as posicoes das casas do tabuleiro.

        Returns:
            list[vetor]: Lista de posicoes das casas do tabuleiro.
        """
        l = []
        y = 0
        for _ in range(8):
            x = 0
            for _ in range(8):
                l.append(vetor(x, y))
                x += TAM_CASA
            y += TAM_CASA
        return l


    def desenhar(self, surf: pg.Surface) -> None:
        """
        Desenha o tabuleiro e as peças na superficie (pygame.Surface).

        Args:
            surf (pygame.Surface): Superfície na qual é desenhado o tabuleiro.
        """
        for linha in range(8):
            for coluna in range(8):
                cor = COR_CASAS_PARES if (linha + coluna) % 2 == 0 else COR_CASAS_IMPARES

                flag_movimento = False
                if self.peca_selecionada is not None:
                    if (linha, coluna) in self.movimentos_possiveis:
                        flag_movimento = True

                pg.draw.rect(
                    surf,
                    cor,
                    pg.Rect(
                        coluna * TAM_CASA,
                        linha * TAM_CASA,
                        TAM_CASA,
                        TAM_CASA
                    )
                )

        for linha in self.matriz:
            for peca in linha:
                if peca not in (None, self.peca_selecionada):
                    peca.desenhar_sprite(surf)

        self.desenhar_mov_highlights(surf)

        if self.peca_selecionada is not None:
            self.peca_selecionada.desenhar_sprite(surf)


    def desenhar_mov_highlights(self, surf: pg.Surface) -> None:
        for (linha, coluna), tipo in self.movimentos_possiveis:
            if tipo == TipoMov.CAPTURA:
                cor = COR_CASAS_CAPTURA
            else:
                cor = COR_CASAS_MOV

            pg.draw.circle(
                surf,
                cor,
                center=(
                    coluna * TAM_CASA + TAM_CASA // 2,
                    linha * TAM_CASA + TAM_CASA // 2
                ),
                radius=RAIO_CIRCULO,
                width=0
            )
