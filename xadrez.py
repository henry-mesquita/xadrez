from constantes import *
import pygame as pg
from renderer import Renderer
from logic.controller import Controller, Movimento
from logic.move import lc_valido
from pygame import Vector2 as vetor
from pecas.peca import Cor, Peca
from logic.player import JogadorHumano, IAAleatoria
from random import shuffle


class Xadrez:
    """
    Orquestrador central da aplicação, coordenando controller e renderização.

    Gerencia o loop de eventos, validação de movimentos e sincronização
    entre a lógica do jogo (Controller) e a apresentação visual (Renderer).
    Funciona como ponto central de controle da aplicação.
    """
    def __init__(self) -> None:
        self.controller = Controller()
        self.running = True
        self.peca_selecionada = None
        self.jogadores = {}

        participantes = [JogadorHumano, IAAleatoria]
        self.configurar_jogadores(participantes)


    def configurar_jogadores(self, participantes: list) -> None:
        shuffle(participantes)

        self.jogadores = {
            Cor.BRANCO: participantes[0](Cor.BRANCO),
            Cor.PRETO:  participantes[1](Cor.PRETO)
        }


    def _inicializar_renderer(self) -> None:
        self.renderer = Renderer(controller=self.controller)
        self.clock = pg.time.Clock()
        
        orientacao = Cor.BRANCO
        
        for cor, jogador in self.jogadores.items():
            if isinstance(jogador, JogadorHumano):
                orientacao = cor
                break
                
        self.renderer.orientacao_tabuleiro = orientacao


    def run(self) -> None:
        """
        Loop principal do jogo.

        Args:
            mostrar_fps (bool): Se True, exibe o contador de frames.
        """
        self._inicializar_renderer()
        
        if hasattr(self, 'cor_do_humano'):
            self.renderer.orientacao_tabuleiro = self.cor_do_humano

        while self.running:
            try:
                self.event_loop()

                if not self.controller.finalizado and not self.controller.aguardando_promocao:
                    turno_atual = self.controller.state.turno
                    jogador_atual = self.jogadores[turno_atual]

                    if isinstance(jogador_atual, IAAleatoria):
                        lances_validos = self.controller.obter_todos_lances_legais_do_turno()
                        
                        lance_escolhido = jogador_atual.decidir_lance(lances_validos)
                        
                        if lance_escolhido:
                            l_orig, c_orig = lance_escolhido.origem
                            peca_ia = self.controller.state.board.matriz[l_orig, c_orig]
                            
                            if peca_ia:
                                self.processar_jogada(mov=lance_escolhido, peca=peca_ia)

                self.renderer.draw()
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
            event (pg.Event): Evento capturado pelo Pygame.
        """
        if event.type == pg.QUIT:
            self.running = False
            return

        if self.controller.aguardando_promocao:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                escolha = self.renderer.obter_escolha_promocao(event.pos)
                if escolha:
                    self.controller.promover_peao(escolha)
                    self.renderer.inicializar_sprites_tabuleiro()
                    self.renderer.sincronizar_todas_pecas()
            return

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_q:
                self.renderer.inverter_visao()
            if event.key == pg.K_z and DESFAZER_MOVIMENTO:
                self.controller.desfazer_movimento()
                self.controller.limpar_movimentos()
                self.renderer.sincronizar_todas_pecas()
        
        if not self.controller.finalizado:
            turno_atual = self.controller.state.turno
            jogador_atual = self.jogadores[turno_atual]
            
            if isinstance(jogador_atual, JogadorHumano):
                movimento, peca_movida = self.handle_input(event=event)
                if movimento and peca_movida:
                    self.processar_jogada(mov=movimento, peca=peca_movida)


    def processar_jogada(self, mov: Movimento, peca: Peca) -> None:
        """
        Processa o movimento realizado.

        Args:
            mov (Movimento): Movimento realizado pelo jogador humano.
            peca (Peca): Peca movida pelo jogador humano.
        """
        self.controller.gerar_mov_peca(peca)

        sucesso = self.controller.movimento_possivel(mov=mov)

        if sucesso:
            self.controller.executar_movimento(mov=mov)
            self.renderer.sincronizar_todas_pecas()

            self.peca_selecionada = None
            self.origem_selecionada = None
            if hasattr(self.renderer, 'peca_arrastada'):
                self.renderer.peca_arrastada = None
            if hasattr(self.renderer, 'origem_mov'):
                self.renderer.origem_mov = None
            self.controller.limpar_movimentos()

            if DEBUG and not self.controller.aguardando_promocao:
                self.renderer.mostrar_tabuleiro_no_terminal()
        else:
            self.renderer.sincronizar_peca_ao_tabuleiro(peca=peca)


    def handle_input(self, event: pg.Event) -> tuple:
        """
        Lida com cliques e arrasto de peças.

        Args:
            event (pg.Event): Evento capturado pelo Pygame.

        Returns:
            tuple: Movimento e peça movida.
        """
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            l, c = self.renderer.obter_lc_pelo_mouse()
            
            if lc_valido(l, c):
                peca = self.controller.state.board.matriz[l, c]
                turno_atual = self.controller.state.turno
                
                if self.peca_selecionada:
                    mov = Movimento(origem=self.origem_selecionada, destino=(l, c))
                    if any(
                        mov.destino == destino
                        for destino, _ in self.controller.movimentos_possiveis
                    ):
                        return mov, self.peca_selecionada
                
                if not peca or peca.cor != turno_atual:
                    self.peca_selecionada = None
                    self.origem_selecionada = None
                    self.renderer.peca_arrastada = None
                    self.controller.limpar_movimentos()
                    return None, None

                self.peca_selecionada = peca
                self.origem_selecionada = (l, c)
                
                self.controller.gerar_mov_peca(self.peca_selecionada)
                self.renderer.drag_offset = vetor(event.pos) - self.peca_selecionada.rect.topleft
                self.renderer.peca_arrastada = self.peca_selecionada
                self.renderer.origem_mov = (l, c)

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

                if destino != origem:
                    if any(
                        destino == d
                        for d, _ in self.controller.movimentos_possiveis
                    ):
                        return Movimento(origem=origem, destino=destino), peca
                    
                    self.peca_selecionada = None
                    self.origem_selecionada = None
                    self.controller.limpar_movimentos()
                
                self.renderer.sincronizar_peca_ao_tabuleiro(peca=peca)

        return None, None
