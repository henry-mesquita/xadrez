from constantes import *
import pygame as pg
from renderer import Renderer
from engine import Engine
from pygame import Vector2 as vetor


# TODO: Mudar os sprites das peças para 110x110
# TODO: Adicionar en passant


class Xadrez:
    def __init__(self) -> None:
        """
        Inicializa o núcleo do jogo, instanciando engine e renderer.
        """
        pg.init()
        self.clock = pg.time.Clock()
        self.engine = Engine()
        self.renderer = Renderer(engine=self.engine)
        self.running = True

        self.debug = False


    def run(self, debug: bool) -> None:
        """
        Loop principal do jogo.

        Args:
            mostrar_fps (bool): Se True, exibe o contador de frames.
        """
        self.debug = debug

        while self.running:
            self.event_loop()
            self.renderer.draw()
            
            if self.debug:
                self.renderer.mostrar_fps(fps=self.clock.get_fps())

            pg.display.flip()
            self.clock.tick(FRAMERATE)
        pg.quit()


    def event_loop(self) -> None:
        """
        Captura e encaminha eventos do sistema e entrada do usuário.
        """
        self.renderer.tela.fill(COR_FUNDO)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            movimento, peca_movida = self.handle_drag_n_drop(event=event)

            if movimento and peca_movida:
                self.processar_jogada(mov=movimento, peca=peca_movida)


    def processar_jogada(self, mov: Movimento, peca: object) -> None:
        """
        Coordena a execução da lógica e a atualização visual após um movimento.

        Args:
            mov (Movimento): Objeto com coordenadas origem e destino.
            peca (object): Instância da peça que foi movida.
        """
        sucesso = self.engine.validar_movimento(mov=mov)

        if sucesso:
            self.engine.executar_movimento(mov=mov)
            self.engine.mudar_turno()

            if self.debug:
                self.renderer.mostrar_matriz_no_terminal()
                
                print(f"Rei branco em xeque: {self.engine.verificar_xeque(cor='w')}")
                print(f"Rei preto em xeque: {self.engine.verificar_xeque(cor='b')}")

        self.renderer.sincronizar_peca_ao_tabuleiro(peca=peca)


    def handle_drag_n_drop(self, event: pg.Event) -> tuple:
        """
        Processa eventos de mouse para arrastar e soltar peças.

        Args:
            event (pg.Event): Evento do Pygame a ser processado.

        Returns:
            tuple: (Movimento ou None, Peca ou None).
        """
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            l, c = self.renderer.obter_lc_pelo_mouse()
            if self.engine.lc_valido(linha=l, coluna=c):
                p = self.engine.matriz[l, c]
                if not p or p.cor != self.engine.turno:
                    self.engine.movimentos_possiveis = []
                else:
                    self.renderer.peca_arrastada = p
                    self.renderer.origem_mov = (l, c)
                    self.renderer.drag_offset = vetor(event.pos) - vetor(p.rect.topleft)
                    self.engine.gerar_mov_peca(p=p)

        elif event.type == pg.MOUSEMOTION and self.renderer.peca_arrastada:
            self.renderer.peca_arrastada.rect.topleft = vetor(event.pos) - self.renderer.drag_offset

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.renderer.peca_arrastada:
                destino = self.renderer.obter_lc_pelo_mouse()
                mov = Movimento(origem=self.renderer.origem_mov, destino=destino)
                
                p_temp = self.renderer.peca_arrastada
                self.renderer.peca_arrastada = None
                self.renderer.origem_mov = None
                
                return mov, p_temp
        
        return None, None
