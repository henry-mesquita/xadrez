import pygame as pg
from tabuleiro import Tabuleiro
from constantes import *
from os.path import join
from pygame import Surface, Clock

class Xadrez:
    def __init__(self) -> None:
        """
        Inicializa o jogo de xadrez.
        """
        self.tela: Surface              = pg.display.set_mode(TAMANHO_TELA)
        self.surface_tabuleiro: Surface = Surface(TAM_TABULEIRO).convert()
        self.clock: Clock               = Clock()
        self.tabuleiro: Tabuleiro       = Tabuleiro()

        pg.display.set_caption('Xadrez')
        self.atualizar_icone()
    
    def atualizar_icone(self) -> None:
        """
        Atualiza o icone da janela.
        """
        caminho: str    = join('img', 'cavalo_preto.png')
        icone: Surface  = pg.image.load(caminho).convert_alpha()
        
        pg.display.set_icon(icone)
    
    def run(self) -> None:
        """
        Inicializa o pygame e executa o game loop.
        """
        self.running: bool = True

        pg.init()
        while self.running:
            try:
                # PROCESSAR
                self.event_loop()

                # DESENHAR
                self.surface_tabuleiro.fill((0, 0, 0))
                self.tabuleiro.desenhar(self.surface_tabuleiro)
                self.tela.fill(PRETO)

                self.tela.blit(self.surface_tabuleiro, TAB_POS)

                # ATUALIZAR
                self.clock.tick(FRAMERATE)
                pg.display.flip()
            except KeyboardInterrupt:
                self.running = False
        pg.quit()

    def event_loop(self) -> None:
        """
        Loop de eventos.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            self.tabuleiro.handle_drag_n_drop(event)
