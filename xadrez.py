from constantes import *
import pygame as pg
from renderer import Renderer
from engine import Engine, Movimento
from pygame import Vector2 as vetor
from pecas.peca import Cor, Peca


class Xadrez:
    """
    Orquestrador central da aplicação, coordenando engine e renderização.

    Gerencia o loop de eventos, validação de movimentos e sincronização
    entre a lógica do jogo (Engine) e a apresentação visual (Renderer).
    Funciona como ponto central de controle da aplicação.
    """
    def __init__(self) -> None:
        """
        Inicializa o núcleo do jogo, instanciando engine e renderer.
        """
        self.engine = Engine()
        self.running = True
        self.peca_selecionada = None


    def _inicializar_renderer(self) -> None:
        """
        Inicializa o gerenciador visual do jogo.
        """
        self.renderer = Renderer(engine=self.engine)
        self.clock = pg.time.Clock()


    def run(self) -> None:
        """
        Loop principal do jogo.

        Args:
            mostrar_fps (bool): Se True, exibe o contador de frames.
        """
        self._inicializar_renderer()
        while self.running:
            try:
                self.event_loop()
                self.renderer.draw()
                
                if DEBUG:
                    self.renderer.mostrar_fps(
                        fps=self.clock.get_fps()
                    )

                pg.display.flip()
                self.clock.tick(FRAMERATE)
            except KeyboardInterrupt:
                self.running = False
                print('Jogo finalizado pelo teclado.')
        pg.quit()


    def event_loop(self) -> None:
        """
        Captura e encaminha eventos do sistema e entrada do usuário.
        """
        self.renderer.tela.fill(COR_FUNDO)
        for event in pg.event.get():
            self._handle_events(event=event)


    def _handle_events(self, event: pg.Event) -> None:
        """
        Lida com os eventos dentro do loop.

        Args:
            event (pg.Event): Objeto de evento do Pygame.
        """
        if event.type == pg.QUIT:
            self.running = False
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_q:
                self.renderer.inverter_visao()
                if DEBUG:
                    self.renderer.mostrar_tabuleiro_no_terminal()

        if not self.engine.finalizado:
            movimento, peca_movida = self.handle_input(event=event)

            if movimento and peca_movida:
                self.processar_jogada(
                    mov=movimento,
                    peca=peca_movida
                )


    def processar_jogada(self, mov: Movimento, peca: Peca) -> None:
        """
        Coordena a execução da lógica e a atualização visual após um movimento.

        Args:
            mov (Movimento): Objeto com coordenadas origem e destino.
            peca (object): Instância da peça que foi movida.
        """
        sucesso = self.engine.movimento_possivel(mov=mov)

        if sucesso:
            self.engine.executar_movimento(mov=mov)

            self.renderer.sincronizar_todas_pecas()

            if DEBUG:
                self.renderer.mostrar_tabuleiro_no_terminal()

                print(
                    f"""Rei branco em xeque: {
                        self.engine.verificar_xeque(cor=Cor.BRANCO)
                    }"""
                )
                print(
                    f"""Rei preto em xeque: {
                        self.engine.verificar_xeque(cor=Cor.PRETO)
                    }"""
                )
        else:
            self.renderer.sincronizar_peca_ao_tabuleiro(peca=peca)


    def handle_input(self, event: pg.Event) -> tuple:
        """
        Captura e encaminha eventos do sistema e entrada do usuário.

        DRAG N DROP + DROP AND DROP

        Args:
            event (pg.Event): Objeto contendo o evento capturado.

        Returns:
            Movimento: Objeto contendo as coordenadas de origem e destino.
        """
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            l, c = self.renderer.obter_lc_pelo_mouse()

            if not self.engine.lc_valido(l, c):
                return None, None

            peca = self.engine.matriz[l, c]

            if peca and peca.cor == self.engine.turno:
                mesma_peca = (
                    self.peca_selecionada == peca
                )

                self.peca_selecionada = peca
                self.origem_selecionada = (l, c)

                self.engine.gerar_mov_peca(peca)

                self.renderer.peca_arrastada = peca
                self.renderer.origem_mov = (l, c)
                self.renderer.drag_offset = (
                    vetor(event.pos) - vetor(peca.rect.topleft)
                )

                if mesma_peca:
                    return None, None

                return None, None

            if self.peca_selecionada:
                mov = Movimento(
                    origem=self.origem_selecionada,
                    destino=(l, c)
                )

                destino_valido = any(
                    mov.destino == destino
                    for destino, _ in self.engine.movimentos_possiveis
                )

                if not destino_valido:
                    self.peca_selecionada = None
                    self.origem_selecionada = None

                    self.engine.limpar_movimentos()
                    return None, None

                return mov, self.peca_selecionada

            self.engine.limpar_movimentos()

        elif event.type == pg.MOUSEMOTION:
            if self.renderer.peca_arrastada:
                self.renderer.peca_arrastada.rect.topleft = (
                    vetor(event.pos) - self.renderer.drag_offset
                )

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.renderer.peca_arrastada:
                destino = self.renderer.obter_lc_pelo_mouse()
                origem = self.renderer.origem_mov
                peca = self.renderer.peca_arrastada

                self.renderer.peca_arrastada = None
                self.renderer.origem_mov = None

                if destino == origem:
                    self.renderer.sincronizar_peca_ao_tabuleiro(
                        peca=peca
                    )

                    return None, None

                mov = Movimento(
                    origem=origem,
                    destino=destino
                )

                return mov, peca

        return None, None
