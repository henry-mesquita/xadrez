from constantes import *
import pygame as pg
from pecas.peca import Cor, Peca
from pygame import Vector2 as vetor, Surface
from pathlib import Path
from engine import Engine, TipoMov

# TODO: Promoção de peão
# TODO: Regra dos 30 lances


class Renderer:
    """
    Gerenciador de renderização visual e apresentação gráfica.

    Abstrai toda a lógica de renderização do Pygame, sincronizando posições visuais
    com o estado lógico da Engine. Responsável por desenho de sprites, tabuleiro,
    highlights de movimentos e interações visuais.
    """
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

    BASE_DIR = Path(__file__).resolve()
    IMG_DIR = BASE_DIR.parent / "img" / "png"


    def __init__(self, engine: Engine) -> None:
        """
        Inicializa o gerenciador visual do jogo.

        Args:
            engine (Engine): Instância da engine lógica.
        """
        self.engine: Engine = engine
        self._inicializar_pg()

        self.cache_sprites: dict[str, Surface] = {}
        self._carregar_cache_sprites()

        self._criar_surface_tabuleiro_estatica()

        self.peca_arrastada: Peca | None    = None
        self.drag_offset: vetor             = vetor(0, 0)
        self.orientacao_tabuleiro: Cor      = Cor.BRANCO
        
        self.inicializar_sprites_tabuleiro()


    def _carregar_cache_sprites(self) -> None:
        """
        Carrega todas as imagens de uma vez, escala e armazena no cache.
        """
        for chave, nome_arquivo in self.MAPA_SPRITES.items():
            path = self.IMG_DIR / nome_arquivo
            img = pg.image.load(path).convert_alpha()
            img_escalada = pg.transform.scale(img, (TAMANHO_PECA, TAMANHO_PECA))
            
            self.cache_sprites[chave] = img_escalada


    def _inicializar_pg(self) -> None:
        """
        Configura o ambiente do Pygame e superfícies de desenho.
        """
        self.tela = pg.display.set_mode(size=TAMANHO_TELA)
        self.surface_tabuleiro_base = Surface(size=TAM_TABULEIRO).convert()
        self.fonte = pg.font.SysFont(name=None, size=30)
        pg.display.set_caption('Xadrez')
        pg.display.set_icon(
            pg.transform.scale(
                pg.image.load(self.IMG_DIR / 'cavalo_preto.png').convert_alpha(),
                (32, 32)
            )
        )


    def inverter_visao(self):
        """
        Inverte a orientação do tabuleiro.
        """
        if self.orientacao_tabuleiro == Cor.BRANCO:
            self.orientacao_tabuleiro = Cor.PRETO
        else:
            self.orientacao_tabuleiro = Cor.BRANCO
        
        for linha in self.engine.matriz:
            for peca in linha:
                if peca:
                    self.sincronizar_peca_ao_tabuleiro(peca)


    def inicializar_sprites_tabuleiro(self) -> None:
        """
        Itera pela matriz e vincula as peças ao sprite do cache.
        """
        for linha in self.engine.matriz:
            for peca in linha:
                if peca is not None:
                    self.vincular_sprite_a_peca(peca=peca)


    def vincular_sprite_a_peca(self, peca: Peca) -> None:
        """
        Faz a peça apontar para o sprite existente no cache e define seu Rect.
        """
        chave = f"{peca.cor}{peca.tipo}"
        peca.sprite = self.cache_sprites[chave]
        
        self.sincronizar_peca_ao_tabuleiro(peca=peca)


    def sincronizar_peca_ao_tabuleiro(self, peca: Peca) -> None:
        """
        Calcula a posição visual do Rect baseada na lógica e na orientação.
        Resolve o problema do AttributeError injetando o atributo se necessário.
        """
        l_visual, c_visual = self.transformar_coords(peca.posicao[0], peca.posicao[1])
        
        x = c_visual * TAM_CASA
        y = l_visual * TAM_CASA
        
        if not hasattr(peca, 'rect') or peca.rect is None:
            peca.rect = peca.sprite.get_rect(topleft=(x, y))
        else:
            peca.rect.topleft = (x, y)


    def obter_lc_pelo_mouse(self) -> tuple[int, int]:
        """
        Converte as coordenadas X, Y do mouse em índices L, C da matriz.

        Returns:
            tuple[int, int]: (linha, coluna).
        """
        mx, my = pg.mouse.get_pos()

        c_visual = (mx - TAB_POS[0]) // TAM_CASA
        l_visual = (my - TAB_POS[1]) // TAM_CASA

        return self.transformar_coords(l_visual, c_visual)


    def transformar_coords(self, l: int, c: int) -> tuple[int, int]:
        """
        Inverte as coordenadas se a orientação for Pretas.
        """
        if self.orientacao_tabuleiro == Cor.PRETO:
            return 7 - l, 7 - c
        return l, c


    def draw(self) -> None:
        """
        Coordena o desenho do tabuleiro, destaques e peças na tela.
        """
        self._desenhar_tabuleiro(surface=self.surface_tabuleiro_base, dest=TAB_POS)
        if DEBUG:
            self._desenhar_turno(surface=self.tela)
        self._desenhar_movimentos_possiveis(surface=self.tela)
        self._desenhar_pecas(surface=self.tela)


    def _desenhar_tabuleiro(self, surface: Surface, dest: tuple[int, int]) -> None:
        """
        Desenha o tabuleiro na superficie.

        Args:
            surface (Surface): Superficie a ser desenhada.
            dest (tuple[int, int]): Posição da superficie na tela.
        """
        self.tela.blit(source=surface, dest=dest)


    def _desenhar_pecas(self, surface: Surface) -> None:
        """
        Desenha as peças na tela.

        Args:
            surface (Surface): Superficie a ser desenhada.
        """
        for linha in self.engine.matriz:
            for peca in linha:
                if peca and peca != self.peca_arrastada and hasattr(peca, 'rect'):
                    self.tela.blit(
                        source=peca.sprite,
                        dest=peca.rect.move(TAB_POS)
                    )

        if self.peca_arrastada and hasattr(self.peca_arrastada, 'rect'):
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
            l_vis, c_vis = self.transformar_coords(l, c)
            x, y = c_vis * TAM_CASA + TAB_POS[0], l_vis * TAM_CASA + TAB_POS[1]

            if tipo == TipoMov.CAPTURA:
                pg.draw.rect(
                    surface=surface,
                    color=COR_CASAS_CAPTURA,
                    rect=(x, y, TAM_CASA, TAM_CASA),
                    width=3
                )
            elif tipo == TipoMov.NORMAL:
                pg.draw.circle(
                    surface=surface,
                    color=COR_CASAS_MOV,
                    center=(x + TAM_CASA // 2, y + TAM_CASA // 2),
                    radius=RAIO_CIRCULO
                )
            elif tipo in (TipoMov.ROQUE_CURTO, TipoMov.ROQUE_LONGO):
                pg.draw.circle(
                    surface=surface,
                    color=COR_CASAS_ROQUE,
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
        Exibe uma representação visual da matriz no terminal para debug,
        respeitando a orientação do tabuleiro.
        """
        if self.orientacao_tabuleiro == Cor.BRANCO:
            indices = range(8)
        else:
            indices = range(7, -1, -1)

        print("\n   " + " ".join([f" {c} " for c in indices])) 
        print("  " + "—" * 33)

        for l in indices:
            linha_str = f"{l} |"
            
            for c in indices:
                peca = self.engine.matriz[l, c]
                
                if peca is None:
                    char = "." if (l + c) % 2 == 0 else " "
                else:
                    char = peca.tipo.upper() if peca.cor == 'w' else peca.tipo.lower()
                
                linha_str += f" {char} |"
            
            print(linha_str)
            print("  " + "—" * 33)

        orientacao_txt = "BRANCAS" if self.orientacao_tabuleiro == Cor.BRANCO else "PRETAS"
        print(f"Visão: {orientacao_txt}")
        print(f"Turno atual: {'Brancas' if self.engine.turno == 'w' else 'Pretas'}\n")
