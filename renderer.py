from constantes import *
import pygame as pg
from pecas.peca import Cor, Peca
from pygame import Vector2 as vetor, Surface
from pathlib import Path
from engine import Engine, TipoMov


class Renderer:
    """
    Gerenciador de renderização visual e apresentação gráfica.

    Abstrai toda a lógica de renderização do Pygame,
    esincronizando posições visuais com o estado lógico da Engine.
    Responsável por de sprites e input handling.
    """
    BASE_DIR = Path(__file__).resolve()
    IMG_DIR = (
        BASE_DIR.parent /
        "img" /
        "png" /
        ESTILO_PECAS
    )

    def __init__(self, engine: Engine) -> None:
        """
        Inicializa o gerenciador visual do jogo.

        Args:
            engine (Engine): Instância da engine lógica.
        """
        # Engine
        self.engine: Engine = engine

        # Render
        self._inicializar_pg()
        self.peca_arrastada: Peca | None = None
        self.cache_sprites: dict[str, Surface] = {}
        self._carregar_cache_sprites()
        self._criar_surface_tabuleiro_estatica()
        self.drag_offset: vetor = vetor(0, 0)
        self.orientacao_tabuleiro: Cor = Cor.BRANCO
        self.inicializar_sprites_tabuleiro()

        self.menu_promocao_rects = {}


    def _inicializar_pg(self) -> None:
        """
        Configura o ambiente do Pygame e superfícies de desenho.
        """
        pg.init()
        self.tela = pg.display.set_mode(size=TAMANHO_TELA)
        self.surf_base_tabuleiro = Surface(size=TAM_TABULEIRO).convert()
        self.fonte = pg.font.SysFont(name=None, size=30)
        pg.display.set_caption('chess.py')

        icon_path = icon_path = self.IMG_DIR / 'bN.png'

        pg.display.set_icon(
            pg.transform.scale(
                surface=pg.image.load(icon_path).convert_alpha(),
                size=(32, 32)
            )
        )


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
        Faz a peça apontar ao sprite correspondente no cache.

        Args:
            peca (Peca): Instância da peça.
        """
        chave = f"{peca.cor}{peca.tipo.value}"
        peca.sprite = self.cache_sprites[chave]
        
        self.sincronizar_peca_ao_tabuleiro(peca=peca)


    def sincronizar_peca_ao_tabuleiro(self, peca: Peca) -> None:
        """
        Calcula a posição visual do Rect baseada na lógica e na orientação.

        Args:
            peca (Peca): Instância da peça.
        """
        l_visual, c_visual = self.transformar_coords(
            l=peca.posicao[0],
            c=peca.posicao[1]
        )
        
        x: int = c_visual * TAM_CASA
        y: int = l_visual * TAM_CASA

        if not hasattr(peca, 'rect') or peca.rect is None:
            peca.rect = peca.sprite.get_rect(topleft=(x, y))
        else:
            peca.rect.topleft = (x, y)

    def sincronizar_todas_pecas(self) -> None:
        for linha in self.engine.matriz:
            for peca in linha:
                if peca is not None:
                    self.sincronizar_peca_ao_tabuleiro(peca=peca)


    def _carregar_cache_sprites(self) -> None:
        """
        Carrega todos os sprites do estilo selecionado.
        """
        for path in self.IMG_DIR.glob("*.png"):
            chave = path.stem.lower()

            img = pg.image.load(path).convert_alpha()

            img_escalada = pg.transform.scale(
                surface=img,
                size=(TAMANHO_PECA, TAMANHO_PECA)
            )

            self.cache_sprites[chave] = img_escalada


    def inverter_visao(self):
        """
        Inverte a orientação do tabuleiro (apenas visual).
        """
        if self.orientacao_tabuleiro == Cor.BRANCO:
            self.orientacao_tabuleiro = Cor.PRETO
        else:
            self.orientacao_tabuleiro = Cor.BRANCO

        # Força a sincronização de todas as peças
        for linha in self.engine.matriz:
            for peca in linha:
                if peca:
                    self.sincronizar_peca_ao_tabuleiro(peca)


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
        Inverte as coordenadas se a orientação for pretas.

        Args:
            l (int): Linha.
            c (int): Coluna.

        Returns:
            tuple[int, int]: (linha, coluna).
        """
        if self.orientacao_tabuleiro == Cor.PRETO:
            return 7 - l, 7 - c
        return l, c


    def draw(self) -> None:
        """
        Coordena o desenho do tabuleiro, destaques e peças na tela.
        """
        self._desenhar_tabuleiro(
            surface=self.surf_base_tabuleiro,
            dest=TAB_POS
        )
        self._desenhar_xeque()
        self._desenhar_movimentos_possiveis(surface=self.tela)
        self._desenhar_pecas(surface=self.tela)

        if self.engine.aguardando_promocao:
            self.desenhar_menu_promocao()

        if DEBUG:
            self._desenhar_turno(surface=self.tela)


    def desenhar_menu_promocao(self) -> None:
        """
        Desenha o menu de escolha de promoção.
        """
        largura = 400
        altura = 100

        x = TAMANHO_TELA[0] // 2 - largura // 2
        y = TAMANHO_TELA[1] // 2 - altura // 2

        fundo = pg.Rect(x, y, largura, altura)

        pg.draw.rect(
            surface=self.tela,
            color=(40, 40, 40),
            rect=fundo,
            border_radius=10
        )

        pecas = ['q', 'r', 'b', 'n']

        self.menu_promocao_rects.clear()

        for i, tipo in enumerate(pecas):
            rect = pg.Rect(
                x + 20 + i * 90,
                y + 20,
                70,
                70
            )

            pg.draw.rect(
                surface=self.tela,
                color=(200, 200, 200),
                rect=rect,
                border_radius=8
            )

            cor = self.engine.turno

            chave = f"{cor}{tipo}"

            sprite = self.cache_sprites[chave]

            sprite_rect = sprite.get_rect(center=rect.center)

            self.tela.blit(sprite, sprite_rect)

            self.menu_promocao_rects[tipo] = rect


    def obter_escolha_promocao(self, pos_mouse: tuple[int, int]) -> str | None:
        """
        Retorna o tipo da peça escolhida no menu de promoção.
        """
        for tipo, rect in self.menu_promocao_rects.items():
            if rect.collidepoint(pos_mouse):
                return tipo

        return None


    def _desenhar_xeque(self) -> None:
        """
        Destaca a casa onde o rei estiver em xeque.
        """
        if self.engine.verificar_xeque(Cor.BRANCO):
            self._desenhar_xeque_branco(surface=self.tela)

        if self.engine.verificar_xeque(Cor.PRETO):
            self._desenhar_xeque_preto(surface=self.tela)


    def _desenhar_xeque_preto(self, surface: Surface) -> None:
        """
        Destaca a casa onde o rei preto estiver em xeque.

        Args:
            surface (Surface): Surface da tela.
        """
        pos = self.engine.achar_lc_rei(Cor.PRETO)
        if pos:
            l_vis, c_vis = self.transformar_coords(pos[0], pos[1])
            x = c_vis * TAM_CASA + TAB_POS[0]
            y = l_vis * TAM_CASA + TAB_POS[1]

            surf_xeque = pg.Surface((TAM_CASA, TAM_CASA))
            surf_xeque.fill(COR_XEQUE)
            surf_xeque.set_alpha(TRANSPARENCIA_XEQUE) 
            surface.blit(surf_xeque, (x, y))


    def _desenhar_xeque_branco(self, surface: Surface) -> None:
        """
        Destaca a casa onde o rei branco estiver em xeque.

        Args:
            surface (Surface): Surface da tela.
        """
        pos = self.engine.achar_lc_rei(Cor.BRANCO)
        if pos:
            l_vis, c_vis = self.transformar_coords(pos[0], pos[1])
            x = c_vis * TAM_CASA + TAB_POS[0]
            y = l_vis * TAM_CASA + TAB_POS[1]

            surf_xeque = pg.Surface((TAM_CASA, TAM_CASA))
            surf_xeque.fill(COR_XEQUE)
            surf_xeque.set_alpha(TRANSPARENCIA_XEQUE)
            surface.blit(surf_xeque, (x, y))


    def _desenhar_tabuleiro(
        self,
        surface: Surface,
        dest: tuple[int, int]
    ) -> None:
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
                if (
                    peca is not None and
                    peca != self.peca_arrastada and
                    hasattr(peca, 'rect')
                ):
                    self.tela.blit(
                        source=peca.sprite,
                        dest=peca.rect.move(TAB_POS)
                    )

        if (
            self.peca_arrastada and
            hasattr(self.peca_arrastada, 'rect')
        ):
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
        if self.engine.turno == Cor.BRANCO:
            turno = 'Brancas'
        else:
            turno = 'Pretas'

        surface.blit(
            source=self.fonte.render(
                text=f'Vez das\n{turno}',
                antialias=True,
                color=(130, 130, 130)
                ),
            dest=(
                    TAM_TABULEIRO[0] + 10,
                    TAMANHO_TELA[1] // 2 - 20
                )
            )


    def _criar_surface_tabuleiro_estatica(self) -> None:
        """
        Cria a superfície do tabuleiro base uma única vez.
        """
        for l in range(8):
            for c in range(8):
                if (l + c) % 2 == 0:
                    cor = COR_CASAS_PARES
                else:
                    cor = COR_CASAS_IMPARES

                pg.draw.rect(
                    surface=self.surf_base_tabuleiro,
                    color=cor,
                    rect=(
                        c * TAM_CASA,
                        l * TAM_CASA,
                        TAM_CASA,
                        TAM_CASA
                    )
                )


    def _desenhar_movimentos_possiveis(self, surface: Surface) -> None:
        """
        Desenha indicadores visuais para movimentos normais e capturas.
        """
        for (l, c), tipo in self.engine.movimentos_possiveis:
            l_vis, c_vis = self.transformar_coords(l, c)
            x, y = (
                c_vis * TAM_CASA + TAB_POS[0],
                l_vis * TAM_CASA + TAB_POS[1]
            )

            if tipo == TipoMov.CAPTURA:
                pg.draw.rect(
                    surface=surface,
                    color=COR_CASAS_CAPTURA,
                    rect=(
                        x,
                        y,
                        TAM_CASA,
                        TAM_CASA
                    ),
                    width=3
                )
            elif tipo == TipoMov.NORMAL:
                pg.draw.circle(
                    surface=surface,
                    color=COR_CASAS_MOV,
                    center=(
                        x + TAM_CASA // 2,
                        y + TAM_CASA // 2
                    ),
                    radius=RAIO_CIRCULO
                )
            elif tipo in (TipoMov.ROQUE_CURTO, TipoMov.ROQUE_LONGO):
                pg.draw.circle(
                    surface=surface,
                    color=COR_CASAS_ROQUE,
                    center=(
                        x + TAM_CASA // 2,
                        y + TAM_CASA // 2
                    ),
                    radius=RAIO_CIRCULO
                )


    def mostrar_fps(self, fps: float) -> None:
        """
        Renderiza o texto de FPS no canto da tela.

        Args:
            fps (float): Valor do FPS atual.
        """
        self.tela.blit(
            source=self.fonte.render(
                text=f"FPS: {int(fps)}",
                antialias=True,
                color=COR_TEXTO
            ),
            dest=(TAM_TABULEIRO[0] + 10, 10)
        )


    def mostrar_tabuleiro_no_terminal(self) -> None:
        """
        Exibe uma representação visual do tabuleiro no terminal.
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
                    if (l + c) % 2 == 0:
                        char = "."
                    else:
                        char = " "
                else:
                    if peca.cor == Cor.BRANCO:
                        char = peca.tipo.value.upper()
                    else:
                        char = peca.tipo.value.lower()
                
                linha_str += f" {char} |"
            
            print(linha_str)
            print("  " + "—" * 33)

        if self.orientacao_tabuleiro == Cor.BRANCO:
            orientacao_txt = "BRANCAS"
        else:
            orientacao_txt = "PRETAS"
        if self.engine.turno == Cor.BRANCO:
            turno_txt = "BRANCAS"
        else:
            turno_txt = "PRETAS"

        print(f"Visão: {orientacao_txt}")
        print(f"Turno atual: {turno_txt}\n")
