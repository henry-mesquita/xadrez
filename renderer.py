from constantes import *
import pygame as pg
from pecas.peca import Peca, TipoMov
from pygame import Vector2 as vetor, Surface
import numpy as np
from os.path import join
from pathlib import Path
from engine import Engine


class Renderer:
    MAPA_SPRITES = {
        'wk': 'rei_branco.png',
        'bk': 'rei_preto.png',
        'wq': 'dama_branca.png',
        'bq': 'dama_preta.png',
        'wr': 'torre_branca.png',
        'br': 'torre_preta.png',
        'wb': 'bispo_branco.png',
        'bb': 'bispo_preto.png',
        'wn': 'cavalo_branco.png',
        'bn': 'cavalo_preto.png',
        'wp': 'peao_branco.png',
        'bp': 'peao_preto.png'
    }

    BASE_DIR    = Path(__file__).resolve()
    IMG_DIR     = BASE_DIR.parent / "img"


    def __init__(self, engine: Engine) -> None:
        """
        Inicializa o renderer.
        """
        self.engine: Engine = engine

        self.inicializar_pg()

        self.click: bool = False
        self.peca_selecionada = None    # Peça que o jogador clicou
        self.drag_offset = vetor(0, 0)  # Offset da peça ao clicar (variável apenas para arrumar o offset)
        self.origem_lc: tuple[int, int] | None = None # Casa onde a peça foi clicada (linha, coluna)

        self.posicao_topleft_casas: list[vetor] = self.calcular_pos_casas()

        # flag pra não deixar gerar movimentos a cada frame
        self.flag_gerar_movimentos = True
        self.inicializar_sprites_tabuleiro(TAMANHO_PECA, TAMANHO_PECA)
    

    def inicializar_sprites_tabuleiro(self, largura: int, altura: int) -> None:
        for linha in self.engine.matriz:
            for peca in linha:
                if peca is None:
                    continue

                cor = peca.cor
                tipo = peca.tipo

                chave = f"{cor}{tipo}"
                nome_sprite = self.MAPA_SPRITES[chave]

                self.inicializar_sprite(peca, largura, altura, nome_sprite)


    def inicializar_pg(self) -> None:
        self.tela: Surface              = pg.display.set_mode(TAMANHO_TELA)
        self.surface_tabuleiro: Surface = Surface(TAM_TABULEIRO).convert()
        self.atualizar_icone()
        self.fonte = pg.font.SysFont(None, 30)
        pg.display.set_caption('Xadrez')


    def atualizar_icone(self) -> None:
        """
        Atualiza o icone da janela.
        """
        caminho: str    = join('img', 'cavalo_preto.png')
        icone: Surface  = pg.image.load(caminho).convert_alpha()
        
        pg.display.set_icon(icone)
    

    def mostrar_fps(self, fps: int) -> None:
        """
        Mostra o FPS na tela.
        """
        texto_fps = self.fonte.render(f"FPS: {int(fps)}", True, COR_TEXTO)
        self.tela.blit(texto_fps, (10, 10))


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
    def lc_para_posicao(linha: int, coluna: int) -> tuple[int, int]:
        """
        Converte linha e coluna do tabuleiro para posição em pixels (topleft).

        Returns:
            tuple[int, int]: (x, y)
        """
        x = coluna * TAM_CASA
        y = linha * TAM_CASA
        return x, y


    @staticmethod
    def lc_valido(linha: int, coluna: int) -> bool:
        """
        Verifica se a linha e coluna são válidas.

        Returns:
            bool: True se a linha e coluna forem validas, False caso contrário.
        """
        return 0 <= linha < 8 and 0 <= coluna < 8


    def desenhar_sprite(self, peca: Peca, tela: pg.Surface) -> None:
        """
        Desenha o sprite da peça na tela.
        
        Args:
            tela (pg.Surface): Superfície na qual é desenhado o sprite.
        """
        if peca.sprite is not None:
            tela.blit(peca.sprite, peca.rect)


    def inicializar_sprite(self, peca: Peca, largura: int, altura: int, nome_sprite: str) -> None:
        caminho_sprite = self.IMG_DIR / nome_sprite
        peca.sprite = pg.transform.scale(pg.image.load(caminho_sprite), (largura, altura))
        posicao_pixels = self.lc_para_posicao(peca.posicao[0], peca.posicao[1])
        peca.rect = peca.sprite.get_rect(topleft=posicao_pixels)


    def handle_drag_n_drop(self, event: pg.Event) -> None:
        """
        Trata os eventos de arrastar e soltar.
        """

        matriz_antiga = self.engine.matriz.copy()

        if self._is_left_click(event):
            self._handle_click(event)

        elif self._is_dragging(event):
            self._handle_drag(event)

        elif self._is_release(event):
            self._handle_release()
        
        if not np.array_equal(self.engine.matriz, matriz_antiga):
            self.engine.mudar_turno()


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
        self.engine.movimentos_possiveis = []

        for li in range(8):
            for co in range(8):
                p = self.engine.matriz[li, co]

                if p is not None and p.rect.collidepoint(event.pos):
                    if p.cor != self.engine.turno:
                        return
                    self._selecionar_peca(p, li, co, event.pos)
                    return


    def _selecionar_peca(self, peca, li: int, co: int, mouse_pos: tuple[int, int]) -> None:
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
            self.flag_gerar_movimentos = False
            self.engine.gerar_mov_peca(peca)


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
        """
        Processa o evento de soltar o botão do mouse.
        """
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


    def soltar_peca(self, peca) -> None:
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
        if not self.engine.lc_valido(alvo_li, alvo_co):
            idx0 = li0 * 8 + co0
            pos0 = self.posicao_topleft_casas[idx0]
            peca.rect.topleft = (int(pos0.x), int(pos0.y))
            return

        # valida movimento
        movimentos_possiveis = []
        for casa, _ in self.engine.movimentos_possiveis:
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
        ocupante = self.engine.matriz[alvo_li, alvo_co]
        if ocupante is not None and ocupante is not peca:
            self.engine.matriz[alvo_li, alvo_co] = None

        # move a peça
        self.engine.matriz[li0, co0] = None
        self.engine.matriz[alvo_li, alvo_co] = peca
        peca.posicao = (alvo_li, alvo_co)

        # atualiza posição visual
        idx = alvo_li * 8 + alvo_co
        pos = self.posicao_topleft_casas[idx]
        peca.rect.topleft = (int(pos.x), int(pos.y))

        # limpa estados
        self.engine.movimentos_possiveis    = []
        self.engine.pseudo_movimentos       = []
        self.flag_gerar_movimentos          = True

        xeque_branco = self.engine.verificar_xeque('w') # branco
        xeque_preto = self.engine.verificar_xeque('b') # preto

        print(f'Rei branco em xeque: {xeque_branco}')
        print(f'Rei preto em xeque: {xeque_preto}')


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


    def draw(self) -> None:
        self.tela.fill(PRETO)
        self.surface_tabuleiro.fill(PRETO)

        self._desenhar_tabuleiro()
        self._desenhar_movimentos()
        self._desenhar_pecas()

        self.tela.blit(self.surface_tabuleiro, TAB_POS)


    def _desenhar_tabuleiro(self) -> None:
        for linha in range(8):
            for coluna in range(8):
                cor = COR_CASAS_PARES if (linha + coluna) % 2 == 0 else COR_CASAS_IMPARES

                pg.draw.rect(
                    self.surface_tabuleiro,
                    cor,
                    pg.Rect(
                        coluna * TAM_CASA,
                        linha * TAM_CASA,
                        TAM_CASA,
                        TAM_CASA
                    )
                )


    def _desenhar_pecas(self) -> None:
        for linha in self.engine.matriz:
            for peca in linha:
                if peca not in (None, self.peca_selecionada):
                    self.desenhar_sprite(peca, self.surface_tabuleiro)

        if self.peca_selecionada is not None:
            self.desenhar_sprite(self.peca_selecionada, self.surface_tabuleiro)


    def _desenhar_movimentos(self) -> None:
        self._desenhar_movimentos_possiveis(self.surface_tabuleiro)
        # self._desenhar_pseudo_movimentos(self.surface_tabuleiro)


    def _desenhar_pseudo_movimentos(self, surf: pg.Surface) -> None:
        """
        Desenha os movimentos pseudo-legais gerados pela peça.

        Args:
            surf (pg.Surface): Superfície na qual é desenhado o destaque.
        """
        if self.engine.pseudo_movimentos is None:
            return

        for (linha, coluna) in self.engine.pseudo_movimentos:
            cor = (0, 255, 0)

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


    def _desenhar_movimentos_possiveis(self, surf: pg.Surface) -> None:
        """
        Desenha os movimentos já validados com tipo normal ou captura.
        """
        for (linha, coluna), tipo in self.engine.movimentos_possiveis:

            x = coluna * TAM_CASA
            y = linha * TAM_CASA

            if tipo == TipoMov.CAPTURA:
                pg.draw.rect(
                    surf,
                    COR_CASAS_CAPTURA,
                    pg.Rect(x, y, TAM_CASA, TAM_CASA),
                    width=3  # borda
                )
            else:
                pg.draw.circle(
                    surf,
                    COR_CASAS_MOV,
                    center=(
                        x + TAM_CASA // 2,
                        y + TAM_CASA // 2
                    ),
                    radius=RAIO_CIRCULO,
                    width=0
                )
