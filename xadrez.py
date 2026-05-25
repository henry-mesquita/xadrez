from constantes import *
import pygame as pg
from renderer import Renderer
from engine import Engine
from pygame import Vector2 as vetor
from pecas.peca import Cor

# TODO: Adicionar en passant


class Xadrez:
    """
    Orquestrador central da aplicação, coordenando engine e renderização.

    Gerencia o loop de eventos, validação de movimentos e sincronização entre
    a lógica do jogo (Engine) e a apresentação visual (Renderer). Funciona como
    ponto central de controle da aplicação.
    """
    def __init__(self) -> None:
        """
        Inicializa o núcleo do jogo, instanciando engine e renderer.
        """
        pg.init()
        self.clock = pg.time.Clock()
        self.engine = Engine()
        self.renderer = Renderer(engine=self.engine)
        self.running = True
        self.peca_selecionada = None


    def run(self) -> None:
        """
        Loop principal do jogo.

        Args:
            mostrar_fps (bool): Se True, exibe o contador de frames.
        """
        while self.running:
            self.event_loop()
            self.renderer.draw()
            
            if DEBUG:
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

            if not self.engine.finalizado:
                movimento, peca_movida = self.handle_input(event=event)

                if movimento and peca_movida:
                    self.processar_jogada(mov=movimento, peca=peca_movida)


    def processar_jogada(self, mov: Movimento, peca: object) -> None:
        """
        Coordena a execução da lógica e a atualização visual após um movimento.

        Args:
            mov (Movimento): Objeto com coordenadas origem e destino.
            peca (object): Instância da peça que foi movida.
        """
        sucesso = self.engine.movimento_possivel(mov=mov)

        if sucesso:
            self.engine.executar_movimento(mov=mov)

            for linha in self.engine.matriz:
                for p in linha:
                    if p:
                        self.renderer.sincronizar_peca_ao_tabuleiro(peca=p)

            if DEBUG:
                self.renderer.mostrar_matriz_no_terminal()
                
                print(f"Rei branco em xeque: {self.engine.verificar_xeque(cor=Cor.BRANCO)}")
                print(f"Rei preto em xeque: {self.engine.verificar_xeque(cor=Cor.PRETO)}")
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
                    vetor(event.pos)
                    - self.renderer.drag_offset
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
