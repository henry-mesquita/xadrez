FRAMERATE: int                          = 60
BRANCO: tuple[int, int, int]            = (255, 255, 255)
PRETO: tuple[int, int, int]             = (0, 0, 0)
COR_CASAS_IMPARES: tuple[int, int, int] = (181,136,99)
COR_CASAS_PARES: tuple[int, int, int]   = (240,217,181)
COR_CASAS_MOV: tuple[int, int, int]     = (255, 0, 0)
TAM_CASA: int                           = 75
TAMANHO_TELA: tuple                     = (TAM_CASA*8, TAM_CASA*8)
TAMANHO_PECA: int                       = TAM_CASA
TAM_TABULEIRO: tuple[int, int]          = (TAM_CASA * 8, TAM_CASA * 8)
TAB_POS: tuple[int, int]                = (0, 0)

FEN_INICIAL: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
