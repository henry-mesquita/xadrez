from dataclasses import dataclass
from enum import Enum, auto
from pecas.peca import Peca
from typing import TypedDict, Literal
from pecas.peca import Cor


def lc_valido(l: int, c: int) -> bool:
    return 0 <= l < 8 and 0 <= c < 8


class TipoPeca(Enum):
    PEAO    = 'p'
    TORRE   = 'r'
    CAVALO  = 'n'
    BISPO   = 'b'
    DAMA    = 'q'
    REI     = 'k'


class TipoMov(Enum):
    NORMAL          = auto()
    CAPTURA         = auto()
    ROQUE_CURTO     = auto()
    ROQUE_LONGO     = auto()
    EN_PASSANT      = auto()


# linha e coluna
type Pos                = tuple[int, int]
# você pode ir para a casa X e isso é um movimento Y
type Candidato          = tuple[Pos, TipoMov]
# conjunto completo de opções que uma peça tem num turno
type JogadasPossiveis   = list[Candidato]
# informação que guarda en passant
type InfoEnPassant      = tuple
# tipagem do ROQUES
type LadoRoque = Literal["curto", "longo"]

class DadosRoque(TypedDict):
    direito:        str
    origem_rei:     Pos
    destino_rei:    Pos
    origem_torre:   Pos
    destino_torre:  Pos
    casas_seguras:  list[Pos]

# o dicionário completo é uma tradução de (Cor, Lado) para DadosRoque
type MapeamentoRoques = dict[tuple[Cor, LadoRoque], DadosRoque]


@dataclass
class Movimento:
    """
    Representa um movimento de peça.
    
    Attributes:
        origem (tuple[int, int]): Casa inicial.
        destino (tuple[int, int]): Casa final.

        Formato: (linha, coluna), (x, y)
    """
    origem:     Pos
    destino:    Pos



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
