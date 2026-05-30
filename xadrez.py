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
        Captura e encaminha eventos do sistema e entrada do usuário.

        Args:
            event (pg.Event): Evento capturado pelo pygame.
        """
        if event.type == pg.QUIT:
            self.running = False
            return
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_z:
                self.engine.desfazer_movimento()
                self.renderer.sincronizar_todas_pecas()

        if self.engine.aguardando_promocao:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                escolha = self.renderer.obter_escolha_promocao(event.pos)
                if escolha:
                    self.engine.promover_peao(escolha)
                    self.renderer.inicializar_sprites_tabuleiro()
                    self.renderer.sincronizar_todas_pecas()

                    if DEBUG:
                        xeque_branco = self.engine.verificar_xeque(cor=Cor.BRANCO)
                        xeque_preto = self.engine.verificar_xeque(cor=Cor.PRETO)
                        self.renderer.mostrar_tabuleiro_no_terminal()
                        print(f"Rei branco em xeque: {xeque_branco}")
                        print(f"Rei preto em xeque: {xeque_preto}")
            return

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_q:
                self.renderer.inverter_visao()
        
        if not self.engine.finalizado:
            movimento, peca_movida = self.handle_input(event=event)
            if movimento and peca_movida:
                self.processar_jogada(mov=movimento, peca=peca_movida)


    def processar_jogada(self, mov: Movimento, peca: Peca) -> None:
        """
        Processa o movimento realizado pelo jogador.

        Args:
            mov (Movimento): O movimento realizado pelo jogador.
            peca (Peca): A peça movida.
        """
        sucesso = self.engine.movimento_possivel(mov=mov)

        if sucesso:
            self.engine.executar_movimento(mov=mov)
            self.renderer.sincronizar_todas_pecas()
            
            self.peca_selecionada = None
            self.origem_selecionada = None

            if DEBUG and not self.engine.aguardando_promocao:
                self.renderer.mostrar_tabuleiro_no_terminal()
                print(f"Rei branco em xeque: {self.engine.verificar_xeque(cor=Cor.BRANCO)}")
                print(f"Rei preto em xeque: {self.engine.verificar_xeque(cor=Cor.PRETO)}")
        else:
            self.renderer.sincronizar_peca_ao_tabuleiro(peca=peca)


    def handle_input(self, event: pg.Event) -> tuple:
        """
        Lida com cliques e arrasto de peças.

        Args:
            event (pg.Event): O evento capturado pelo pygame.
        """
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            l, c = self.renderer.obter_lc_pelo_mouse()

            if not self.engine.lc_valido(l, c):
                return None, None

            peca_clicada = self.engine.matriz[l, c]

            if peca_clicada and peca_clicada.cor == self.engine.turno:
                if self.peca_selecionada == peca_clicada:
                    self.peca_selecionada = None
                    self.origem_selecionada = None
                    self.engine.limpar_movimentos()
                    return None, None

                self.peca_selecionada = peca_clicada
                self.origem_selecionada = (l, c)
                self.engine.gerar_mov_peca(peca_clicada)

                self.renderer.peca_arrastada = peca_clicada
                self.renderer.origem_mov = (l, c)
                self.renderer.drag_offset = vetor(event.pos) - vetor(peca_clicada.rect.topleft)
                return None, None

            if self.peca_selecionada:
                mov = Movimento(origem=self.origem_selecionada, destino=(l, c))
                
                if any(
                    mov.destino == destino
                    for destino, _ in self.engine.movimentos_possiveis
                ):
                    return mov, self.peca_selecionada
                
                self.peca_selecionada = None
                self.origem_selecionada = None
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
                    self.renderer.sincronizar_peca_ao_tabuleiro(peca=peca)
                    return None, None

                return Movimento(origem=origem, destino=destino), peca

        return None, None
