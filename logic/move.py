from dataclasses import dataclass
from enum import Enum, auto
from pecas.peca import Peca


@dataclass
class EstadoHistorico:
    """
    Guarda o estado necessário para reverter um lance.
    """
    movimento: Movimento
    peca_movida: Peca
    peca_capturada: Peca | None
    pos_peca_capturada: tuple[int, int] | None
    roque_curto_branco: bool
    roque_longo_branco: bool
    roque_curto_preto: bool
    roque_longo_preto: bool
    en_passant: list | None
    posicao_peao_en_passant: list[tuple[int, int]]
    posicao_alvo_en_passant: tuple[int, int] | None
    halfmove_clock: int
    ultimo_mov: Movimento | None
    foi_promocao: bool


@dataclass
class Movimento:
    """
    Representa um movimento de peça.
    
    Attributes:
        origem (tuple[int, int]): Casa inicial.
        destino (tuple[int, int]): Casa final.

        Formato: (linha, coluna), (x, y)
    """
    origem:     tuple[int, int]
    destino:    tuple[int, int]


class TipoMov(Enum):
    NORMAL          = auto()
    CAPTURA         = auto()
    ROQUE_CURTO     = auto()
    ROQUE_LONGO     = auto()
    EN_PASSANT      = auto()
