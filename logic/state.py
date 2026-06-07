from dataclasses import dataclass, field
from pecas.peca import Cor
from .board import Board

@dataclass
class GameState:
    board: Board = field(default_factory=Board)
    
    turno: Cor = Cor.BRANCO

    posicoes_jogadas: list[str] = field(default_factory=list)

    # Direitos de roque
    roque_curto_branco: bool = True
    roque_longo_branco: bool = True
    roque_curto_preto: bool = True
    roque_longo_preto: bool = True
    
    # En Passant
    en_passant: list = None 
    posicao_peao_en_passant: list = field(default_factory=list)
    posicao_alvo_en_passant: tuple = None
    
    # Clocks
    halfmove_clock: int = 0
    fullmove_number: int = 1
    
    # Status
    vitoria_negras: bool = False
    vitoria_brancas: bool = False
    empate: bool = False
