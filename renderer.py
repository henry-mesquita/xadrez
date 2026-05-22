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
    IMG_DIR = BASE_DIR.parent / "img" / "png"


    def __init__(self, engine: Engine, mostrar_turno: bool = False) -> None:
        """
        Inicializa o gerenciador visual do jogo.

        Args:
            engine (Engine): Instância da engine lógica.
        """
        self.engine: Engine = engine
        self._inicializar_pg()
        self._criar_surface_tabuleiro_estatica()

        self.mostrar_turno: bool = mostrar_turno
        
        self.peca_arrastada = None
        self.origem_mov = None
        self.drag_offset = vetor(0, 0)
        
        self.inicializar_sprites_tabuleiro()


    def _inicializar_pg(self) -> None:
        """
        Configura o ambiente do Pygame e superfícies de desenho.
        """
        self.tela = pg.display.set_mode(size=TAMANHO_TELA)
        self.surface_tabuleiro_base = Surface(size=TAM_TABULEIRO).convert()
        self.fonte = pg.font.SysFont(name=None, size=30)
        pg.display.set_caption('Xadrez')


    def inicializar_sprites_tabuleiro(self) -> None:
        """
        Itera pela matriz da engine para carregar as imagens das peças.
        """
        for linha in self.engine.matriz:
            for peca in linha:
                if peca is not None:
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
    

    def draw(self) -> None:
        """
        Coordena o desenho do tabuleiro, destaques e peças na tela.
        """
        self.tela.blit(source=self.surface_tabuleiro_base, dest=TAB_POS)
        self._desenhar_turno(surface=self.tela)
        self._desenhar_movimentos_possiveis(surface=self.tela)
        self._desenhar_pecas(surface=self.tela)


    def _desenhar_pecas(self, surface: Surface) -> None:
        """
        Desenha as peças na tela.

        Args:
            surface (Surface): Superficie a ser desenhada.
        """
        for linha in self.engine.matriz:
            for peca in linha:
                if peca and peca != self.peca_arrastada:
                    self.tela.blit(
                        source=peca.sprite,
                        dest=peca.rect.move(TAB_POS)
                    )

        if self.peca_arrastada:
            surface.blit(
                source=self.peca_arrastada.sprite,
                dest=self.peca_arrastada.rect.move(TAB_POS)
            )


    def _desenhar_turno(self, surface: Surface) -> None:
        """
        Desenha o turno no canto inferior direito da tela.

        Args:
            surface (Surface): Superficie a ser desenhada.
        """
        turno = 'Brancas' if self.engine.turno == 'w' else 'Pretas'
        surface.blit(self.fonte.render(f'Vez das\n{turno}',
                                       True,
                                       (130, 130, 130)),
                                       (TAM_TABULEIRO[0] + 10, TAMANHO_TELA[1] // 2 - 20))


    def _criar_surface_tabuleiro_estatica(self) -> None:
        """
        Cria a superfície do tabuleiro com as casas desenhadas uma única vez.
        """
        for l in range(8):
            for c in range(8):
                cor = COR_CASAS_PARES if (l + c) % 2 == 0 else COR_CASAS_IMPARES
                pg.draw.rect(surface=self.surface_tabuleiro_base,
                             color=cor,
                             rect=(c*TAM_CASA, l*TAM_CASA, TAM_CASA, TAM_CASA))


    def _desenhar_movimentos_possiveis(self, surface: Surface) -> None:
        """
        Desenha indicadores visuais para movimentos normais e capturas.
        """
        for (l, c), tipo in self.engine.movimentos_possiveis:
            x, y = c * TAM_CASA + TAB_POS[0], l * TAM_CASA + TAB_POS[1]
            if tipo == TipoMov.CAPTURA:
                pg.draw.rect(
                    surface=surface,
                    color=COR_CASAS_CAPTURA,
                    rect=(x, y, TAM_CASA, TAM_CASA),
                    width=3
                )
            else:
                pg.draw.circle(
                    surface=surface,
                    color=COR_CASAS_MOV,
                    center=(x + TAM_CASA // 2, y + TAM_CASA // 2),
                    radius=RAIO_CIRCULO
                )


    def mostrar_fps(self, fps: float) -> None:
        """
        Renderiza o texto de FPS no canto da tela.

        Args:
            fps (float): Valor do FPS atual.
        """
        txt = self.fonte.render(f"FPS: {int(fps)}", True, COR_TEXTO)
        self.tela.blit(source=txt, dest=(TAM_TABULEIRO[0] + 10, 10))


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
    