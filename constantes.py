from dataclasses import dataclass

FRAMERATE: int                          = 75
BRANCO: tuple[int, int, int]            = (255, 255, 255)
PRETO: tuple[int, int, int]             = (0, 0, 0)
COR_CASAS_IMPARES: tuple[int, int, int] = (181, 136, 99)
COR_CASAS_PARES: tuple[int, int, int]   = (240, 217, 181)
COR_CASAS_MOV: tuple[int, int, int]     = (0, 0, 128)
COR_CASAS_CAPTURA: tuple[int, int, int] = (200, 0, 0)
COR_TEXTO: tuple[int, int, int]         = (75, 0, 130)
COR_FUNDO: tuple[int, int, int]         = (230, 230, 230)
TAM_CASA: int                           = 50
RAIO_CIRCULO: int                       = int(0.05 * TAM_CASA)
TAMANHO_TELA: tuple[int, int]           = (TAM_CASA * 8 + 100, TAM_CASA * 8 + 1)
TAMANHO_PECA: int                       = TAM_CASA
TAM_TABULEIRO: tuple[int, int]          = (TAM_CASA * 8, TAM_CASA * 8)
TAB_POS: tuple[int, int]                = (0, 0)

FEN_INICIAL: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


@dataclass
class Movimento:
    origem:     tuple[int, int]
    destino:    tuple[int, int]
