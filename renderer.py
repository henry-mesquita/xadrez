from constantes import *
import pygame as pg
from pecas.peca import TipoMov
from pygame import Vector2 as vetor, Surface
from pathlib import Path
from engine import Engine


class Renderer:
    MAPA_SPRITES = {
        'wk': 'rei_branco.png', 'bk': 'rei_preto.png',
        'wq': 'dama_branca.png', 'bq': 'dama_preta.png',
        'wr': 'torre_branca.png', 'br': 'torre_preta.png',
        'wb': 'bispo_branco.png', 'bb': 'bispo_preto.png',
        'wn': 'cavalo_branco.png', 'bn': 'cavalo_preto.png',
        'wp': 'peao_branco.png', 'bp': 'peao_preto.png'
    }

    BASE_DIR = Path(__file__).resolve()
    IMG_DIR = BASE_DIR.parent / "img"


    def __init__(self, engine: Engine) -> None:
        """
        Inicializa o gerenciador visual do jogo.

        Args:
            engine (Engine): Instância da engine lógica.
        """
        self.engine: Engine = engine
        self.inicializar_pg()
        
        self.peca_arrastada = None
        self.origem_mov = None
        self.drag_offset = vetor(0, 0)
        
        self.inicializar_sprites_tabuleiro()


    def inicializar_pg(self) -> None:
        """
        Configura o ambiente do Pygame e superfícies de desenho.
        """
        self.tela = pg.display.set_mode(size=TAMANHO_TELA)
        self.surface_tabuleiro = Surface(size=TAM_TABULEIRO).convert()
        self.fonte = pg.font.SysFont(name=None, size=30)
        pg.display.set_caption('Xadrez')


    def inicializar_sprites_tabuleiro(self) -> None:
        """
        Itera pela matriz da engine para carregar as imagens das peças.
        """
        for linha in self.engine.matriz:
            for peca in linha:
                if peca:
                    self.carregar_sprite_peca(peca=peca)


    def carregar_sprite_peca(self, peca) -> None:
        """
        Carrega o arquivo de imagem e associa o Rect inicial à peça.

        Args:
            peca (Peca): A peça a ser carregada.
        """
        chave = f"{peca.cor}{peca.tipo}"
        path = self.IMG_DIR / self.MAPA_SPRITES[chave]
        peca.sprite = pg.transform.scale(pg.image.load(path), (TAMANHO_PECA, TAMANHO_PECA))
        self.sincronizar_peca_ao_tabuleiro(peca=peca)


    def sincronizar_peca_ao_tabuleiro(self, peca) -> None:
        """
        Alinha a posição visual (Rect) com a posição lógica da matriz.

        Args:
            peca (Peca): Peça a ser sincronizada.
        """
        x = peca.posicao[1] * TAM_CASA
        y = peca.posicao[0] * TAM_CASA
        peca.rect = peca.sprite.get_rect(topleft=(x, y))


    def obter_lc_pelo_mouse(self) -> tuple[int, int]:
        """
        Converte as coordenadas X, Y do mouse em índices L, C da matriz.

        Returns:
            tuple[int, int]: (linha, coluna).
        """
        mx, my = pg.mouse.get_pos()
        return my // TAM_CASA, mx // TAM_CASA


    def handle_drag_n_drop(self, event: pg.Event) -> tuple:
        """
        Processa eventos de mouse para arrastar e soltar peças.

        Args:
            event (pg.Event): Evento do Pygame a ser processado.

        Returns:
            tuple: (Movimento ou None, Peca ou None).
        """
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            l, c = self.obter_lc_pelo_mouse()
            if self.engine.lc_valido(linha=l, coluna=c):
                p = self.engine.matriz[l, c]
                if p and p.cor == self.engine.turno:
                    self.peca_arrastada = p
                    self.origem_mov = (l, c)
                    self.drag_offset = vetor(event.pos) - vetor(p.rect.topleft)
                    self.engine.gerar_mov_peca(p=p)
                else:
                    self.engine.movimentos_possiveis = [] # CRIME DE ARQUITETURA

        elif event.type == pg.MOUSEMOTION and self.peca_arrastada:
            self.peca_arrastada.rect.topleft = vetor(event.pos) - self.drag_offset

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.peca_arrastada:
                destino = self.obter_lc_pelo_mouse()
                mov = Movimento(origem=self.origem_mov, destino=destino)
                
                p_temp = self.peca_arrastada
                self.peca_arrastada = None
                self.origem_mov = None
                
                return mov, p_temp
        
        return None, None


    def draw(self) -> None:
        """
        Coordena o desenho do tabuleiro, destaques e peças na tela.
        """
        self.surface_tabuleiro.fill(color=PRETO)
        self._desenhar_tabuleiro()
        self._desenhar_movimentos_possiveis()
        
        for linha in self.engine.matriz:
            for peca in linha:
                if peca and peca != self.peca_arrastada:
                    self.surface_tabuleiro.blit(source=peca.sprite, dest=peca.rect)
        
        if self.peca_arrastada:
            self.surface_tabuleiro.blit(source=self.peca_arrastada.sprite, dest=self.peca_arrastada.rect)
            
        self.tela.blit(source=self.surface_tabuleiro, dest=TAB_POS)


    def _desenhar_tabuleiro(self) -> None:
        """
        Desenha o padrão xadrez de casas no tabuleiro.
        """
        for l in range(8):
            for c in range(8):
                cor = COR_CASAS_PARES if (l + c) % 2 == 0 else COR_CASAS_IMPARES
                pg.draw.rect(surface=self.surface_tabuleiro, color=cor, rect=(c*TAM_CASA, l*TAM_CASA, TAM_CASA, TAM_CASA))


    def _desenhar_movimentos_possiveis(self) -> None:
        """
        Desenha indicadores visuais para movimentos normais e capturas.
        """
        for (l, c), tipo in self.engine.movimentos_possiveis:
            x, y = c * TAM_CASA, l * TAM_CASA
            if tipo == TipoMov.CAPTURA:
                pg.draw.rect(surface=self.surface_tabuleiro, color=COR_CASAS_CAPTURA, rect=(x, y, TAM_CASA, TAM_CASA), width=3)
            else:
                pg.draw.circle(surface=self.surface_tabuleiro, color=COR_CASAS_MOV, center=(x + TAM_CASA//2, y + TAM_CASA//2), radius=RAIO_CIRCULO)


    def mostrar_fps(self, fps: float) -> None:
        """
        Renderiza o texto de FPS no canto da tela.

        Args:
            fps (float): Valor do FPS atual.
        """
        txt = self.fonte.render(f"FPS: {int(fps)}", True, COR_TEXTO)
        self.tela.blit(source=txt, dest=(10, 10))


    def mostrar_matriz_no_terminal(self) -> None:
        """
        Exibe uma representação visual da matriz no terminal para debug.
        """
        print("\n   " + " ".join([f" {c} " for c in range(8)])) 
        print("  " + "—" * 33)

        for l in range(8):
            linha_str = f"{l} |"
            for c in range(8):
                peca = self.engine.matriz[l, c]
                if peca is None:
                    char = "." if (l + c) % 2 == 0 else " "
                else:
                    char = peca.tipo.upper() if peca.cor == 'w' else peca.tipo.lower()
                linha_str += f" {char} |"
            print(linha_str)
            print("  " + "—" * 33)
        print(f"Turno atual: {'Brancas' if self.engine.turno == 'w' else 'Pretas'}\n")
    