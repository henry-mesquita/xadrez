from pecas.peca import Cor
from pecas.peao import Peao
from pecas.rei import Rei
from .state import GameState
from .move import TipoMov
from .board import Board
from .factory import criar_peca


def carregar_posicao_fen(
    state: GameState,
    fen: str,
    board: Board
) -> None:
    """
    Carrega uma posição de um FEN.

    Args:
        state (GameState): Estado do controller.
        fen (str): FEN da posição.
    """
    partes = fen.strip().split()
    tabuleiro_str, turno, roques, ep_square = partes[:4]
    
    if len(partes) > 4:
        state.halfmove_clock = int(partes[4])
    else:
        state.halfmove_clock = 0
        
    if len(partes) > 5:
        state.fullmove_number = int(partes[5])
    else:
        state.fullmove_number = 1

    state.board.matriz.fill(None)

    ranks = tabuleiro_str.split('/')
    for i, rank in enumerate(ranks):
        j = 0
        for ch in rank:
            if ch.isdigit():
                j += int(ch)
            else:
                cor_peca = Cor.BRANCO if ch.isupper() else Cor.PRETO

                peca_nova = criar_peca(tipo=ch.lower(), cor=cor_peca, pos=[i, j])
                board.matriz[i, j] = peca_nova

                if isinstance(peca_nova, Rei):
                    board.reis[cor_peca] = peca_nova

                board.matriz[i, j] = peca_nova
                j += 1

    state.turno = turno
    state.roque_curto_branco = 'K' in roques
    state.roque_longo_branco = 'Q' in roques
    state.roque_curto_preto  = 'k' in roques
    state.roque_longo_preto  = 'q' in roques

    state.en_passant = None
    state.posicao_alvo_en_passant = None
    state.posicao_peao_en_passant = []

    if ep_square != '-':
        col = ord(ep_square[0]) - ord('a')
        row = 8 - int(ep_square[1])
        state.en_passant = [(row, col), TipoMov.CAPTURA]
        
        if turno == Cor.BRANCO:
            state.posicao_alvo_en_passant = (row + 1, col)
        else:
            state.posicao_alvo_en_passant = (row - 1, col)
        
        alvo_p = state.posicao_alvo_en_passant
        for dc in (-1, 1):
            c_viz = alvo_p[1] + dc
            if Board.lc_valido(alvo_p[0], c_viz):
                v = state.board.matriz[alvo_p[0], c_viz]
                if isinstance(v, Peao):
                    if v.cor == turno:
                        state.posicao_peao_en_passant.append((alvo_p[0], c_viz))


def exportar_posicao_fen(state: GameState) -> str:
    """
    Exporta a posição atual no padrão FEN.

    Returns:
        str: String FEN da posição atual.
    """

    ranks = []

    for linha in state.board.matriz:
        rank = ""
        vazias = 0
        for peca in linha:
            if peca is None:
                vazias += 1
                continue
            if vazias > 0:
                rank += str(vazias)
                vazias = 0

            simbolo = peca.tipo.value
            if peca.cor == Cor.BRANCO:
                simbolo = simbolo.upper()

            rank += simbolo
        if vazias > 0:
            rank += str(vazias)

        ranks.append(rank)

    tabuleiro_str = "/".join(ranks)
    turno = state.turno

    roques = ""

    if state.roque_curto_branco:
        roques += "K"
    if state.roque_longo_branco:
        roques += "Q"
    if state.roque_curto_preto:
        roques += "k"
    if state.roque_longo_preto:
        roques += "q"
    if roques == "":
        roques = "-"
    
    ep_square = "-"

    if state.en_passant is not None:
        linha, coluna = state.en_passant[0]

        arquivo = chr(ord("a") + coluna)
        rank = str(8 - linha)

        ep_square = f"{arquivo}{rank}"

    halfmove_clock = state.halfmove_clock
    fullmove_number = state.fullmove_number

    return (
        f"{tabuleiro_str} "
        f"{turno} "
        f"{roques} "
        f"{ep_square} "
        f"{halfmove_clock} "
        f"{fullmove_number}"
    )
