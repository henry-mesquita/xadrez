from constantes import *
import pygame as pg
from pygame import Clock
from renderer import Renderer

class Xadrez:
    def __init__(self) -> None:
        """
        Inicializa o jogo de xadrez.
        """
        self.clock: Clock = Clock()


    def run(self, mostrar_fps: bool) -> None:
        """
        Inicializa o pygame e executa o game loop.
        """
        pg.init()
        self.renderer: Renderer     = Renderer()
        self.running: bool          = True
        while self.running:
            try:
                # PROCESSAR
                self.event_loop()

                # DESENHAR
                self.renderer.draw()

                if mostrar_fps:
                    self.renderer.mostrar_fps(self.clock.get_fps())

                # ATUALIZAR
                pg.display.flip()
                self.clock.tick(FRAMERATE)
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

            self.renderer.handle_drag_n_drop(event)
