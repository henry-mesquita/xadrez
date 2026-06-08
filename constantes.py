DEBUG: bool                             = False
FRAMERATE: int                          = 75

BRANCO: tuple[int, int, int]            = (255, 255, 255)
PRETO: tuple[int, int, int]             = (0, 0, 0)

# COR_CASAS_IMPARES: tuple[int, int, int] = (181, 136, 99)
# COR_CASAS_PARES: tuple[int, int, int]   = (240, 217, 181)

COR_CASAS_IMPARES: tuple[int, int, int] = (125, 74, 141)
COR_CASAS_PARES: tuple[int, int, int]   = (159, 144, 176)
COR_CASAS_MOV: tuple[int, int, int]     = (0, 0, 128)
COR_CASAS_CAPTURA: tuple[int, int, int] = (200, 0, 0)
COR_CASAS_ROQUE: tuple[int, int, int]   = (0, 190, 0)
COR_TEXTO: tuple[int, int, int]         = (75, 0, 130)
COR_FUNDO: tuple[int, int, int]         = (230, 230, 230)
COR_XEQUE: tuple[int, int, int]         = (190, 0, 0)
TRANSPARENCIA_XEQUE: int                = 130

COR_ULTIMO_MOV: tuple[int, int, int]    = (222, 108, 242)
TRANSPARENCIA_DESTAQUE: int             = 150

TAM_CASA: int                           = 70
RAIO_CIRCULO: int                       = int(0.05 * TAM_CASA)

if DEBUG:
    TAMANHO_TELA: tuple[int, int]       = (TAM_CASA * 8 + 100, TAM_CASA * 8 + 1)
else:
    TAMANHO_TELA: tuple[int, int]       = (TAM_CASA * 8, TAM_CASA * 8)

TAMANHO_PECA: int                       = TAM_CASA
TAM_TABULEIRO: tuple[int, int]          = (TAM_CASA * 8, TAM_CASA * 8)
TAB_POS: tuple[int, int]                = (0, 0)

DESFAZER_MOVIMENTO: bool                = True

FEN_INICIAL: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

ESTILO_PECAS = "mpchess"
