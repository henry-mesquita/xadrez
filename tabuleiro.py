from constantes import *
import pygame as pg
from peca import Peca, TipoMov
from pygame import Vector2 as vetor
import numpy as np


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
        self.turno = 'w' # w = branco | b = preto

    def mudar_turno(self) -> None:
        self.turno = 'b' if self.turno == 'w' else 'w'


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
    

    def gerar_mov_peca(self, p: Peca) -> None | list[tuple[tuple[int, int], TipoMov]]:
        """
        Gera os movimentos possíveis para a peça selecionada.

        Args:
            p (Peca): Peça selecionada.

        Returns:
            list[tuple[int, int]]: Lista de movimentos possíveis.
        """
        self.flag_gerar_movimentos = False
        self.movimentos_possiveis = p.gerar_movimentos_possiveis(self.matriz, lc=self.achar_lc_peca(p))
        # print(self.movimentos_possiveis)
        return self.movimentos_possiveis


    def handle_drag_n_drop(self, event: pg.Event) -> None:
        """
        Trata os eventos de arrastar e soltar.
        """

        matriz_antiga = self.matriz.copy()

        if self._is_left_click(event):
            self._handle_click(event)

        elif self._is_dragging(event):
            self._handle_drag(event)

        elif self._is_release(event):
            self._handle_release()
        
        if not np.array_equal(self.matriz, matriz_antiga):
            self.mudar_turno()


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

        self.flag_gerar_movimentos = True
        self.movimentos_possiveis = []

        for li in range(8):
            for co in range(8):
                p: Peca = self.matriz[li, co]

                if p is not None and p.rect.collidepoint(event.pos):
                    if p.cor != self.turno:
                        return
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
        # origem
        if self.origem_lc is None:
            origem = vetor(peca.rect.topleft)
            casa_mais_proxima = min(self.posicao_topleft_casas, key=lambda c: c.distance_to(origem))
            idx0 = self.posicao_topleft_casas.index(casa_mais_proxima)
            li0, co0 = idx0 // 8, idx0 % 8
        else:
            li0, co0 = self.origem_lc

        # alvo
        mx, my = pg.mouse.get_pos()
        alvo_li = my // TAM_CASA
        alvo_co = mx // TAM_CASA

        # alvo fora do tabuleiro
        if not self.lc_valido(alvo_li, alvo_co):
            idx0 = li0 * 8 + co0
            pos0 = self.posicao_topleft_casas[idx0]
            peca.rect.topleft = (int(pos0.x), int(pos0.y))
            return

        # valida movimento
        movimentos_possiveis = []
        for casa, _ in self.movimentos_possiveis:
            movimentos_possiveis.append(casa)
        
        
        mov_valido = (alvo_li, alvo_co) in movimentos_possiveis

        if not mov_valido:
            idx0 = li0 * 8 + co0
            pos0 = self.posicao_topleft_casas[idx0]
            peca.rect.topleft = (int(pos0.x), int(pos0.y))
            return

        # =========================
        # movimento válido
        # =========================

        # captura
        ocupante = self.matriz[alvo_li, alvo_co]
        if ocupante is not None and ocupante is not peca:
            self.matriz[alvo_li, alvo_co] = None

        # move a peça
        self.matriz[li0, co0] = None
        self.matriz[alvo_li, alvo_co] = peca

        # atualiza posição visual
        idx = alvo_li * 8 + alvo_co
        pos = self.posicao_topleft_casas[idx]
        peca.rect.topleft = (int(pos.x), int(pos.y))

        # limpa estados
        self.movimentos_possiveis = []
        self.flag_gerar_movimentos = True

        xeque_branco = self.verificar_xeque('w') # branco
        xeque_preto = self.verificar_xeque('b') # preto

        print(f'Rei branco em xeque: {xeque_branco}')
        print(f'Rei preto em xeque: {xeque_preto}')


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
                if p is not None and p.tipo == 'k' and p.cor == cor:
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

                if destino.cor != cor and destino.tipo in ('r', 'q'):
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

                if destino.cor != cor and destino.tipo in ('b', 'q'):
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

            if destino.tipo == 'n' and destino.cor != cor:
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
            
            if destino.tipo == 'k' and destino.cor != cor:
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
            
            if destino.tipo == 'p' and destino.cor != cor:
                return True
        return False


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
